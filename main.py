import pygame
from pygame import mixer
from fighter import Fighter
import sys
import os # Import os for path joining

mixer.init()
pygame.init()

#create game window
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Warriors Showdown")

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

# Define game states
STATE_MENU = 0
STATE_SINGLE_PLAYER = 1
STATE_MULTIPLAYER = 2 # State for local multiplayer
STATE_QUIT = 3

# Initial game state
current_state = STATE_MENU
print(f"Initial state: STATE_MENU") # Debug print

#define fighter variables
WARRIOR_SIZE = 162
WARRIOR_SCALE = 4
WARRIOR_OFFSET = [72, 56]
WARRIOR_DATA = [WARRIOR_SIZE, WARRIOR_SCALE, WARRIOR_OFFSET] # Corrected scale and offset variable names
WIZARD_SIZE = 250
WIZARD_SCALE = 3
WIZARD_OFFSET = [112, 107]
WIZARD_DATA = [WIZARD_SIZE, WIZARD_SCALE, WIZARD_OFFSET]


# Helper function to get the absolute path for assets
def get_asset_path(relative_path):
    # Get the directory where the script is running
    script_dir = os.path.dirname(__file__)
    # Join the script directory with the relative path to the asset
    return os.path.join(script_dir, relative_path)

#load music and sounds
# Ensure your asset paths are correct
try:
    pygame.mixer.music.load(get_asset_path("assets/audio/music.mp3"))
    pygame.mixer.music.set_volume(0.5)
    # Stop music from playing immediately, wait for game state
    # pygame.mixer.music.play(-1, 0.0, 5000)
    sword_fx = pygame.mixer.Sound(get_asset_path("assets/audio/sword.wav"))
    sword_fx.set_volume(0.5)
    magic_fx = pygame.mixer.Sound(get_asset_path("assets/audio/magic.wav"))
    magic_fx.set_volume(0.75)
    print("Audio assets loaded successfully.") # Debug print
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
    bg_image = pygame.image.load(get_asset_path("assets/images/background/background.jpg")).convert_alpha()
    print("Background image loaded successfully.") # Debug print
except pygame.error as e:
    print(f"Error loading background image: {e}")
    bg_image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT)) # Placeholder
    bg_image.fill(BLACK)

#load spritesheets
try:
    warrior_sheet = pygame.image.load(get_asset_path("assets/images/warrior/Sprites/warrior.png")).convert_alpha()
    wizard_sheet = pygame.image.load(get_asset_path("assets/images/wizard/Sprites/wizard.png")).convert_alpha()
    print("Spritesheets loaded successfully.") # Debug print
except pygame.error as e:
    print(f"Error loading spritesheets: {e}")
    # Create placeholder surfaces if loading fails
    warrior_sheet = pygame.Surface((WARRIOR_SIZE, WARRIOR_SIZE), pygame.SRCALPHA)
    wizard_sheet = pygame.Surface((WIZARD_SIZE, WIZARD_SIZE), pygame.SRCALPHA)


#load vicory image
try:
    victory_img = pygame.image.load(get_asset_path("assets/images/icons/victory.png")).convert_alpha()
    print("Victory image loaded successfully.") # Debug print
except pygame.error as e:
    print(f"Error loading victory image: {e}")
    victory_img = pygame.Surface((100, 50), pygame.SRCALPHA) # Placeholder


#define number of steps in each animation
WARRIOR_ANIMATION_STEPS = [10, 8, 1, 7, 7, 3, 7]
WIZARD_ANIMATION_STEPS = [8, 8, 1, 8, 8, 3, 7]

#define font
try:
    # Using os.path.join for robustness
    count_font = pygame.font.Font(get_asset_path("assets/fonts/turok.ttf"), 80)
    score_font = pygame.font.Font(get_asset_path("assets/fonts/turok.ttf"), 30)
    info_font = pygame.font.Font(get_asset_path("assets/fonts/turok.ttf"), 20)
    menu_font = pygame.font.Font(get_asset_path("assets/fonts/turok.ttf"), 50) # Font for menu
    print("Custom font loaded successfully.") # Debug print
except pygame.error as e:
    print(f"Warning: Could not load custom font. Using default font. {e}")
    count_font = pygame.font.SysFont(None, 80)
    score_font = pygame.font.SysFont(None, 30)
    info_font = pygame.font.SysFont(None, 20)
    menu_font = pygame.font.SysFont(None, 50)
    print("Using default font.") # Debug print


