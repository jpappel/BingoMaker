/**
 * @typedef {Object} Tile
 * @property {string} type - The tile's type (text or image)
 * @property {string} content - The tile content
 * @property {string[]) tags - Tags for the tile
 */

/**
 * @typedef {Object} tilepool
 * @property {string} id
 * @property {string} name
 * @property {Tile[]} tiles
 * @property {string} created_at
 * @property {string} owner
 */

/**
 * @typedef {Object} Bingocard
 * @property {string} id
 * @property {Tile[]} tiles
 * @property {number} size
 */

/**
 * Return if a board contains a win
 *
 * @param {boolean[][]} board - a square game board
 */
function checkBoardWin(board) {
    const size = board.length;

    function checkRowWin() {
        for (let row = 0; row < size; row++) {
            let isWin = true;
            for (let col = 0; col < size; col++) {
                isWin &= board[row][col];
            }
            if (isWin) { return true; }
        }

        return false
    }

    function checkColWin() {
        for (let col = 0; col < size; col++) {
            let isWin = true;
            for (let row = 0; row < size; row++) {
                isWin &= board[row][col];
            }
            if (isWin) { return true }
        }

        return false;
    }

    // check diagaonals
    function checkDiagWin() {
        let mainDiagWin = true;
        let offDiagWin = true;
        for (let i = 0; i < size; i++) {
            mainDiagWin &= board[i][i];
            offDiagWin &= board[i][size - i - 1];
        }

        return mainDiagWin || offDiagWin;
    }

    return checkDiagWin() || checkRowWin() || checkColWin();
}

/**
 * Generate a bingocard via the api
 * 
 * @param {string} tilepoolId
 * @param {number|null} size
 * @param {string|null} seed
 * @returns Bingocard
 */
async function getBingoCard(tilepoolId, size, seed) {
    let baseUrl = `${server_ip}/tilepools/${tilepoolId}`;
    let queryParams = ""
    if (size || seed) {
        queryParams += "?"
        queryParams += (size) ? `size=${size}` : ""
        queryParams += (seed) ? `seed=${seed}` : ""
    }
    const url = baseUrl + queryParams;

    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('Failed to fetch bingo card');
        }

        const bingocard = await response.json();
        return bingocard;
    } catch (error) {
        console.error("Error:", error);
        throw error;
    }
}

/**
 * @deprecated
 */
function checkBingoWin() {
    function displayWinMessage() {
        alert('BINGO! You have a winning card!');
    }

    const bingoCells = document.querySelectorAll('.bingo-cell');
    const size = 5; // Assuming a 5x5 bingo grid
    let cellArray = [];

    for (let i = 0; i < size; i++) {
        cellArray[i] = [];
        for (let j = 0; j < size; j++) {
            const index = i * size + j;
            cellArray[i][j] = bingoCells[index].classList.contains('marked');
        }
    }
    for (let i = 0; i < size; i++) {
        let rowWin = true;
        let colWin = true;

        for (let j = 0; j < size; j++) {
            if (!cellArray[i][j]) {
                rowWin = false;
            }
            if (!cellArray[j][i]) {
                colWin = false;
            }
        }
        if (rowWin || colWin) {
            displayWinMessage();
            return;
        }
    }
    let diagWin1 = true;
    let diagWin2 = true;
    for (let i = 0; i < size; i++) {
        if (!cellArray[i][i]) {
            diagWin1 = false;
        }
        if (!cellArray[i][size - i - 1]) {
            diagWin2 = false;
        }
    }

    if (diagWin1 || diagWin2) {
        displayWinMessage();
        return;
    }
}

/**
 * @deprecated
 */
async function fetchBingoCard(tilepoolId, size, seed) {
    tilepoolId = tilepoolId;
    const size = 5;
    const seed = Math.floor(Math.random() * 10000);

    try {
        // Fetch the tile pool to get its name
        const tilePoolResponse = await fetch(`${server_ip}/tilepools/${tilepoolId}`);
        if (!tilePoolResponse.ok) {
            throw new Error('Failed to fetch tile pool');
        }
        const tilePoolData = await tilePoolResponse.json();
        currentTilePoolName = tilePoolData.name; // Store the tile pool name

        // Fetch the bingo card
        const response = await fetch(`${server_ip}/bingocard/${tilepoolId}?size=${size}&seed=${seed}`);
        if (!response.ok) {
            throw new Error('Failed to fetch bingo card');
        }
        const data = await response.json();
        generateBingoCard(data);
    } catch (error) {
        console.error('Error:', error);
        alert('An error occurred while fetching the bingo card. Please try again later.');
    }
}

/**
 * @deprecated
 */
function saveCurrentBingoCard() {
    const bingoCells = document.querySelectorAll('.bingo-cell');
    const cardData = Array.from(bingoCells, (cell) => cell.textContent);

    // Prompt the user for a card name
    let cardName = prompt('Enter a name for this bingo card:');
    if (!cardName) {
        // If the user cancels or doesn't enter a name, use a default name
        cardName = 'Untitled Card';
    }

    // Get existing saved cards from localStorage
    let savedCards = JSON.parse(localStorage.getItem('savedBingoCards')) || [];

    // Implement a limit on the number of saved cards
    const maxCards = 50;
    if (savedCards.length >= maxCards) {
        savedCards.shift(); // Remove the oldest card
    }

    // Save the new card with its name
    savedCards.push({
        name: cardName,
        data: cardData
    });
    localStorage.setItem('savedBingoCards', JSON.stringify(savedCards));

    alert(`Bingo card "${cardName}" saved successfully!`);
}
