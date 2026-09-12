import copy

import pytest
from flask import Flask

import sudoku_logic
from app import CURRENT, app


@pytest.fixture(autouse=True)
def reset_current_game():
    CURRENT['puzzle'] = None
    CURRENT['solution'] = None
    CURRENT['hints_used'] = 0
    yield
    CURRENT['puzzle'] = None
    CURRENT['solution'] = None
    CURRENT['hints_used'] = 0


def start_game(client):
    client.get('/new')
    return CURRENT['puzzle'], CURRENT['solution']


def test_app_can_start():
    assert isinstance(app, Flask)


def test_main_page_responds_successfully():
    client = app.test_client()

    response = client.get('/')

    assert response.status_code == 200
    assert b'Sudoku Game' in response.data


def test_main_page_includes_difficulty_selector_with_hard_default():
    client = app.test_client()

    response = client.get('/')

    assert b'value="easy"' in response.data
    assert b'value="medium"' in response.data
    assert b'value="hard" checked' in response.data
    assert b'id="timer"' in response.data
    assert b'Time: 00:00' in response.data
    assert b'id="hint"' in response.data
    assert b'id="hints-used">Hints: 0' in response.data
    assert b'id="theme-toggle"' in response.data
    assert b'id="leaderboard-body"' in response.data


def test_new_route_returns_a_sudoku_puzzle():
    client = app.test_client()

    response = client.get('/new')

    assert response.status_code == 200
    assert 'puzzle' in response.json


@pytest.mark.parametrize('difficulty', ['easy', 'medium', 'hard'])
def test_new_route_accepts_difficulty(difficulty):
    client = app.test_client()

    response = client.get(f'/new?difficulty={difficulty}')

    assert response.status_code == 200
    assert response.json['difficulty'] == difficulty
    assert len(response.json['puzzle']) == sudoku_logic.SIZE


def test_new_route_rejects_invalid_difficulty():
    client = app.test_client()

    response = client.get('/new?difficulty=impossible')

    assert response.status_code == 400
    assert response.json == {
        'error': 'Invalid difficulty. Choose easy, medium, or hard.'
    }


def test_new_route_returns_a_9_by_9_puzzle():
    client = app.test_client()

    puzzle = client.get('/new').json['puzzle']

    assert len(puzzle) == sudoku_logic.SIZE
    assert all(len(row) == sudoku_logic.SIZE for row in puzzle)
    assert all(cell in range(sudoku_logic.EMPTY, sudoku_logic.SIZE + 1)
               for row in puzzle for cell in row)


def test_check_route_returns_error_when_no_game_is_active():
    client = app.test_client()

    response = client.post('/check', json={'board': sudoku_logic.create_empty_board()})

    assert response.status_code == 400
    assert response.json == {'error': 'No game in progress'}


def test_check_route_accepts_a_valid_9_by_9_board_after_new_game():
    client = app.test_client()
    puzzle = client.get('/new').json['puzzle']

    response = client.post('/check', json={'board': puzzle})

    assert response.status_code == 200
    assert 'incorrect' in response.json
    assert isinstance(response.json['incorrect'], list)


def test_check_route_rejects_invalid_board_dimensions():
    client = app.test_client()
    start_game(client)

    response = client.post('/check', json={'board': [[0] * 9]})

    assert response.status_code == 400
    assert '9x9 grid' in response.json['error']


def test_check_route_rejects_missing_board():
    client = app.test_client()
    start_game(client)

    response = client.post('/check', json={})

    assert response.status_code == 400
    assert '9x9 grid' in response.json['error']


def test_check_route_rejects_invalid_board_values():
    client = app.test_client()
    start_game(client)
    invalid_board = sudoku_logic.create_empty_board()
    invalid_board[0][0] = 10

    response = client.post('/check', json={'board': invalid_board})

    assert response.status_code == 400
    assert 'integers from 0 to 9' in response.json['error']


def test_check_route_does_not_report_empty_cells():
    client = app.test_client()
    puzzle, _ = start_game(client)

    response = client.post('/check', json={'board': puzzle})

    assert response.json['incorrect'] == []


def test_check_route_does_not_report_correct_values():
    client = app.test_client()
    _, solution = start_game(client)

    response = client.post('/check', json={'board': solution})

    assert response.json['incorrect'] == []


