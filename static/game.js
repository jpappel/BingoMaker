/**
 * @typedef {Object} Tile
 * @property {string} type - The tile's type (text or image)
 * @property {string} content - The tile content
 * @property {string[]} tags - Tags for the tile
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
