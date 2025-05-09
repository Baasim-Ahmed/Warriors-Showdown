# Warriors Showdown

## Description

Switch Strike Showdown is a 2D fighting game built with Pygame where two players can battle it out, each controlling a team of two distinct characters. Players can strategically switch between their characters during combat, adding a unique layer of depth to the classic fighting game formula.

## Features

* **Two-Player Local Multiplayer:** Battle against a friend on the same machine.
* **Dual Character Teams:** Each player selects and can switch between two unique fighters (currently Warrior and Wizard).
* **Character Switching Mechanic:**
    * Players can switch their active fighter during the match.
    * A cooldown period prevents spamming the switch ability.
    * Visual cooldown timer and status ("Ready", "KO") displayed on screen.
* **Automatic Switching:** If an active fighter is defeated, the game automatically switches to the player's benched character if available.
* **Health Bars:** Clear display of active and benched character health.
* **Round-Based Gameplay:** Win rounds by defeating both of your opponent's characters.
* **Score Tracking:** Keeps track of rounds won by each player.
* **Sound Effects & Music:** Basic audio for attacks and background music.
* **Animated Sprites:** Characters have animations for idle, run, jump, attack, hit, and death.

## Requirements

* Python 3.x
* Pygame library

## Installation

1.  **Clone the repository (or download the files):**
    ```bash
    git clone <your-repository-link>
    cd <repository-folder-name>
    ```
2.  **Install Pygame:**
    If you don't have Pygame installed, you can install it using pip:
    ```bash
    pip install pygame
    ```

## How to Play

1.  Navigate to the directory where you saved the game files.
2.  Run the main game file:
    ```bash
    python main.py
    ```

## Controls

### Player 1:
* **Move Left:** A
* **Move Right:** D
* **Jump:** W
* **Attack 1:** R
* **Attack 2:** T
* **Switch Character:** Q

### Player 2:
* **Move Left:** Left Arrow Key
* **Move Right:** Right Arrow Key
* **Jump:** Up Arrow Key
* **Attack 1:** Numpad 1
* **Attack 2:** Numpad 2
* **Switch Character:** Numpad 0

## Game Logic

* The game starts with an intro countdown.
* Each player controls their active fighter.
* Reduce your opponent's active fighter's health to zero to KO them.
* If a fighter is KO'd and the player has a benched character, the game will auto-switch.
* Players can manually switch characters if their benched character is alive and the switch cooldown has elapsed.
* A player wins the round when both of their opponent's characters are KO'd.
* The game keeps track of round scores.

## Assets

All game assets (images, sounds, fonts) are located in the `assets/` directory, categorized into:
* `assets/audio/`
* `assets/images/background/`
* `assets/images/icons/`
* `assets/images/warrior/Sprites/`
* `assets/images/wizard/Sprites/`
* `assets/fonts/`

The game expects this directory structure to load assets correctly.

## Future Enhancements (Ideas)

* More characters with unique abilities.
* Character selection screen.
* Different stages/arenas.
* More complex attack combos.
* AI for single-player mode.
* Improved UI and visual effects.

---

*This README was generated based on the game's state as of the last update.*
