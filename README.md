# 🧩 Maze Game (Pygame)

A fun and interactive maze game built using **Pygame**, where players navigate through multiple levels, avoid enemies, and find the exit. The game features **AI pathfinding algorithms**, **sound effects**, and even supports **custom level creation**!

---

## 🎮 Features

- 🚶 Player movement with arrow keys.
- 👾 Smart enemies that chase the player using **A\* (A-Star) algorithm**.
- 🎧 Sound effects for **win** and **death** events.
- 🧠 Hiding mechanics to temporarily avoid enemies.
- ❤️ Health/lives system.
- 🔁 Automatic level switching.
- 🧱 Create and load your own **custom levels** using a built-in level editor.

---

## 🧠 Technologies Used

- **Python 3**
- **Pygame**
- **A\* Search Algorithm** for enemy movement
- **File I/O** and **Dynamic Imports** for level loading
- **Modular Architecture** for easy extension

---

## 🗂 Folder Structure

│
├── main.py # Main game file
├── maze_editor.py # Custom level editor
├── custom_level/ # Folder where new levels are stored (level_1.py, level_2.py, ...)
├── heart.png # UI image for lives
├── win.mp3 # Sound for winning
├── death.mp3 # Sound for getting caught
├── requirements.txt # Python dependencies
├── README.md # This file
└── custom_level.json # (Optional) Save system for level progress
 
 