# --- Multi-Character Setup ---
player1_fighters_defs = [
    {"name": "Warrior", "data": WARRIOR_DATA, "sheet": warrior_sheet, "steps": WARRIOR_ANIMATION_STEPS, "sound": sword_fx, "initial_x": 200, "initial_flip": False},
    {"name": "Wizard", "data": WIZARD_DATA, "sheet": wizard_sheet, "steps": WIZARD_ANIMATION_STEPS, "sound": magic_fx, "initial_x": 200, "initial_flip": False}
]
# Player 2 starts on the right, flipped
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
P2_SWITCH_KEY = pygame.K_KP_0 # Numpad 0 - Re-enabled for local multiplayer
SWITCH_COOLDOWN_TIME = 3000 # milliseconds
player1_last_switch_time = 0
player2_last_switch_time = 0

def initialize_fighters():
    global player1_fighters, player2_fighters, p1_fighter, p2_fighter
    global player1_current_fighter_index, player2_current_fighter_index
    global player1_last_switch_time, player2_last_switch_time
    global score # Reset score on game start
    global intro_count, round_over, last_count_update # Also reset these for a clean start

    score = [0, 0] # Reset score

    player1_fighters.clear()
    player2_fighters.clear()

    for i, char_def in enumerate(player1_fighters_defs):
        # Ensure different initial x for benched character to avoid overlap if drawn before first switch
        # Active fighter (index 0) at initial_x, others slightly offset
        initial_x_pos = char_def["initial_x"] if i == 0 else char_def["initial_x"] - 50
        fighter = Fighter(1, initial_x_pos, 310, char_def["initial_flip"], char_def["data"], char_def["sheet"], char_def["steps"], char_def["sound"])
        player1_fighters.append(fighter)

    for i, char_def in enumerate(player2_fighters_defs):
        # Active fighter (index 0) at initial_x, others slightly offset
        initial_x_pos = char_def["initial_x"] if i == 0 else char_def["initial_x"] + 50
        fighter = Fighter(2, initial_x_pos, 310, char_def["initial_flip"], char_def["data"], char_def["sheet"], char_def["steps"], char_def["sound"])
        player2_fighters.append(fighter)

    player1_current_fighter_index = 0
    player2_current_fighter_index = 0
    p1_fighter = player1_fighters[player1_current_fighter_index]
    p2_fighter = player2_fighters[player2_current_fighter_index]

    # Ensure fighters start fresh
    for f_list in [player1_fighters, player2_fighters]:
        for char_idx, f in enumerate(f_list):
            f.health = 100
            f.alive = True
            f.rect.y = 310 # Reset y position to ground
            # Reset x position based on player and initial definition
            if f.player == 1:
                # Ensure benched fighters are also positioned correctly if they were moved
                f.rect.x = player1_fighters_defs[char_idx]["initial_x"] if char_idx == 0 else player1_fighters_defs[char_idx]["initial_x"] - 50
                f.flip = player1_fighters_defs[char_idx]["initial_flip"]
            else: # player == 2
                # Ensure benched fighters are also positioned correctly if they were moved
                f.rect.x = player2_fighters_defs[char_idx]["initial_x"] if char_idx == 0 else player2_fighters_defs[char_idx]["initial_x"] + 50
                f.flip = player2_fighters_defs[char_idx]["initial_flip"]
            f.update_action(0) # Idle
            f.vel_y = 0 # Reset vertical velocity
            f.jump = False # Reset jump state
            f.attacking = False # Reset attacking state
            f.hit = False # Reset hit state
            f.attack_cooldown = 0 # Reset cooldown

    # Position active fighters correctly at the start of the round
    p1_fighter.rect.x = player1_fighters_defs[player1_current_fighter_index]["initial_x"]
    p2_fighter.rect.x = player2_fighters_defs[player2_current_fighter_index]["initial_x"]


    player1_last_switch_time = -SWITCH_COOLDOWN_TIME # Allow immediate switch at round start if needed
    player2_last_switch_time = -SWITCH_COOLDOWN_TIME # Allow immediate switch for P2 as well

    intro_count = 3 # Reset intro count
    round_over = False # Reset round over flag
    last_count_update = pygame.time.get_ticks() # Reset countdown timer