def test_check_route_reports_incorrect_editable_values():
    client = app.test_client()
    puzzle, solution = start_game(client)
    board = copy.deepcopy(puzzle)
    target = next(
        (row, column)
        for row in range(sudoku_logic.SIZE)
        for column in range(sudoku_logic.SIZE)
        if puzzle[row][column] == sudoku_logic.EMPTY
    )
    row, column = target
    board[row][column] = solution[row][column] % sudoku_logic.SIZE + 1

    response = client.post('/check', json={'board': board})

    assert [row, column] in response.json['incorrect']


def test_check_route_does_not_report_changed_prefilled_cells():
    client = app.test_client()
    puzzle, solution = start_game(client)
    board = copy.deepcopy(puzzle)
    row, column = next(
        (row, column)
        for row in range(sudoku_logic.SIZE)
        for column in range(sudoku_logic.SIZE)
        if puzzle[row][column] != sudoku_logic.EMPTY
    )
    board[row][column] = solution[row][column] % sudoku_logic.SIZE + 1

    response = client.post('/check', json={'board': board})

    assert [row, column] not in response.json['incorrect']


def test_hint_requires_an_active_game():
    client = app.test_client()

    response = client.post('/hint', json={'board': sudoku_logic.create_empty_board()})

    assert response.status_code == 400
    assert response.json == {'error': 'No game in progress'}


def test_hint_returns_correct_value_for_an_editable_cell():
    client = app.test_client()
    puzzle, solution = start_game(client)
    board = copy.deepcopy(puzzle)

    response = client.post('/hint', json={'board': board})
    hint = response.json['hint']

    assert response.status_code == 200
    assert hint['value'] == solution[hint['row']][hint['column']]
    assert puzzle[hint['row']][hint['column']] == sudoku_logic.EMPTY
    assert response.json['hints_used'] == 1


def test_hint_counter_increments_once_per_successful_hint():
    client = app.test_client()
    puzzle, _ = start_game(client)
    board = copy.deepcopy(puzzle)

    first_response = client.post('/hint', json={'board': board})
    first_hint = first_response.json['hint']
    board[first_hint['row']][first_hint['column']] = first_hint['value']
    second_response = client.post('/hint', json={'board': board})

    assert first_response.json['hints_used'] == 1
    assert second_response.json['hints_used'] == 2


def test_new_game_resets_hint_counter():
    client = app.test_client()
    puzzle, _ = start_game(client)
    hint_response = client.post('/hint', json={'board': puzzle})
    assert hint_response.json['hints_used'] == 1

    response = client.get('/new')

    assert response.status_code == 200
    assert CURRENT['hints_used'] == 0


def test_hint_counter_does_not_increment_for_invalid_request():
    client = app.test_client()
    start_game(client)

    response = client.post('/hint', json={'board': [[0] * 9]})

    assert response.status_code == 400
    assert CURRENT['hints_used'] == 0


def test_hint_rejects_invalid_board_values():
    client = app.test_client()
    start_game(client)
    invalid_board = sudoku_logic.create_empty_board()
    invalid_board[0][0] = -1

    response = client.post('/hint', json={'board': invalid_board})

    assert response.status_code == 400
    assert 'integers from 0 to 9' in response.json['error']


def test_hint_returns_no_hint_when_no_editable_cells_remain():
    client = app.test_client()
    _, solution = start_game(client)

    response = client.post('/hint', json={'board': solution})

    assert response.status_code == 200
    assert response.json == {
        'hint': None,
        'hints_used': 0,
        'message': 'No empty editable cells remain.',
    }


def test_generated_solution_has_valid_rows_columns_and_boxes():
    puzzle, solution = sudoku_logic.generate_puzzle()
    expected_numbers = set(range(1, sudoku_logic.SIZE + 1))

    assert len(puzzle) == sudoku_logic.SIZE
    assert len(solution) == sudoku_logic.SIZE
    assert all(set(row) == expected_numbers for row in solution)

    for column in range(sudoku_logic.SIZE):
        assert {solution[row][column] for row in range(sudoku_logic.SIZE)} == expected_numbers

    for box_row in range(0, sudoku_logic.SIZE, 3):
        for box_column in range(0, sudoku_logic.SIZE, 3):
            box = {
                solution[row][column]
                for row in range(box_row, box_row + 3)
                for column in range(box_column, box_column + 3)
            }
            assert box == expected_numbers
