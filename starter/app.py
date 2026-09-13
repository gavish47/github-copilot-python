from flask import Flask, render_template, jsonify, request
import sudoku_logic

app = Flask(__name__)

# The browser owns the visible board; this store supplies the matching solution
# for the current session without exposing it in the initial page response.
CURRENT = {
    'puzzle': None,
    'solution': None,
    'hints_used': 0,
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new')
def new_game():
    selected_difficulty = request.args.get('difficulty')
    if selected_difficulty is not None:
        try:
            clues = sudoku_logic.get_clues_for_difficulty(selected_difficulty)
        except ValueError as error:
            return jsonify({'error': str(error)}), 400
    else:
        try:
            clues = int(request.args.get('clues', 35))
        except (TypeError, ValueError):
            return jsonify({'error': 'Clues must be an integer.'}), 400
        if not 0 <= clues <= sudoku_logic.SIZE * sudoku_logic.SIZE:
            return jsonify({'error': 'Clues must be between 0 and 81.'}), 400

    puzzle, solution = sudoku_logic.generate_puzzle(clues)
    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    CURRENT['hints_used'] = 0
    response = {'puzzle': puzzle}
    if selected_difficulty is not None:
        response['difficulty'] = selected_difficulty.strip().lower()
    return jsonify(response)

@app.route('/check', methods=['POST'])
def check_solution():
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400

    data = request.get_json(silent=True)
    board = data.get('board') if isinstance(data, dict) else None
    # Reject malformed requests before comparing cells so API callers receive a
    # predictable error instead of an indexing or type exception.
    if not sudoku_logic.is_valid_board_values(board):
        return jsonify({
            'error': 'Board must be a 9x9 grid containing integers from 0 to 9.'
        }), 400

    puzzle = CURRENT['puzzle']
    incorrect = []
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            # Empty cells are intentionally ignored: Check reports wrong
            # entries, not unfinished work or changes to fixed clues.
            if (puzzle[i][j] == sudoku_logic.EMPTY
                    and board[i][j] != sudoku_logic.EMPTY
                    and board[i][j] != solution[i][j]):
                incorrect.append([i, j])
    return jsonify({'incorrect': incorrect})


@app.route('/hint', methods=['POST'])
def get_hint():
    puzzle = CURRENT.get('puzzle')
    solution = CURRENT.get('solution')
    if puzzle is None or solution is None:
        return jsonify({'error': 'No game in progress'}), 400

    data = request.get_json(silent=True)
    board = data.get('board') if isinstance(data, dict) else None
    # Keep malformed hint requests from changing the session hint counter.
    if not sudoku_logic.is_valid_board_values(board):
        return jsonify({
            'error': 'Board must be a 9x9 grid containing integers from 0 to 9.'
        }), 400

    hint = sudoku_logic.find_hint(board, puzzle, solution)
    if hint is None:
        return jsonify({
            'hint': None,
            'hints_used': CURRENT['hints_used'],
            'message': 'No empty editable cells remain.',
        })

    # Only a returned hint counts; asking when no editable cell remains does not.
    CURRENT['hints_used'] += 1
    return jsonify({
        'hint': hint,
        'hints_used': CURRENT['hints_used'],
    })

if __name__ == '__main__':
    app.run(debug=True)