def switch_character_action(player_num, new_fighter_index):
    global p1_fighter, player1_current_fighter_index, player1_last_switch_time
    global p2_fighter, player2_current_fighter_index, player2_last_switch_time

    current_time = pygame.time.get_ticks()
    switch_successful = False

    if player_num == 1:
        # Check if the target character is alive and it's a different character
        if player1_fighters[new_fighter_index].alive and new_fighter_index != player1_current_fighter_index:
            old_fighter_state = {
                "rect_center": p1_fighter.rect.center, # Use center for smoother transition
                "vel_y": p1_fighter.vel_y,
                "jump": p1_fighter.jump,
                # "flip": p1_fighter.flip # Flip is determined by target, so don't force
            }
            # Move the current fighter off-screen or to a benched position visually
            p1_fighter.rect.x = -1000 # Example: move off-screen left
            # Update the active fighter
            player1_current_fighter_index = new_fighter_index
            p1_fighter = player1_fighters[player1_current_fighter_index]

            # Restore state to new fighter
            p1_fighter.rect.center = old_fighter_state["rect_center"]
            p1_fighter.vel_y = old_fighter_state["vel_y"]
            p1_fighter.jump = old_fighter_state["jump"]

            p1_fighter.update_action(0) # Reset to idle animation on switch
            p1_fighter.attacking = False # Cancel any ongoing attack
            p1_fighter.hit = False # Clear hit state
            player1_last_switch_time = current_time
            print(f"Player 1 switched to {player1_fighters_defs[new_fighter_index]['name']}")
            switch_successful = True # Switch successful
    elif player_num == 2:
        # Check if the target character is alive and it's a different character
        if player2_fighters[new_fighter_index].alive and new_fighter_index != player2_current_fighter_index:
             old_fighter_state = {
                "rect_center": p2_fighter.rect.center,
                "vel_y": p2_fighter.vel_y,
                "jump": p2_fighter.jump,
                # "flip": p2_fighter.flip
            }
             # Move the current fighter off-screen or to a benched position visually
             p2_fighter.rect.x = SCREEN_WIDTH + 1000 # Example: move off-screen right
             # Update the active fighter
             player2_current_fighter_index = new_fighter_index
             p2_fighter = player2_fighters[player2_current_fighter_index]

             p2_fighter.rect.center = old_fighter_state["rect_center"]
             p2_fighter.vel_y = old_fighter_state["vel_y"]
             p2_fighter.jump = old_fighter_state["jump"]

             p2_fighter.update_action(0)
             p2_fighter.attacking = False
             p2_fighter.hit = False
             player2_last_switch_time = current_time
             print(f"Player 2 switched to {player2_fighters_defs[player2_current_fighter_index]['name']}")
             switch_successful = True # Switch successful

    return switch_successful # Return status of the switch attempt


#function for drawing text
def draw_text(text, font, text_col, x, y):
  img = font.render(text, True, text_col)
  text_rect = img.get_rect(topleft=(x, y))
  screen.blit(img, text_rect)
  return text_rect # Return the rect for button handling

