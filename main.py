import pygame
from pygame import mixer
from fighter import Fighter

mixer.init()
pygame.init()

#create game window
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("AI_Project - Multi-Character")

#set framerate
clock = pygame.time.Clock()
FPS = 60

#define colours
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
GREY = (128, 128, 128)
LIGHT_BLUE = (173, 216, 230) # For cooldown text

#define game variables
intro_count = 3
last_count_update = pygame.time.get_ticks()
score = [0, 0]#player scores. [P1, P2]
round_over = False
ROUND_OVER_COOLDOWN = 3000 # Increased for better visibility of victory/defeat

#define fighter variables
WARRIOR_SIZE = 162
WARRIOR_SCALE = 4
WARRIOR_OFFSET = [72, 56]
WARRIOR_DATA = [WARRIOR_SIZE, WARRIOR_SCALE, WARRIOR_OFFSET]
WIZARD_SIZE = 250
WIZARD_SCALE = 3
WIZARD_OFFSET = [112, 107]
WIZARD_DATA = [WIZARD_SIZE, WIZARD_SCALE, WIZARD_OFFSET]

#load music and sounds
# Ensure your asset paths are correct
try:
    pygame.mixer.music.load("assets/audio/music.mp3")
    pygame.mixer.music.set_volume(0.5)
    pygame.mixer.music.play(-1, 0.0, 5000)
    sword_fx = pygame.mixer.Sound("assets/audio/sword.wav")
    sword_fx.set_volume(0.5)
    magic_fx = pygame.mixer.Sound("assets/audio/magic.wav")
    magic_fx.set_volume(0.75)
except pygame.error as e:
    print(f"Warning: Could not load audio assets. {e}")
    # Create dummy sound objects if loading fails, so the game doesn't crash
    class DummySound:
        def play(self): pass
        def set_volume(self, vol): pass
    sword_fx = DummySound()
    magic_fx = DummySound()


#load background image
try:
    bg_image = pygame.image.load("assets/images/background/background.jpg").convert_alpha()
except pygame.error as e:
    print(f"Error loading background image: {e}")
    bg_image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)) # Placeholder
    bg_image.fill(BLACK)

#load spritesheets
try:
    warrior_sheet = pygame.image.load("assets/images/warrior/Sprites/warrior.png").convert_alpha()
    wizard_sheet = pygame.image.load("assets/images/wizard/Sprites/wizard.png").convert_alpha()
except pygame.error as e:
    print(f"Error loading spritesheets: {e}")
    # Create placeholder surfaces if loading fails
    warrior_sheet = pygame.Surface((WARRIOR_SIZE, WARRIOR_SIZE), pygame.SRCALPHA)
    wizard_sheet = pygame.Surface((WIZARD_SIZE, WIZARD_SIZE), pygame.SRCALPHA)


#load vicory image
try:
    victory_img = pygame.image.load("assets/images/icons/victory.png").convert_alpha()
except pygame.error as e:
    print(f"Error loading victory image: {e}")
    victory_img = pygame.Surface((100, 50), pygame.SRCALPHA) # Placeholder


#define number of steps in each animation
WARRIOR_ANIMATION_STEPS = [10, 8, 1, 7, 7, 3, 7]
WIZARD_ANIMATION_STEPS = [8, 8, 1, 8, 8, 3, 7]

#define font
try:
    count_font = pygame.font.Font("assets/fonts/turok.ttf", 80)
    score_font = pygame.font.Font("assets/fonts/turok.ttf", 30)
    info_font = pygame.font.Font("assets/fonts/turok.ttf", 20)
except pygame.error as e:
    print(f"Warning: Could not load custom font. Using default font. {e}")
    count_font = pygame.font.SysFont(None, 80)
    score_font = pygame.font.SysFont(None, 30)
    info_font = pygame.font.SysFont(None, 20)


# --- Multi-Character Setup ---
player1_fighters_defs = [
    {"name": "Warrior", "data": WARRIOR_DATA, "sheet": warrior_sheet, "steps": WARRIOR_ANIMATION_STEPS, "sound": sword_fx, "initial_x": 200, "initial_flip": False},
    {"name": "Wizard", "data": WIZARD_DATA, "sheet": wizard_sheet, "steps": WIZARD_ANIMATION_STEPS, "sound": magic_fx, "initial_x": 200, "initial_flip": False}
]
player2_fighters_defs = [
    {"name": "Wizard", "data": WIZARD_DATA, "sheet": wizard_sheet, "steps": WIZARD_ANIMATION_STEPS, "sound": magic_fx, "initial_x": 700, "initial_flip": True},
    {"name": "Warrior", "data": WARRIOR_DATA, "sheet": warrior_sheet, "steps": WARRIOR_ANIMATION_STEPS, "sound": sword_fx, "initial_x": 700, "initial_flip": True}
]

