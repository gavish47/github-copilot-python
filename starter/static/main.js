// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
const LEADERBOARD_KEY = 'sudokuLeaderboard';
const THEME_KEY = 'sudokuTheme';
const DIFFICULTIES = new Set(['easy', 'medium', 'hard']);
let puzzle = [];
let currentDifficulty = 'hard';
let gameCompleted = false;
let timerId = null;
let elapsedSeconds = 0;
let finalElapsedSeconds = null;

function formatTime(seconds) {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${String(minutes).padStart(2, '0')}:${String(remainingSeconds).padStart(2, '0')}`;
}

function updateTimerDisplay() {
  document.getElementById('timer').innerText = `Time: ${formatTime(elapsedSeconds)}`;
}

function startTimer() {
  // Always clear an older interval first so repeated starts cannot accelerate time.
  stopTimer();
  timerId = setInterval(() => {
    elapsedSeconds += 1;
    updateTimerDisplay();
  }, 1000);
}

function stopTimer() {
  if (timerId !== null) {
    clearInterval(timerId);
    timerId = null;
  }
}

function resetTimer() {
  stopTimer();
  elapsedSeconds = 0;
  finalElapsedSeconds = null;
  updateTimerDisplay();
}

function setMessage(text, type = '') {
  const message = document.getElementById('message');
  message.classList.remove('message-error', 'message-success');
  if (type) message.classList.add(`message-${type}`);
  message.innerText = text;
}

function isBoardComplete(board) {
  return board.every(row => row.every(value => value !== 0));
}

function handleBoardInput(event) {
  const input = event.target;
  if (!input.matches('.sudoku-cell') || input.disabled) return;

  input.value = input.value.replace(/[^1-9]/g, '');
  // Recheck a changed value immediately, while leaving untouched blanks alone.
  input.classList.remove('incorrect');
  input.removeAttribute('aria-invalid');
  if (input.value) checkSolution(false);
}

function createLeaderboardRow(score, rank) {
  const row = document.createElement('tr');
  [rank, score.name, formatTime(score.time), score.difficulty, score.hints]
    .forEach(value => {
      const cell = document.createElement('td');
      cell.textContent = value;
      row.appendChild(cell);
    });
  return row;
}

function isValidScore(score) {
  return score
    && typeof score.name === 'string'
    && Number.isInteger(score.time)
    && score.time >= 0
    && DIFFICULTIES.has(score.difficulty)
    && Number.isInteger(score.hints)
    && score.hints >= 0;
}

function loadLeaderboard() {
  try {
    const storedScores = JSON.parse(localStorage.getItem(LEADERBOARD_KEY) || '[]');
    // Discard malformed persisted entries so old or edited storage cannot break
    // rendering or enter the sorted top ten.
    return Array.isArray(storedScores) ? storedScores.filter(isValidScore) : [];
  } catch (error) {
    return [];
  }
}

function sortScores(scores) {
  return scores.sort((first, second) => (
    first.time - second.time
    || first.name.localeCompare(second.name)
    || first.difficulty.localeCompare(second.difficulty)
    || first.hints - second.hints
  ));
}

function saveLeaderboard(scores) {
  try {
    localStorage.setItem(LEADERBOARD_KEY, JSON.stringify(scores));
  } catch (error) {
    // Storage can be disabled or full; the completed game remains usable.
    return false;
  }
  return true;
}

function renderLeaderboard() {
  const leaderboardBody = document.getElementById('leaderboard-body');
  leaderboardBody.replaceChildren();
  loadLeaderboard().slice(0, 10).forEach((score, index) => {
    leaderboardBody.appendChild(createLeaderboardRow(score, index + 1));
  });
}

function saveCompletedScore() {
  const enteredName = window.prompt('Enter your name for the leaderboard:');
  const name = enteredName && enteredName.trim() ? enteredName.trim() : 'Anonymous';
  const hints = Number.parseInt(
    document.getElementById('hints-used').innerText.replace(/\D/g, ''),
    10,
  ) || 0;
  const scores = loadLeaderboard();
  scores.push({
    name,
    time: finalElapsedSeconds,
    difficulty: currentDifficulty,
    hints,
  });
  saveLeaderboard(sortScores(scores).slice(0, 10));
  renderLeaderboard();
}

function applyTheme(darkMode) {
  document.body.classList.toggle('dark-mode', darkMode);
  const themeToggle = document.getElementById('theme-toggle');
  themeToggle.setAttribute('aria-pressed', String(darkMode));
  themeToggle.innerText = darkMode ? 'Light Mode' : 'Dark Mode';
}

function applyStoredTheme() {
  let darkMode = false;
  try {
    darkMode = localStorage.getItem(THEME_KEY) === 'dark';
  } catch (error) {
    darkMode = false;
  }
  applyTheme(darkMode);
}

function toggleTheme() {
  const darkMode = !document.body.classList.contains('dark-mode');
  applyTheme(darkMode);
  try {
    localStorage.setItem(THEME_KEY, darkMode ? 'dark' : 'light');
  } catch (error) {
    // The game remains usable when storage is unavailable.
  }
}

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  boardDiv.oninput = handleBoardInput;
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.className = 'sudoku-cell';
      input.setAttribute('aria-label', `Row ${i + 1}, column ${j + 1}`);
      input.dataset.row = i;
      input.dataset.col = j;
      if ((Math.floor(i / 3) + Math.floor(j / 3)) % 2 === 1) {
        input.classList.add('box-shaded');
      }
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function renderPuzzle(puz) {
  puzzle = puz;
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      inp.classList.remove('prefilled', 'hinted', 'incorrect');
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        inp.classList.add('prefilled');
      } else {
        inp.value = '';
        inp.disabled = false;
      }
    }
  }
}

async function newGame() {
  const difficulty = document.querySelector('input[name="difficulty"]:checked').value;
  const message = document.getElementById('message');
  // Stop the previous game while the new puzzle request is in flight.
  stopTimer();

  try {
    const res = await fetch(`/new?difficulty=${encodeURIComponent(difficulty)}`);
    const data = await res.json();
    if (!res.ok || !data.puzzle) {
      throw new Error(data.error || 'Unable to start a new game.');
    }
    renderPuzzle(data.puzzle);
    currentDifficulty = data.difficulty || difficulty;
    gameCompleted = false;
    resetTimer();
    startTimer();
    document.getElementById('hints-used').innerText = 'Hints: 0';
    setMessage('');
  } catch (error) {
    setMessage(error.message || 'Unable to start a new game.', 'error');
  }
}

function readBoard() {
  const inputs = document.getElementById('sudoku-board').getElementsByTagName('input');
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const value = inputs[i * SIZE + j].value;
      board[i][j] = value ? parseInt(value, 10) : 0;
    }
  }
  return board;
}

async function checkSolution(showSummary = true) {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const msg = document.getElementById('message');
  const board = readBoard();

  try {
    const res = await fetch('/check', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({board})
    });
    const data = await res.json();
    if (!res.ok || data.error) {
      throw new Error(data.error || 'Unable to check the solution.');
    }

    const incorrect = new Set(data.incorrect.map(x => x[0] * SIZE + x[1]));
    for (let idx = 0; idx < inputs.length; idx++) {
      const inp = inputs[idx];
      if (inp.disabled) continue;
      inp.classList.remove('incorrect');
      inp.removeAttribute('aria-invalid');
      if (incorrect.has(idx)) {
        inp.classList.add('incorrect');
        inp.setAttribute('aria-invalid', 'true');
      }
    }

    const boardIsComplete = isBoardComplete(board);
    if (boardIsComplete && incorrect.size === 0 && !gameCompleted) {
      // This guard makes completion and score recording a one-time transition.
      stopTimer();
      finalElapsedSeconds = elapsedSeconds;
      gameCompleted = true;
      setMessage(
        `Congratulations! You solved it in ${formatTime(finalElapsedSeconds)}.`,
        'success',
      );
      saveCompletedScore();
    } else if (showSummary && incorrect.size === 0) {
      setMessage('No incorrect entries yet.', 'success');
    } else if (showSummary && incorrect.size > 0) {
      setMessage('Some cells are incorrect.', 'error');
    }
  } catch (error) {
    setMessage(error.message || 'Unable to check the solution.', 'error');
  }
}

async function requestHint() {
  const msg = document.getElementById('message');
  try {
    const res = await fetch('/hint', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({board: readBoard()})
    });
    const data = await res.json();
    if (!res.ok || data.error) {
      throw new Error(data.error || 'Unable to get a hint.');
    }

    document.getElementById('hints-used').innerText = `Hints: ${data.hints_used}`;
    if (!data.hint) {
      setMessage(data.message, 'success');
      return;
    }

    const index = data.hint.row * SIZE + data.hint.column;
    const input = document.getElementById('sudoku-board').getElementsByTagName('input')[index];
    // Hints become fixed cells so later checks cannot treat them as user edits.
    input.value = data.hint.value;
    input.disabled = true;
    input.classList.add('hinted');
    setMessage('Hint added.', 'success');
  } catch (error) {
    setMessage(error.message || 'Unable to get a hint.', 'error');
  }
}

// Wire buttons
window.addEventListener('load', () => {
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  document.getElementById('hint').addEventListener('click', requestHint);
  document.getElementById('theme-toggle').addEventListener('click', toggleTheme);
  applyStoredTheme();
  renderLeaderboard();
  // initialize
  newGame();
});