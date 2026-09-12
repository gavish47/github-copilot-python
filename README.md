# Refactor a Sudoku Game written in Python Flask

Use this simple Sudoku game as a starting point to practice your skills with GitHub Copilot. The goal is to refactor the code to use modern technologies, while also adding new features and improving the overall user experience.

## Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

### Dependencies

```
```

### Installation

1. Fork this repository to your GitHub account. (You can use the "Fork" button on the top right corner of the repository page.)

2. Clone your forked repository to your local machine.

3. Open a terminal window and navigate to the "github-copilot-python/starter" directory.

4. Create a Python virtual environment and activate it (optional but highly recommended).

```bash
python3 -m venv .venv
source .venv/bin/activate
```

5. Install required Python packages.

```bash
pip install -r requirements.txt
```

6. Run the Flask app.

```bash
python app.py
```

7. Open http://127.0.0.1:5000 in your browser.

## Project Instructions

Use GitHub Copilot to refactor the code for this game to add more advanced features. The goal is to create a more modern and maintainable codebase and add additional functionality to the final product. You can use any combination of code completion and chat features, like Ask, Edit, or Agent modes.


# Sudoku Game

A Flask-based Sudoku game refactored from a small legacy implementation. The browser provides the game board and interaction while Flask generates puzzles and checks submitted boards.

## Features

- Easy, Medium, and Hard difficulty levels.
- Valid Sudoku generation with exactly one solution.
- Locked prefilled cells and distinct hint cells.
- Immediate incorrect-entry feedback and a Check Solution button.
- Hints that fill and lock one correct editable cell.
- MM:SS timer that starts with a new puzzle and stops on completion.
- Top 10 leaderboard stored in browser localStorage.
- Leaderboard records player name, completion time, difficulty, and hints used.
- Safe handling of malformed leaderboard data and player names.
- User-controlled Dark Mode with persisted preference.
- Responsive desktop and mobile layout, including the Sudoku 3x3 block structure.
- Keyboard-friendly controls, labels, focus styles, status messages, and non-color error cues.

## Installation

Use Python 3 and a modern web browser.

From the `starter` directory, create and activate a virtual environment if desired:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Run the Application

From `starter`:

```powershell
python app.py
```

Open <http://127.0.0.1:5000> in a browser.

## Test

From `starter`, run the complete pytest suite:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

The suite covers Flask routes, board validation, difficulty behavior, unique-solution generation, Check, Hint, and rendered page controls. Browser-only behavior such as localStorage, Dark Mode, responsive layout, and timer interaction should also be checked manually in a browser.
