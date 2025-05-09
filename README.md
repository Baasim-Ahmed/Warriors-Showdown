# Warriors Showdown

## Watch the demo video 
(https://drive.google.com/file/d/15CuHf-hprKG7_aIvWdqDNnAvCiFVngnL/view?usp=drive_link)](https://drive.google.com/file/d/1Ga5eI_i8OSUZIn3kXFGB6MENsiYLKV0i/view?usp=drive_link)

## Description

A 2D fighting game built with Pygame, featuring multiple characters per player and character switching mechanics. This project serves as a foundation for developing AI agents to play fighting games, with an initial implementation for human vs. human local multiplayer and a placeholder for human vs. AI mode.

## Features

* **Core Fighting Mechanics:** Basic movement (run, jump), attacks, health bars, and collision detection.
* **Multi-Character Teams:** Each player has a team of multiple fighters.
* **Character Switching:** Players can switch between their active and benched fighters during gameplay (subject to a cooldown).
* **Home Menu:** Start screen with options for Single Player, Multiplayer, and Quit.
* **Single Player Mode:** Human player vs. an AI opponent (currently uses a basic placeholder AI logic - needs training).
* **Multiplayer Mode:** Local human player vs. human player on the same keyboard using different control sets.
* **Return to Menu:** Pressing the Escape key during gameplay returns to the main menu.
* **Round System:** Tracks scores and resets fighters after a round ends until a match win condition is met (currently hardcoded to 2 rounds).

## Requirements

* Python 3.x
* Pygame library (`pip install pygame`)
* Game assets (images, fonts, audio) in the specified `assets` directory structure. Ensure you have the following:
    * `assets/audio/music.mp3`
    * `assets/audio/sword.wav`
    * `assets/audio/magic.wav`
    * `assets/fonts/turok.ttf`
    * `assets/images/background/background.jpg`
    * `assets/images/icons/victory.png`
    * `assets/images/warrior/Sprites/warrior.png`
    * `assets/images/wizard/Sprites/wizard.png`

## How to Run

1.  Ensure you have Python and Pygame installed.
2.  Place the `main.py` and `fighter.py` files, along with the `assets` folder containing the required files, in the same directory.
3.  Open a terminal or command prompt in that directory.
4.  Run the command: `python main.py`

## Controls

Controls are active during Single Player and Multiplayer game modes when the intro countdown finishes.

### Player 1

* **Move Left:** `A` key
* **Move Right:** `D` key
* **Jump:** `W` key
* **Attack 1:** `R` key
* **Attack 2:** `T` key
* **Switch Character:** `Q` key
* **Return to Menu:** `Escape` key (during gameplay)

### Player 2 (Local Multiplayer)

* **Move Left:** `Left Arrow` key
* **Move Right:** `Right Arrow` key
* **Jump:** `Up Arrow` key
* **Attack 1:** `Numpad 1` key
* **Attack 2:** `Numpad 2` key
* **Switch Character:** `Numpad 0` key
* **Return to Menu:** `Escape` key (during gameplay)

## Project Structure

* `main.py`: Contains the main game loop, state management (menu, single player, multiplayer), input handling, drawing logic, and game variable management. Includes a placeholder `get_ai_action` function for the AI opponent.
* `fighter.py`: Defines the `Fighter` class, handling character-specific properties, animations, movement, attack logic, and health.
* `assets/`: Directory containing subfolders for audio, fonts, and images.

## Future Enhancements

* **Train the AI:** Replace the basic placeholder logic in `get_ai_action` with a trained AI model (e.g., using Reinforcement Learning) to create a more challenging single-player opponent.
* **More Characters:** Add more fighter classes and integrate them into the character selection and switching system.
* **Special Moves:** Implement unique special moves for each character.
* **Improved Animations and Effects:** Enhance visual feedback for hits, attacks, and switches.
* **Sound Effects:** Add more distinct sound effects for different actions.
* **UI Improvements:** Add character selection screens, win/loss screens, pause menu, etc.
* **Network Multiplayer:** (Advanced) Implement online play using networking concepts and libraries.

## AI Development Focus

The current structure allows for the integration of an AI agent that can control Player 2 in Single Player mode. The `get_ai_action` function is the entry point where your AI's decision-making logic would reside. Developing a strong AI for a fighting game, especially with character switching, is the primary AI challenge this project is designed to explore, likely requiring techniques such as Reinforcement Learning.

---