player1_fighters = []
player2_fighters = []
player1_current_fighter_index = 0
player2_current_fighter_index = 0
p1_fighter = None # Active fighter for player 1
p2_fighter = None # Active fighter for player 2

# Switch mechanics
P1_SWITCH_KEY = pygame.K_q
P2_SWITCH_KEY = pygame.K_KP_0 # Numpad 0
SWITCH_COOLDOWN_TIME = 3000 # milliseconds
player1_last_switch_time = 0
player2_last_switch_time = 0

def initialize_fighters():
    global player1_fighters, player2_fighters, p1_fighter, p2_fighter
    global player1_current_fighter_index, player2_current_fighter_index
    global player1_last_switch_time, player2_last_switch_time

    player1_fighters.clear()
    player2_fighters.clear()

    for i, char_def in enumerate(player1_fighters_defs):
        # Ensure different initial x for benched character to avoid overlap if drawn before first switch
        initial_x_pos = char_def["initial_x"] if i == 0 else char_def["initial_x"] - 50 
        fighter = Fighter(1, initial_x_pos, 310, char_def["initial_flip"], char_def["data"], char_def["sheet"], char_def["steps"], char_def["sound"])
        player1_fighters.append(fighter)
    
    for i, char_def in enumerate(player2_fighters_defs):
        initial_x_pos = char_def["initial_x"] if i == 0 else char_def["initial_x"] + 50
        fighter = Fighter(2, initial_x_pos, 310, char_def["initial_flip"], char_def["data"], char_def["sheet"], char_def["steps"], char_def["sound"])
        player2_fighters.append(fighter)

    player1_current_fighter_index = 0
    player2_current_fighter_index = 0
    p1_fighter = player1_fighters[player1_current_fighter_index]
    p2_fighter = player2_fighters[player2_current_fighter_index]
    
    # Ensure fighters start fresh
    for f_idx, f_list in enumerate([player1_fighters, player2_fighters]):
        for char_idx, f in enumerate(f_list):
            f.health = 100
            f.alive = True
            f.rect.y = 310 # Reset y position
            if f.player == 1:
                f.rect.x = player1_fighters_defs[char_idx]["initial_x"]
                f.flip = player1_fighters_defs[char_idx]["initial_flip"]
            else: # player == 2
                f.rect.x = player2_fighters_defs[char_idx]["initial_x"]
                f.flip = player2_fighters_defs[char_idx]["initial_flip"]
            f.update_action(0) # Idle

    p1_fighter.rect.x = player1_fighters_defs[0]["initial_x"] # Active fighter at correct start
    p2_fighter.rect.x = player2_fighters_defs[0]["initial_x"] # Active fighter at correct start


    player1_last_switch_time = -SWITCH_COOLDOWN_TIME # Allow immediate switch at round start if needed
    player2_last_switch_time = -SWITCH_COOLDOWN_TIME


def switch_character_action(player_num, new_fighter_index):
    global p1_fighter, player1_current_fighter_index, player1_last_switch_time
    global p2_fighter, player2_current_fighter_index, player2_last_switch_time
    
    current_time = pygame.time.get_ticks()

    if player_num == 1:
        if player1_fighters[new_fighter_index].alive: # Check if the target character is alive
            old_fighter_state = {
                "rect_center": p1_fighter.rect.center, # Use center for smoother transition
                "vel_y": p1_fighter.vel_y,
                "jump": p1_fighter.jump,
                # "flip": p1_fighter.flip # Flip is determined by target, so don't force
            }
            player1_current_fighter_index = new_fighter_index
            p1_fighter = player1_fighters[player1_current_fighter_index]
            
            # Restore state to new fighter
            p1_fighter.rect.center = old_fighter_state["rect_center"]
            p1_fighter.vel_y = old_fighter_state["vel_y"]
            p1_fighter.jump = old_fighter_state["jump"]
            
            p1_fighter.update_action(0) # Reset to idle
            p1_fighter.attacking = False
            p1_fighter.hit = False
            player1_last_switch_time = current_time
            print(f"Player 1 switched to {player1_fighters_defs[new_fighter_index]['name']}")
            return True
    elif player_num == 2:
        if player2_fighters[new_fighter_index].alive: # Check if the target character is alive
            old_fighter_state = {
                "rect_center": p2_fighter.rect.center,
                "vel_y": p2_fighter.vel_y,
                "jump": p2_fighter.jump,
                # "flip": p2_fighter.flip
            }
            player2_current_fighter_index = new_fighter_index
            p2_fighter = player2_fighters[player2_current_fighter_index]

            p2_fighter.rect.center = old_fighter_state["rect_center"]
            p2_fighter.vel_y = old_fighter_state["vel_y"]
            p2_fighter.jump = old_fighter_state["jump"]

            p2_fighter.update_action(0)
            p2_fighter.attacking = False
            p2_fighter.hit = False
            player2_last_switch_time = current_time
            print(f"Player 2 switched to {player2_fighters_defs[new_fighter_index]['name']}")
            return True
    return False

