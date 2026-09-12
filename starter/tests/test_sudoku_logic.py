import copy

import pytest
import sudoku_logic


COMPLETED_BOARD = [
    [5, 3, 4, 6, 7, 8, 9, 1, 2],
    [6, 7, 2, 1, 9, 5, 3, 4, 8],
    [1, 9, 8, 3, 4, 2, 5, 6, 7],
    [8, 5, 9, 7, 6, 1, 4, 2, 3],
    [4, 2, 6, 8, 5, 3, 7, 9, 1],
    [7, 1, 3, 9, 2, 4, 8, 5, 6],
    [9, 6, 1, 5, 3, 7, 2, 8, 4],
    [2, 8, 7, 4, 1, 9, 6, 3, 5],
    [3, 4, 5, 2, 8, 6, 1, 7, 9],
]


def count_clues(board):
    return sum(cell != sudoku_logic.EMPTY for row in board for cell in row)


def test_valid_completed_board_has_exactly_one_solution():
    assert sudoku_logic.count_solutions(COMPLETED_BOARD) == 1


def test_difficulty_configuration_has_expected_order():
    assert sudoku_logic.DIFFICULTY_CLUES == {
        'easy': 45,
        'medium': 40,
        'hard': 35,
    }
    assert (sudoku_logic.DIFFICULTY_CLUES['easy']
            > sudoku_logic.DIFFICULTY_CLUES['medium'])
    assert (sudoku_logic.DIFFICULTY_CLUES['medium']
            > sudoku_logic.DIFFICULTY_CLUES['hard'])


def test_valid_difficulty_names_return_configured_clues():
    for difficulty, clues in sudoku_logic.DIFFICULTY_CLUES.items():
        assert sudoku_logic.get_clues_for_difficulty(difficulty) == clues


def test_invalid_difficulty_raises_value_error():
    with pytest.raises(ValueError, match='Invalid difficulty'):
        sudoku_logic.get_clues_for_difficulty('impossible')


@pytest.mark.parametrize('difficulty', ['easy', 'medium', 'hard'])
def test_difficulty_puzzles_have_expected_clues_unique_solutions_and_matching_cells(
        difficulty):
    puzzle, solution = sudoku_logic.generate_puzzle(difficulty=difficulty)

    assert count_clues(puzzle) == sudoku_logic.DIFFICULTY_CLUES[difficulty]
    assert sudoku_logic.count_solutions(puzzle, limit=2) == 1
    for row in range(sudoku_logic.SIZE):
        for column in range(sudoku_logic.SIZE):
            if puzzle[row][column] != sudoku_logic.EMPTY:
                assert puzzle[row][column] == solution[row][column]


def test_generate_puzzle_without_arguments_preserves_default_clues():
    puzzle, solution = sudoku_logic.generate_puzzle()

    assert count_clues(puzzle) == 35
    assert sudoku_logic.count_solutions(puzzle, limit=2) == 1


def test_generate_puzzle_accepts_numeric_clues():
    puzzle, solution = sudoku_logic.generate_puzzle(35)

    assert count_clues(puzzle) == 35
    assert sudoku_logic.count_solutions(puzzle, limit=2) == 1


def test_empty_board_returns_two_when_limit_is_two():
    empty_board = sudoku_logic.create_empty_board()

    assert sudoku_logic.count_solutions(empty_board, limit=2) == 2


def test_invalid_board_has_no_solutions():
    invalid_board = copy.deepcopy(COMPLETED_BOARD)
    invalid_board[0][1] = invalid_board[0][0]

    assert sudoku_logic.count_solutions(invalid_board) == 0


def test_count_solutions_does_not_modify_input_board():
    board = copy.deepcopy(COMPLETED_BOARD)
    board[0][0] = sudoku_logic.EMPTY
    original_board = copy.deepcopy(board)

    assert sudoku_logic.count_solutions(board) == 1
    assert board == original_board


def test_generated_puzzle_has_exactly_one_solution():
    puzzle, solution = sudoku_logic.generate_puzzle()

    assert sudoku_logic.count_solutions(puzzle, limit=2) == 1


def test_every_puzzle_clue_matches_returned_solution():
    puzzle, solution = sudoku_logic.generate_puzzle()

    for row in range(sudoku_logic.SIZE):
        for column in range(sudoku_logic.SIZE):
            if puzzle[row][column] != sudoku_logic.EMPTY:
                assert puzzle[row][column] == solution[row][column]
