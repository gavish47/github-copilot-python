# Sudoku Project Instructions

## Project Goal

This is a Flask-based Sudoku game that is being refactored from legacy code.

The final application must include:

- Easy, Medium, and Hard difficulty levels
- Sudoku puzzles with exactly one unique solution
- Locked prefilled cells
- Immediate invalid-entry feedback
- Check button
- Hint button
- Completion message
- Timer
- Top 10 leaderboard
- LocalStorage persistence
- Dark mode
- Responsive desktop and mobile design
- Alternating styling for the 3x3 Sudoku boxes
- Accessible controls
- Automated tests

## Coding Standards

- Use Python 3 and modern Python features where appropriate.
- Follow PEP 8.
- Use 4 spaces for indentation.
- Use descriptive names.
- Keep functions small and focused.
- Avoid duplicated code.
- Use modular and reusable components.
- Add type hints where practical.
- Add useful comments for non-obvious logic.
- Do not add unnecessary dependencies.
- Preserve working functionality when refactoring.
- Handle invalid input and errors gracefully.

## Sudoku Logic

A Sudoku board is 9x9.

A valid solution must contain numbers 1-9 exactly once in every:

- Row
- Column
- 3x3 box

Every generated puzzle MUST have exactly one solution.

When generating a puzzle:

1. Generate a complete valid Sudoku.
2. Remove cells according to the selected difficulty.
3. Count the number of solutions after removals.
4. Keep a removal only when exactly one solution remains.
5. Never assume that a puzzle is unique without checking.

The solver should be reusable for:

- Solving puzzles
- Counting solutions
- Validating uniqueness

## Difficulty

Support:

- Easy
- Medium
- Hard

Difficulty should control the number of prefilled cells.

Keep difficulty configuration in one clearly defined place instead of scattering magic numbers throughout the code.

## Flask

Keep Flask route handlers focused on HTTP requests and responses.

Keep Sudoku generation, solving, validation, and uniqueness logic separate from Flask routes.

Validate incoming request data and return useful HTTP/JSON errors.

Do not use unnecessary global mutable state.

## Frontend

Use modern JavaScript.

Keep rendering, API communication, game state, validation feedback, and UI behavior organized into small functions.

Handle network and invalid-response errors gracefully.

## Leaderboard

The Top 10 leaderboard must store:

- Player name
- Completion time
- Difficulty
- Number of hints

Use browser localStorage.

Scores must persist across page refreshes and browser sessions.

Sort fastest times first and keep only the top 10.

Validate stored data before using it.

## Timer

The timer starts with a new game and stops when the puzzle is solved.

Display elapsed time as MM:SS.

## Hint

A hint must:

- Fill one currently empty editable cell with the correct answer.
- Lock that cell.
- Visually identify the hinted cell.
- Increase the hint count.

## Check

The Check button should identify incorrect player entries without marking untouched empty cells as incorrect.

## Styling

The application must:

- Work in light and dark modes.
- Work on desktop and mobile.
- Avoid horizontal overflow on mobile.
- Clearly distinguish the nine 3x3 Sudoku boxes.
- Maintain consistent cell sizes.
- Keep text and controls readable.

Use CSS variables for themes where practical.

## Accessibility

Use semantic HTML, accessible labels, keyboard-friendly controls, visible focus states, and sufficient contrast.

Do not rely only on color to communicate errors.

## Testing

Before every major change:

- Run the existing test suite.
- Make sure tests pass.
- Add tests for important new functionality.
- Do not knowingly leave failing tests.

Use pytest.

The README must contain the test command.

## Copilot Workflow

Before making major changes:

1. Inspect the existing implementation.
2. Explain the proposed changes.
3. Make small, incremental changes.
4. Do not rewrite unrelated code.
5. Explain unfamiliar or complex code when requested.
6. Review generated code before accepting it.
7. Test all changes.

If a Copilot suggestion introduces unnecessary complexity or does not satisfy the project requirements, reject or modify it rather than accepting it blindly.

## Project Documentation

Keep the README updated.

The Screenshots folder must contain evidence of Copilot usage for major milestones, including:

- Testing framework
- Unique Sudoku solution
- Top 10 leaderboard/localStorage
- 3x3 grid styling

At least one screenshot must demonstrate evaluating or rejecting a Copilot suggestion.