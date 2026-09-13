import copy
import random

SIZE = 9
BOX_SIZE = 3
EMPTY = 0
DIFFICULTY_CLUES = {
    'easy': 45,
    'medium': 40,
    'hard': 35,
}
# Keeping clue counts together ensures route validation and puzzle generation
# use the same difficulty contract.

def deep_copy(board):
    return copy.deepcopy(board)

def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]


def is_valid_board_values(board):
    if not isinstance(board, list) or len(board) != SIZE:
        return False

    return all(
        isinstance(row, list)
        and len(row) == SIZE
        and all(type(value) is int and EMPTY <= value <= SIZE for value in row)
        for row in board
    )


def get_clues_for_difficulty(difficulty):
    if not isinstance(difficulty, str):
        raise ValueError('Difficulty must be easy, medium, or hard.')

    normalized_difficulty = difficulty.strip().lower()
    if normalized_difficulty not in DIFFICULTY_CLUES:
        raise ValueError(
            'Invalid difficulty. Choose easy, medium, or hard.'
        )

    return DIFFICULTY_CLUES[normalized_difficulty]


def is_valid_board(board):
    if not isinstance(board, list) or len(board) != SIZE:
        return False

    for row in board:
        if not isinstance(row, list) or len(row) != SIZE:
            return False
        if any(not isinstance(value, int) or value < EMPTY or value > SIZE
               for value in row):
            return False
        filled_values = [value for value in row if value != EMPTY]
        if len(filled_values) != len(set(filled_values)):
            return False

    for column in range(SIZE):
        filled_values = [board[row][column] for row in range(SIZE)
                         if board[row][column] != EMPTY]
        if len(filled_values) != len(set(filled_values)):
            return False

    for box_row in range(0, SIZE, BOX_SIZE):
        for box_column in range(0, SIZE, BOX_SIZE):
            box_values = [
                board[row][column]
                for row in range(box_row, box_row + BOX_SIZE)
                for column in range(box_column, box_column + BOX_SIZE)
                if board[row][column] != EMPTY
            ]
            if len(box_values) != len(set(box_values)):
                return False

    return True


def find_empty_cell(board):
    for row in range(SIZE):
        for column in range(SIZE):
            if board[row][column] == EMPTY:
                return row, column
    return None


def find_hint(board, puzzle, solution):
    if not all(is_valid_board_values(candidate)
               for candidate in (board, puzzle, solution)):
        return None

    for row in range(SIZE):
        for column in range(SIZE):
            if puzzle[row][column] == EMPTY and board[row][column] == EMPTY:
                return {
                    'row': row,
                    'column': column,
                    'value': solution[row][column],
                }

    return None


def is_safe(board, row, col, num):
    # A candidate must satisfy all three Sudoku constraints before recursion
    # commits it to the working board.
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False
    # Check 3x3 box
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(BOX_SIZE):
        for j in range(BOX_SIZE):
            if board[start_row + i][start_col + j] == num:
                return False
    return True

def fill_board(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        # Undo this branch so the next candidate sees the board
                        # exactly as it was before the speculative assignment.
                        board[row][col] = EMPTY
                return False
    return True


def count_solutions(board, limit=2):
    """Count solutions, stopping once ``limit`` solutions are found."""
    if limit < 1:
        return 0

    working_board = deep_copy(board)
    if not is_valid_board(working_board):
        return 0

    def count_from_current_board():
        empty_cell = find_empty_cell(working_board)
        if empty_cell is None:
            return 1

        row, column = empty_cell
        solution_count = 0
        for number in range(1, SIZE + 1):
            if is_safe(working_board, row, column, number):
                working_board[row][column] = number
                solution_count += count_from_current_board()
                # Restore the empty cell before exploring the next candidate;
                # otherwise one branch would contaminate all later branches.
                working_board[row][column] = EMPTY

                if solution_count >= limit:
                    # Puzzle generation only needs to distinguish unique from
                    # non-unique puzzles, so a second solution is sufficient.
                    return limit

        return solution_count

    return count_from_current_board()


def remove_cells(board, clues):
    cells_to_remove = max(0, SIZE * SIZE - clues)
    positions = [(row, column)
                 for row in range(SIZE) for column in range(SIZE)]
    random.shuffle(positions)

    removed_cells = 0
    for row, column in positions:
        if removed_cells >= cells_to_remove:
            break

        original_value = board[row][column]
        if original_value == EMPTY:
            continue

        board[row][column] = EMPTY
        # Retain a removal only when the remaining puzzle still has one
        # solution, preserving uniqueness while reaching the clue target.
        if count_solutions(board, limit=2) == 1:
            removed_cells += 1
        else:
            board[row][column] = original_value

def generate_puzzle(clues=35, difficulty=None):
    if difficulty is not None:
        clues = get_clues_for_difficulty(difficulty)

    board = create_empty_board()
    fill_board(board)
    # Keep the completed board separate so the returned answer is unaffected
    # by clue removal from the playable puzzle.
    solution = deep_copy(board)
    remove_cells(board, clues)
    puzzle = deep_copy(board)
    return puzzle, solution