#function for drawing text
def draw_text(text, font, text_col, x, y):
  img = font.render(text, True, text_col)
  screen.blit(img, (x, y))

#function for drawing background
def draw_bg():
  scaled_bg = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
  screen.blit(scaled_bg, (0, 0))

#function for drawing fighter health bars
def draw_health_bar(health, x, y, width=400, height=30, is_active=True):
    ratio = health / 100
    
    outline_color = WHITE if is_active else GREY
    bar_color = RED
    health_color = YELLOW if is_active else GREEN # Different color for benched health

    pygame.draw.rect(screen, outline_color, (x - 2, y - 2, width + 4, height + 4))
    pygame.draw.rect(screen, bar_color, (x, y, width, height))
    pygame.draw.rect(screen, health_color, (x, y, width * ratio, height))

# Function to draw switch cooldown status
def draw_switch_cooldown_status(player_num, last_switch_time, current_time, x, y):
    cooldown_remaining_ms = SWITCH_COOLDOWN_TIME - (current_time - last_switch_time)
    
    can_switch_to_benched = False
    benched_fighter_name = ""

    if player_num == 1:
        benched_idx = (player1_current_fighter_index + 1) % len(player1_fighters)
        if player1_fighters[benched_idx].alive:
            can_switch_to_benched = True
        benched_fighter_name = player1_fighters_defs[benched_idx]['name']
    elif player_num == 2:
        benched_idx = (player2_current_fighter_index + 1) % len(player2_fighters)
        if player2_fighters[benched_idx].alive:
            can_switch_to_benched = True
        benched_fighter_name = player2_fighters_defs[benched_idx]['name']

    if cooldown_remaining_ms > 0:
        text = f"Switch CD: {cooldown_remaining_ms / 1000:.1f}s"
        color = YELLOW 
    else:
        if can_switch_to_benched:
            text = "Switch Ready!"
            color = GREEN
        else:
            text = f"{benched_fighter_name} KO" 
            color = GREY
            
    draw_text(text, info_font, color, x, y)

# Initialize fighters at the start of the game
initialize_fighters()

