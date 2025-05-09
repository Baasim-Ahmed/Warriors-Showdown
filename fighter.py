import pygame

class Fighter():
  def __init__(self, player, x, y, flip, data, sprite_sheet, animation_steps, sound):
    self.player = player
    self.size = data[0]
    self.image_scale = data[1]
    self.offset = data[2]
    self.flip = flip
    self.animation_list = self.load_images(sprite_sheet, animation_steps)
    self.action = 0#0:idle #1:run #2:jump #3:attack1 #4: attack2 #5:hit #6:death
    self.frame_index = 0
    self.image = self.animation_list[self.action][self.frame_index]
    self.update_time = pygame.time.get_ticks()
    # Adjust the collision rectangle size to be more representative of the character's core
    # The current 80x180 might be too large or misaligned depending on the sprite
    # A common approach is to define a smaller rect relative to the sprite offset/size
    # For simplicity, keeping the current size but be aware this might need tuning
    self.rect = pygame.Rect((x, y, 80, 180))

    self.vel_y = 0
    self.running = False # This will now be set by the move method based on input
    self.jump = False # This will now be set by the move method based on input
    self.attacking = False
    self.attack_type = 0 # This will now be set by the attack method based on input
    self.attack_cooldown = 0
    self.attack_sound = sound
    self.hit = False
    self.health = 100
    self.alive = True
    self.hit_timer = 0 # Timer to control how long the hit animation plays
    self.HIT_DURATION = 500 # Milliseconds the hit animation lasts

    # Add a small rectangle for attack collision detection, relative to the fighter
    # This will be calculated dynamically during an attack
    self.attack_rect = pygame.Rect(0, 0, 0, 0)


  def load_images(self, sprite_sheet, animation_steps):
    #extract images from spritesheet
    animation_list = []
    for y, animation in enumerate(animation_steps):
      temp_img_list = []
      for x in range(animation):
        # Calculate the correct sub-surface based on the frame's position
        y_pos = y * self.size
        x_pos = x * self.size
        temp_img = sprite_sheet.subsurface(x_pos, y_pos, self.size, self.size)
        temp_img_list.append(pygame.transform.scale(temp_img, (self.size * self.image_scale, self.size * self.image_scale)))
      animation_list.append(temp_img_list)
    return animation_list


  # Modified move method to accept movement direction (dx) directly
  def move(self, screen_width, screen_height, surface, target, round_over, move_direction):
    SPEED = 10
    GRAVITY = 2
    dx = 0
    dy = 0

    # Can only perform other actions if not currently attacking and is alive and round is not over
    if self.attacking == False and self.alive == True and round_over == False:
        # Movement
        if move_direction == -1: # Move left
            dx = -SPEED
            self.running = True
        elif move_direction == 1: # Move right
            dx = SPEED
            self.running = True
        else:
            self.running = False # Not moving horizontally

        # Jump is now triggered by the main loop logic calling move with jump=True (implicitly handled by vel_y)
        # The main loop sets self.vel_y = -30 and self.jump = True when a jump action is requested
        # Gravity is applied regardless of input, handled below

    # apply gravity
    self.vel_y += GRAVITY
    dy += self.vel_y

    # ensure player stays on screen
    # Check horizontal bounds
    if self.rect.left + dx < 0:
      dx = -self.rect.left
    if self.rect.right + dx > screen_width:
      dx = screen_width - self.rect.right

    # Check vertical bounds (ground collision)
    ground_level = screen_height - 110 # Assuming 110 is the height of the ground area below fighters
    if self.rect.bottom + dy > ground_level:
      self.vel_y = 0 # Stop vertical movement
      self.jump = False # Reset jump state
      dy = ground_level - self.rect.bottom # Place fighter exactly on the ground

    # ensure players face each other
    if target.rect.centerx > self.rect.centerx:
      self.flip = False
    else:
      self.flip = True

    # apply attack cooldown
    if self.attack_cooldown > 0:
      self.attack_cooldown -= 1

    # update player position
    self.rect.x += dx
    self.rect.y += dy


  # Modified attack method to accept attack_type directly
  def attack(self, target, attack_type):
    # Only allow attack if not already attacking, alive, and cooldown is ready
    if self.attacking == False and self.alive == True and self.attack_cooldown == 0:
      self.attack_type = attack_type
      self.attacking = True
      self.attack_sound.play()
      # Define attack hit area relative to the fighter's current position and direction
      attack_width = self.rect.width * 1.5 # Example attack reach
      attack_height = self.rect.height / 2 # Example attack height
      attack_y = self.rect.centery - attack_height / 2 # Center attack vertically

      if self.flip: # Facing left
          attack_x = self.rect.left - attack_width # Attack to the left of the fighter
      else: # Facing right
          attack_x = self.rect.right # Attack to the right of the fighter

      self.attack_rect = pygame.Rect(attack_x, attack_y, attack_width, attack_height)

      # Check for collision with the target
      if self.attack_rect.colliderect(target.rect):
        # Apply damage (example damage values)
        damage = 0
        if self.attack_type == 1:
            damage = 10
        elif self.attack_type == 2:
            damage = 15 # Example for a stronger attack
        target.health -= damage
        target.hit = True # Set hit state on target
        target.hit_timer = pygame.time.get_ticks() # Start hit animation timer


  #handle animation updates
  def update(self):
    #check what action the player is performing
    # Death has highest priority
    if self.health <= 0:
      self.health = 0 # Ensure health doesn't go below 0
      self.alive = False
      self.update_action(6)#6:death
    # Hit has next priority, but only play for a short duration
    elif self.hit == True and pygame.time.get_ticks() - self.hit_timer < self.HIT_DURATION:
        self.update_action(5) # 5:hit
    # If hit duration is over, reset hit state
    elif self.hit == True and pygame.time.get_ticks() - self.hit_timer >= self.HIT_DURATION:
         self.hit = False # Reset hit state
         self.update_action(0) # Go back to idle or appropriate state
         self.attacking = False # Cancel any ongoing attack if hit
    # Attack has next priority
    elif self.attacking == True:
      if self.attack_type == 1:
        self.update_action(3)#3:attack1
      elif self.attack_type == 2:
        self.update_action(4)#4:attack2
    # Jump has next priority
    elif self.jump == True:
      self.update_action(2)#2:jump
    # Running has next priority
    elif self.running == True:
      self.update_action(1)#1:run
    # Otherwise, idle
    else:
      self.update_action(0)#0:idle

    animation_cooldown = 50
    #update image
    self.image = self.animation_list[self.action][self.frame_index]
    #check if enough time has passed since the last update
    if pygame.time.get_ticks() - self.update_time > animation_cooldown:
      self.frame_index += 1
      self.update_time = pygame.time.get_ticks()
    #check if the animation has finished
    if self.frame_index >= len(self.animation_list[self.action]):
      #if the player is dead then end the animation on the last frame
      if self.alive == False:
        self.frame_index = len(self.animation_list[self.action]) - 1
      else:
        self.frame_index = 0
        #check if an attack animation has finished
        if self.action == 3 or self.action == 4:
          self.attacking = False
          self.attack_cooldown = 20 # Start cooldown after attack animation finishes
          self.attack_type = 0 # Reset attack type

        #check if hit animation has finished (handled by hit_timer now, but keep this for completeness)
        if self.action == 5:
           # The hit state is now primarily managed by the hit_timer in the update logic
           # This block might be redundant but can stay as a fallback
           pass


  # Helper method to update the current action and reset animation frame/timer
  def update_action(self, new_action):
    #check if the new action is different to the previous one
    if new_action != self.action:
      self.action = new_action
      #update the animation settings
      self.frame_index = 0
      self.update_time = pygame.time.get_ticks()

  def draw(self, surface):
    # Flip the image if needed
    img = pygame.transform.flip(self.image, self.flip, False)
    # Position the image based on the rectangle, using the offset to align the sprite correctly
    # The offset accounts for the empty space in the sprite sheet frames
    img_pos = (self.rect.x - (self.offset[0] * self.image_scale), self.rect.y - (self.offset[1] * self.image_scale))
    surface.blit(img, img_pos)
    # Optional: Draw the collision rectangle for debugging
    # pygame.draw.rect(surface, RED, self.rect, 2)
    # Optional: Draw the attack rectangle for debugging (only when attacking)
    # if self.attacking:
    #     pygame.draw.rect(surface, GREEN, self.attack_rect, 2)