#function for drawing background
def draw_bg():
  # Check if bg_image was loaded successfully before trying to scale/blit
  if 'bg_image' in globals() and bg_image:
      scaled_bg = pygame.transform.scale(bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
      screen.blit(scaled_bg, (0, 0))
  else:
      # If background failed to load, just fill with black or another color
      screen.fill(BLACK)


#function for drawing fighter health bars
# Added player_num parameter to differentiate player 1 and player 2 bars
def draw_health_bar(health, x, y, player_num, width=400, height=30, is_active=True):
    # Ensure health is within valid range
    health = max(0, min(100, health))
    ratio = health / 100

    outline_color = WHITE if is_active else GREY
    bar_color = RED
    health_color = YELLOW if is_active else GREEN # Different color for benched health

    pygame.draw.rect(screen, outline_color, (x - 2, y - 2, width + 4, height + 4))
    pygame.draw.rect(screen, bar_color, (x, y, width, height))

    # Draw health bar from the left for Player 1, and from the right for Player 2
    if player_num == 1:
        pygame.draw.rect(screen, health_color, (x, y, width * ratio, height))
    elif player_num == 2:
        pygame.draw.rect(screen, health_color, (x + width * (1 - ratio), y, width * ratio, height))


# Function to draw switch cooldown status
def draw_switch_cooldown_status(player_num, last_switch_time, current_time, x, y):
    cooldown_remaining_ms = max(0, SWITCH_COOLDOWN_TIME - (current_time - last_switch_time)) # Ensure it doesn't go below 0

    can_switch_to_benched = False
    benched_fighter_name = ""
    benched_fighter_index = -1

    if player_num == 1:
        benched_fighter_index = (player1_current_fighter_index + 1) % len(player1_fighters)
        if benched_fighter_index < len(player1_fighters) and player1_fighters[benched_fighter_index].alive:
            can_switch_to_benched = True
        benched_fighter_name = player1_fighters_defs[benched_fighter_index]['name'] if benched_fighter_index < len(player1_fighters_defs) else "N/A" # Handle potential index error

    elif player_num == 2:
        benched_fighter_index = (player2_current_fighter_index + 1) % len(player2_fighters)
        if benched_fighter_index < len(player2_fighters) and player2_fighters[benched_fighter_index].alive:
            can_switch_to_benched = True
        benched_fighter_name = player2_fighters_defs[benched_fighter_index]['name'] if benched_fighter_index < len(player2_fighters_defs) else "N/A" # Handle potential index error


    if cooldown_remaining_ms > 0:
        text = f"Switch CD: {cooldown_remaining_ms / 1000:.1f}s"
        color = YELLOW
    else:
        if can_switch_to_benched:
            text = f"Switch to {benched_fighter_name} Ready!" # Indicate who's ready
            color = GREEN
        else:
            text = f"{benched_fighter_name} KO" # Indicate who is KO'd
            color = GREY

    draw_text(text, info_font, color, x, y)


# --- Menu Screen Functions ---
def draw_menu():
    screen.fill(BLACK) # Or draw a specific menu background

    # Corrected: Use font.size(text)[0] for width
    title_text = "Warriors Showdown"
    # Ensure font is loaded before getting size
    if 'count_font' in globals() and count_font:
        title_x = SCREEN_WIDTH / 2 - count_font.size(title_text)[0] / 2
        draw_text(title_text, count_font, WHITE, title_x, 100)
    else:
        # Fallback if font failed to load
        fallback_font = pygame.font.SysFont(None, 80)
        title_x = SCREEN_WIDTH / 2 - fallback_font.size(title_text)[0] / 2
        draw_text(title_text, fallback_font, WHITE, title_x, 100)


    # Menu Options
    single_player_text = "Single Player"
    multiplayer_text = "Multiplayer" # Removed "(Not Implemented)"
    quit_text = "Quit"

    # Corrected: Use font.size(text)[0] for width for centering
    # Ensure font is loaded before getting size
    if 'menu_font' in globals() and menu_font:
        sp_x = SCREEN_WIDTH / 2 - menu_font.size(single_player_text)[0] / 2
        mp_x = SCREEN_WIDTH / 2 - menu_font.size(multiplayer_text)[0] / 2
        q_x = SCREEN_WIDTH / 2 - menu_font.size(quit_text)[0] / 2
        font_to_use = menu_font
    else:
        # Fallback if font failed to load
        fallback_font = pygame.font.SysFont(None, 50)
        sp_x = SCREEN_WIDTH / 2 - fallback_font.size(single_player_text)[0] / 2
        mp_x = SCREEN_WIDTH / 2 - fallback_font.size(multiplayer_text)[0] / 2
        q_x = SCREEN_WIDTH / 2 - fallback_font.size(quit_text)[0] / 2
        font_to_use = fallback_font


    sp_y = SCREEN_HEIGHT / 2 - 50
    mp_y = sp_y + 60
    q_y = mp_y + 60

    # Draw text and store their rects for click detection (draw_text returns rect)
    single_player_rect = draw_text(single_player_text, font_to_use, WHITE, sp_x, sp_y)
    multiplayer_rect = draw_text(multiplayer_text, font_to_use, WHITE, mp_x, mp_y) # Set color to WHITE as it's implemented
    quit_rect = draw_text(quit_text, font_to_use, WHITE, q_x, q_y)

    return {
        "single_player": single_player_rect,
        "multiplayer": multiplayer_rect,
        "quit": quit_rect
    }

# --- AI Placeholder Function ---
# This function is only used in STATE_SINGLE_PLAYER
def get_ai_action(fighter, target, current_time, fighters_list, fighter_defs, current_fighter_index, last_switch_time, screen_width, screen_height):
    # This is a placeholder function.
    # Replace this with your AI agent's decision-making logic.
    # The AI should analyze the game state (fighter, target, current_time, etc.)
    # and return a dictionary of actions, similar to how player input is handled.
    # Possible actions could include:
    # "move": -1 (left), 1 (right), 0 (none)
    # "jump": True, False
    # "attack_type": 1, 2, 0 (0 means no attack)
    # "switch": Index of fighter to switch to, or None

    ai_action = {
        "move": 0, # Use 0 for no movement
        "jump": False,
        "attack_type": 0,
        "switch": None
    }

    # --- Basic AI Logic (Example: Just move towards player 1 and attack sometimes) ---
    # This is a very simple AI and will not play well.
    # You need to replace this with your trained AI model.

    # Check if AI is alive before attempting actions
    if fighter.alive:
        move_threshold = 50 # Pixels to stop moving when close
        attack_distance_threshold = 150 # Pixels to attempt attack

        # Determine movement towards or away from target
        if abs(fighter.rect.centerx - target.rect.centerx) > move_threshold:
            if target.rect.centerx < fighter.rect.centerx: # Target is to the left
                ai_action["move"] = -1
            elif target.rect.centerx > fighter.rect.centerx: # Target is to the right
                ai_action["move"] = 1
        else:
             ai_action["move"] = 0 # Stop if aligned or close enough

        # Simple attack logic: attack if target is close and cooldown is ready and not already attacking
        if abs(fighter.rect.centerx - target.rect.centerx) < attack_distance_threshold and fighter.attack_cooldown == 0 and not fighter.attacking:
             # Choose an attack type (simple alternation or random)
             ai_action["attack_type"] = 1 if pygame.time.get_ticks() % 2000 < 1000 else 2 # Example: alternate attacks
             ai_action["move"] = 0 # Stop moving when attempting to attack

        # Simple jump logic: jump occasionally if not already jumping
        if pygame.time.get_ticks() % 3000 < 30 and not fighter.jump and not fighter.attacking: # Small chance to jump if not jumping or attacking
             ai_action["jump"] = True

        # --- AI Switch Logic Placeholder ---
        # Example: Switch if active fighter is low on health and benched is alive and switch is ready
        benched_idx = (current_fighter_index + 1) % len(fighters_list)
        # Ensure benched_idx is within bounds of the list before accessing
        can_switch_to_benched = benched_idx < len(fighters_list) and fighters_list[benched_idx].alive
        cooldown_remaining_ms = SWITCH_COOLDOWN_TIME - (current_time - last_switch_time)

        if fighter.health < 40 and can_switch_to_benched and cooldown_remaining_ms <= 0 and not fighter.hit and not fighter.attacking:
             print(f"P2 AI deciding to switch from {fighter_defs[current_fighter_index]['name']} (Low Health)")
             ai_action["switch"] = benched_idx


    return ai_action


# Initialize fighters when entering the game state for the first time
# initialize_fighters() # Don't initialize here, do it when entering single player/multiplayer state


#game loop
run = True
print("Game loop started.") # Debug print
while run:

  clock.tick(FPS)
  current_time_ingame = pygame.time.get_ticks() # Get current time once per frame

  # Event handler outside the state machine to catch QUIT
  for event in pygame.event.get():
      if event.type == pygame.QUIT:
          run = False
          # sys.exit() # Let the loop finish and pygame.quit() be called

      # --- Handle Escape Key Press ---
      # Check for keydown event when in gameplay states
      if event.type == pygame.KEYDOWN:
          if event.key == pygame.K_ESCAPE:
              if current_state == STATE_SINGLE_PLAYER or current_state == STATE_MULTIPLAYER:
                  current_state = STATE_MENU
                  print("Escape pressed. Returning to STATE_MENU") # Debug print
                  # Reset game state variables for a clean return to menu
                  intro_count = 3
                  round_over = False
                  last_count_update = pygame.time.get_ticks()
                  score = [0, 0] # Reset score
                  # Optionally stop music when returning to menu
                  pygame.mixer.music.stop()
                  # Note: Fighters will be re-initialized when starting a new game from the menu


  if current_state == STATE_MENU:
      # print("Current state: STATE_MENU") # Debug print
      draw_bg() # Draw background on menu
      menu_rects = draw_menu()

      for event in pygame.event.get():
          if event.type == pygame.MOUSEBUTTONDOWN:
              if menu_rects["single_player"].collidepoint(event.pos):
                  current_state = STATE_SINGLE_PLAYER
                  print("Switching to STATE_SINGLE_PLAYER (Human vs AI)") # Debug print
                  # Initialize game variables for single player
                  # Note: Initialization now handled within initialize_fighters
                  initialize_fighters() # Initialize fighters for the new game
                  if not pygame.mixer.music.get_busy():
                       try:
                            pygame.mixer.music.play(-1, 0.0, 5000) # Start music
                            print("Music started.") # Debug print
                       except pygame.error as e:
                            print(f"Warning: Could not play music. {e}")

              if menu_rects["multiplayer"].collidepoint(event.pos):
                  current_state = STATE_MULTIPLAYER
                  print("Switching to STATE_MULTIPLAYER (Human vs Human)") # Debug print
                  # Initialize game variables for multiplayer
                   # Note: Initialization now handled within initialize_fighters
                  initialize_fighters() # Initialize fighters for the new game
                  if not pygame.mixer.music.get_busy():
                       try:
                            pygame.mixer.music.play(-1, 0.0, 5000) # Start music
                            print("Music started.") # Debug print
                       except pygame.error as e:
                            print(f"Warning: Could not play music. {e}")


              if menu_rects["quit"].collidepoint(event.pos):
                  run = False # Exit the main loop
                  print("Quit selected. Exiting game loop.") # Debug print


  elif current_state == STATE_SINGLE_PLAYER or current_state == STATE_MULTIPLAYER:
      # print(f"Current state: { 'STATE_SINGLE_PLAYER' if current_state == STATE_SINGLE_PLAYER else 'STATE_MULTIPLAYER' }") # Debug print
      #draw background
      draw_bg()

      #show player stats (active fighters)
      if 'p1_fighter' in globals() and p1_fighter and 'p2_fighter' in globals() and p2_fighter: # Check if fighters are initialized
          draw_text(f"P1: {player1_fighters_defs[player1_current_fighter_index]['name']}", score_font, WHITE, 20, 10)
          # Pass player number to draw_health_bar
          draw_health_bar(p1_fighter.health, 20, 40, 1)
          draw_text(f"P2: {player2_fighters_defs[player2_current_fighter_index]['name']}", score_font, WHITE, 580, 10)
          # Pass player number to draw_health_bar
          draw_health_bar(p2_fighter.health, 580, 40, 2)

          draw_text("P1 Score: " + str(score[0]), score_font, RED, 20, 160) # y-pos adjusted
          draw_text("P2 Score: " + str(score[1]), score_font, RED, 580, 160) # y-pos adjusted

          # Show benched character health
          p1_benched_index = (player1_current_fighter_index + 1) % len(player1_fighters)
          p1_benched_fighter = player1_fighters[p1_benched_index]
          draw_text(f"Bench: {player1_fighters_defs[p1_benched_index]['name']}", info_font, WHITE, 20, 80)
          if p1_benched_fighter.alive:
              # Pass player number to draw_health_bar for benched fighter
              draw_health_bar(p1_benched_fighter.health, 20, 105, 1, width=150, height=15, is_active=False)
          else:
              draw_text("KO", info_font, RED, 180, 105) # Adjusted x for "KO"

          p2_benched_index = (player2_current_fighter_index + 1) % len(player2_fighters)
          p2_benched_fighter = player2_fighters[p2_benched_index]
          draw_text(f"Bench: {player2_fighters_defs[p2_benched_index]['name']}", info_font, WHITE, 580, 80)
          if p2_benched_fighter.alive:
              # Pass player number to draw_health_bar for benched fighter
              draw_health_bar(p2_benched_fighter.health, 580, 105, 2, width=150, height=15, is_active=False)
          else:
              draw_text("KO", info_font, RED, 740, 105) # Adjusted x for "KO"


      # Display switch cooldown status (only when game is active)
      if intro_count <= 0 and 'p1_fighter' in globals() and p1_fighter and 'p2_fighter' in globals() and p2_fighter: # Check if fighters are initialized
          draw_switch_cooldown_status(1, player1_last_switch_time, current_time_ingame, 20, 130)
          draw_switch_cooldown_status(2, player2_last_switch_time, current_time_ingame, 580, 130)


      #update countdown or handle game logic
      if intro_count > 0:
        #display count timer
        # Ensure font is loaded before getting size
        if 'count_font' in globals() and count_font:
            count_text = str(intro_count)
            count_x = SCREEN_WIDTH / 2 - count_font.size(count_text)[0] / 2
            draw_text(count_text, count_font, RED, count_x, SCREEN_HEIGHT / 3) # Centered timer
        else:
            # Fallback if font failed to load
            fallback_font = pygame.font.SysFont(None, 80)
            count_text = str(intro_count)
            count_x = SCREEN_WIDTH / 2 - fallback_font.size(count_text)[0] / 2
            draw_text(count_text, fallback_font, RED, count_x, SCREEN_HEIGHT / 3)


        #update count timer
        if (current_time_ingame - last_count_update) >= 1000:
          intro_count -= 1
          last_count_update = current_time_ingame
          if intro_count < 0: # Ensure it doesn't go below 0
              intro_count = 0

      else: # intro_count is 0 or less, game is active
          # current_time_ingame is already defined above

          # Ensure fighters are initialized before processing inputs/AI
          if 'p1_fighter' in globals() and p1_fighter and 'p2_fighter' in globals() and p2_fighter:

              # --- Player 1 Controls (Human) ---
              keys = pygame.key.get_pressed()
              p1_action = {
                  "move": 0, # Use 0 for no movement
                  "jump": False,
                  "attack_type": 0,
                  "switch": None
              }
              if keys[pygame.K_a]: p1_action["move"] = -1 # -1 for left
              if keys[pygame.K_d]: p1_action["move"] = 1 # 1 for right
              # Jump input - set the jump flag and vertical velocity
              if keys[pygame.K_w] and not p1_fighter.jump and p1_fighter.alive and not round_over:
                  p1_action["jump"] = True
                  p1_fighter.vel_y = -30 # Apply initial jump velocity
                  p1_fighter.jump = True # Set jump state

              # Attack input
              if keys[pygame.K_r] and p1_fighter.alive and not round_over: p1_action["attack_type"] = 1
              if keys[pygame.K_t] and p1_fighter.alive and not round_over: p1_action["attack_type"] = 2

              # Player 1 manual switch input
              if keys[P1_SWITCH_KEY] and p1_fighter.alive and not round_over: # Only allow switch if current fighter is alive
                   # Check cooldown and if benched fighter is alive
                   cooldown_remaining = SWITCH_COOLDOWN_TIME - (current_time_ingame - player1_last_switch_time)
                   if cooldown_remaining <= 0:
                       next_idx = (player1_current_fighter_index + 1) % len(player1_fighters)
                       if next_idx < len(player1_fighters) and player1_fighters[next_idx].alive:
                           p1_action["switch"] = next_idx # Pass potential switch action
                       else:
                           # print("P1: Cannot switch - Benched fighter KO'd or index out of bounds.")
                           pass # Cannot switch


              # --- Player 2 Controls (Human or AI) ---
              p2_action = {
                  "move": 0,
                  "jump": False,
                  "attack_type": 0,
                  "switch": None
              }

              if current_state == STATE_SINGLE_PLAYER:
                  # Get AI action for Player 2
                  if p2_fighter.alive and not round_over:
                       p2_action = get_ai_action(
                            p2_fighter, p1_fighter, current_time_ingame,
                            player2_fighters, player2_fighters_defs,
                            player2_current_fighter_index, player2_last_switch_time,
                            SCREEN_WIDTH, SCREEN_HEIGHT
                            )
              elif current_state == STATE_MULTIPLAYER:
                  # Get Human input for Player 2 (using different keys)
                  if p2_fighter.alive and not round_over:
                       p2_keys = pygame.key.get_pressed()
                       if p2_keys[pygame.K_LEFT]: p2_action["move"] = -1 # -1 for left
                       if p2_keys[pygame.K_RIGHT]: p2_action["move"] = 1 # 1 for right
                       # Jump input - set the jump flag and vertical velocity
                       if p2_keys[pygame.K_UP] and not p2_fighter.jump and p2_fighter.alive and not round_over:
                            p2_action["jump"] = True
                            p2_fighter.vel_y = -30 # Apply initial jump velocity
                            p2_fighter.jump = True # Set jump state

                       # Attack input
                       if p2_keys[pygame.K_KP1] and p2_fighter.alive and not round_over: p2_action["attack_type"] = 1
                       if p2_keys[pygame.K_KP2] and p2_fighter.alive and not round_over: p2_action["attack_type"] = 2

                       # Player 2 manual switch input
                       if p2_keys[P2_SWITCH_KEY] and p2_fighter.alive and not round_over: # Only allow switch if current fighter is alive
                           # Check cooldown and if benched fighter is alive
                           cooldown_remaining_p2 = SWITCH_COOLDOWN_TIME - (current_time_ingame - player2_last_switch_time)
                           if cooldown_remaining_p2 <= 0:
                               next_idx = (player2_current_fighter_index + 1) % len(player2_fighters)
                               if next_idx < len(player2_fighters) and player2_fighters[next_idx].alive:
                                    p2_action["switch"] = next_idx # Pass potential switch action
                               else:
                                    # print("P2: Cannot switch - Benched fighter KO'd or index out of bounds.")
                                    pass # Cannot switch


              # Apply Player 1 actions (move is handled inside the fighter class based on dx)
              # The move method needs the direction to determine flip and running state correctly
              p1_fighter.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, p2_fighter, round_over, p1_action["move"])

              # Attack action is separate as it depends on cooldown and state
              if p1_action["attack_type"] > 0:
                   p1_fighter.attack(p2_fighter, p1_action["attack_type"])

              # Switch action
              if p1_action["switch"] is not None:
                  switch_character_action(1, p1_action["switch"])


              # Apply Player 2 actions
              p2_fighter.move(SCREEN_WIDTH, SCREEN_HEIGHT, screen, p1_fighter, round_over, p2_action["move"])

              if p2_action["attack_type"] > 0:
                   p2_fighter.attack(p1_fighter, p2_action["attack_type"])

              if p2_action["switch"] is not None:
                   # Switch action has its own cooldown check inside switch_character_action now
                   switch_character_action(2, p2_action["switch"])


          # --- update fighters ---
          # Ensure fighters are initialized before updating
          if 'p1_fighter' in globals() and p1_fighter:
              p1_fighter.update()
          if 'p2_fighter' in globals() and p2_fighter:
              p2_fighter.update()


          # --- draw fighters ---
          # Draw benched fighters slightly off-screen or in background if you want them visible
          # For now, only draw active fighters
          if 'p1_fighter' in globals() and p1_fighter:
              p1_fighter.draw(screen)
          if 'p2_fighter' in globals() and p2_fighter:
              p2_fighter.draw(screen)


          #check for player defeat
          if round_over == False: # Only check for defeat if round is not already over
              p1_can_continue = any(f.alive for f in player1_fighters)
              p2_can_continue = any(f.alive for f in player2_fighters)

              # Auto-switch if active fighter is KO'd and another is available
              # This logic is still relevant for both Human and AI
              if 'p1_fighter' in globals() and p1_fighter and not p1_fighter.alive and p1_can_continue:
                  print(f"P1: {player1_fighters_defs[player1_current_fighter_index]['name']} KO'd. Auto-switching...")
                  # Find the index of the next *alive* fighter
                  next_idx = (player1_current_fighter_index + 1) % len(player1_fighters)
                  # Loop through potential next fighters until an alive one is found or we loop back
                  start_idx = next_idx
                  while not player1_fighters[next_idx].alive and (next_idx + 1) % len(player1_fighters) != start_idx:
                      next_idx = (next_idx + 1) % len(player1_fighters)

                  if next_idx < len(player1_fighters) and player1_fighters[next_idx].alive: # Double check just in case
                       switch_character_action(1, next_idx)
                  else:
                       # This case should theoretically not be reached if p1_can_continue is True,
                       # but added for robustness. It means no other fighters are alive.
                       print("P1: No alive fighters left to auto-switch to.")


              if 'p2_fighter' in globals() and p2_fighter and not p2_fighter.alive and p2_can_continue:
                  print(f"P2: {player2_fighters_defs[player2_current_fighter_index]['name']} KO'd. Auto-switching...")
                  # Find the index of the next *alive* fighter
                  next_idx = (player2_current_fighter_index + 1) % len(player2_fighters)
                  # Loop through potential next fighters until an alive one is found or we loop back
                  start_idx = next_idx
                  while not player2_fighters[next_idx].alive and (next_idx + 1) % len(player2_fighters) != start_idx:
                       next_idx = (next_idx + 1) % len(player2_fighters)

                  if next_idx < len(player2_fighters) and player2_fighters[next_idx].alive: # Double check
                      switch_character_action(2, next_idx)
                  else:
                       # Robustness check
                       print("P2: No alive fighters left to auto-switch to.")


              # Re-check overall status after potential auto-switches to determine round end
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


          elif round_over == True: # round_over is True
            #display victory image
            # Ensure victory_img is loaded before blitting
            if 'victory_img' in globals() and victory_img:
                screen.blit(victory_img, (SCREEN_WIDTH / 2 - victory_img.get_width() / 2, SCREEN_HEIGHT / 3 - victory_img.get_height()/2))
            else:
                 # Fallback text if victory image failed to load
                 # Ensure font is loaded before getting size
                 if 'count_font' in globals() and count_font:
                     fallback_font_ro = count_font
                 else:
                     fallback_font_ro = pygame.font.SysFont(None, 80)
                 draw_text("Round Over!", fallback_font_ro, WHITE, SCREEN_WIDTH / 2 - fallback_font_ro.size("Round Over!")[0] / 2, SCREEN_HEIGHT / 3)


            if current_time_ingame - round_over_time > ROUND_OVER_COOLDOWN:
                # Round over, reset for next round or end match
                round_over = False
                intro_count = 3
                last_count_update = pygame.time.get_ticks() # Reset countdown timer
                initialize_fighters() # Reset fighter states, positions, and health for the new round
                print("Starting new round.") # Debug print
                # Check if a player has won the match (e.g., first to 2 rounds)
                # If match is over, perhaps go back to menu or show match result screen
                # For now, just go back to menu if score reaches 2 (example match win condition)
                if score[0] >= 2 or score[1] >= 2:
                     current_state = STATE_MENU
                     print("Match over. Returning to menu.") # Debug print
                     pygame.mixer.music.stop() # Stop music when returning to menu


  elif current_state == STATE_QUIT:
      run = False # Exit the main loop


  #update display
  pygame.display.update()

#exit pygame
pygame.quit()
# sys.exit() # Removed redundant sys.exit() here