#game loop
run = True
while run:

  clock.tick(FPS)
  current_time_ingame = pygame.time.get_ticks() # Get current time once per frame

  #draw background
  draw_bg()

  #show player stats (active fighters)
  draw_text(f"P1: {player1_fighters_defs[player1_current_fighter_index]['name']}", score_font, WHITE, 20, 10)
  draw_health_bar(p1_fighter.health, 20, 40)
  draw_text(f"P2: {player2_fighters_defs[player2_current_fighter_index]['name']}", score_font, WHITE, 580, 10)
  draw_health_bar(p2_fighter.health, 580, 40)
  
  draw_text("P1 Score: " + str(score[0]), score_font, RED, 20, 160) # y-pos adjusted
  draw_text("P2 Score: " + str(score[1]), score_font, RED, 580, 160) # y-pos adjusted

  # Show benched character health
  p1_benched_index = (player1_current_fighter_index + 1) % len(player1_fighters)
  p1_benched_fighter = player1_fighters[p1_benched_index]
  draw_text(f"Bench: {player1_fighters_defs[p1_benched_index]['name']}", info_font, WHITE, 20, 80)
  if p1_benched_fighter.alive:
      draw_health_bar(p1_benched_fighter.health, 20, 105, width=150, height=15, is_active=False)
  else:
      draw_text("KO", info_font, RED, 180, 105) # Adjusted x for "KO"

  p2_benched_index = (player2_current_fighter_index + 1) % len(player2_fighters)
  p2_benched_fighter = player2_fighters[p2_benched_index]
  draw_text(f"Bench: {player2_fighters_defs[p2_benched_index]['name']}", info_font, WHITE, 580, 80)
  if p2_benched_fighter.alive:
      draw_health_bar(p2_benched_fighter.health, 580, 105, width=150, height=15, is_active=False)
  else:
      draw_text("KO", info_font, RED, 740, 105) # Adjusted x for "KO"

  # Display switch cooldown status (only when game is active)
  if intro_count <= 0:
    draw_switch_cooldown_status(1, player1_last_switch_time, current_time_ingame, 20, 130)
    draw_switch_cooldown_status(2, player2_last_switch_time, current_time_ingame, 580, 130)

  #update countdown
  if intro_count <= 0:
    # current_time_ingame is already defined above
    keys = pygame.key.get_pressed()

    # Player 1 manual switch
    if keys[P1_SWITCH_KEY] and current_time_ingame - player1_last_switch_time > SWITCH_COOLDOWN_TIME:
        next_idx = (player1_current_fighter_index + 1) % len(player1_fighters)
        if player1_fighters[next_idx].alive:
            switch_character_action(1, next_idx)
        else:
            print("P1: Cannot switch to KO'd character.")
            # Optionally, still apply cooldown to prevent spamming attempts if desired,
            # but current logic correctly prevents switch if benched is KO'd.
            # player1_last_switch_time = current_time_ingame 

    # Player 2 manual switch
    if keys[P2_SWITCH_KEY] and current_time_ingame - player2_last_switch_time > SWITCH_COOLDOWN_TIME:
        next_idx = (player2_current_fighter_index + 1) % len(player2_fighters)
        if player2_fighters[next_idx].alive:
            switch_character_action(2, next_idx)
        else:
            print("P2: Cannot switch to KO'd character.")
            # player2_last_switch_time = current_time_ingame


    #move fighters
    p1_fighter.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, p2_fighter, round_over)
    p2_fighter.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, p1_fighter, round_over)
  else:
    #display count timer
    draw_text(str(intro_count), count_font, RED, SCREEN_WIDTH / 2 - count_font.size(str(intro_count))[0] / 2, SCREEN_HEIGHT / 3) # Centered timer
    #update count timer
    if (current_time_ingame - last_count_update) >= 1000:
      intro_count -= 1
      last_count_update = current_time_ingame

  #update fighters
  p1_fighter.update()
  p2_fighter.update()

  #draw fighters
  p1_fighter.draw(screen)
  p2_fighter.draw(screen)

  #check for player defeat
  if round_over == False:
    p1_can_continue = any(f.alive for f in player1_fighters)
    p2_can_continue = any(f.alive for f in player2_fighters)

    # Auto-switch if active fighter is KO'd and another is available
    if not p1_fighter.alive and p1_can_continue:
        print(f"P1: {player1_fighters_defs[player1_current_fighter_index]['name']} KO'd. Auto-switching...")
        next_idx = (player1_current_fighter_index + 1) % len(player1_fighters)
        # Ensure the next character is actually alive before switching (should be if p1_can_continue)
        if player1_fighters[next_idx].alive : 
             switch_character_action(1, next_idx)
        
    if not p2_fighter.alive and p2_can_continue:
        print(f"P2: {player2_fighters_defs[player2_current_fighter_index]['name']} KO'd. Auto-switching...")
        next_idx = (player2_current_fighter_index + 1) % len(player2_fighters)
        if player2_fighters[next_idx].alive :
            switch_character_action(2, next_idx)
        
    # Re-check overall status after potential auto-switches
    p1_lost = not any(f.alive for f in player1_fighters)
    p2_lost = not any(f.alive for f in player2_fighters)

    if p1_lost:
      score[1] += 1
      round_over = True
      round_over_time = current_time_ingame # Use current_time_ingame
      print("Player 1 has no fighters left. Player 2 wins round.")
    elif p2_lost:
      score[0] += 1
      round_over = True
      round_over_time = current_time_ingame # Use current_time_ingame
      print("Player 2 has no fighters left. Player 1 wins round.")

  else: # round_over is True
    #display victory image
    screen.blit(victory_img, (SCREEN_WIDTH / 2 - victory_img.get_width() / 2, SCREEN_HEIGHT / 3 - victory_img.get_height()/2))
    if current_time_ingame - round_over_time > ROUND_OVER_COOLDOWN:
      round_over = False
      intro_count = 3
      initialize_fighters() 

  #event handler
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      run = False


  #update display
  pygame.display.update()

#exit pygame
pygame.quit()
