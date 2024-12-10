let savedCardsModal;
let createTilesetModal;
let editModal;
let currentTilePoolName = null; 


// functionality
// * bingo game
// * tilepool creation/selection

const modals = {
    savedCard: null,
    createTilepool: null,
    edit: null
}


function initModals() {
    // create bootstrap modals
    modals.createTilepool = new bootstrap.Modal(document.getElementById('createTilesetModal'));
  
    // add event listeners
    //
    document.getElementById('create-btn')
        .addEventListener('click', () => {
            modals.createTilepool.show();
        });

    document.getElementById('save-btn')
        .addEventListener('click', () => {
            saveWords();
            modals.edit.hide();
        });
}

function login() {
  window.location.href = `${cognito_ip}/login`;
}

// Done: new tilepool form
const tilesetTilesInput = document.getElementById('tileset-tiles');
const numberedTilesDiv = document.getElementById('numbered-tiles');

tilesetTilesInput.addEventListener('input', () => {
  const tiles = tilesetTilesInput.value.split('\n').map(tile => tile.trim()).filter(tile => tile !== '');
  numberedTilesDiv.innerHTML = '';
  tiles.forEach((tile, index) => {
    const tileElement = document.createElement('div');
    tileElement.textContent = `${index + 1}. ${tile}`;
    numberedTilesDiv.appendChild(tileElement);
  });
});
document.getElementById('createTilesetForm').addEventListener('submit', async (event) => {
  event.preventDefault();

  const tilesetName = document.getElementById('tileset-name').value.trim();
  const tilesetTiles = document.getElementById('tileset-tiles').value.trim();

  if (!tilesetName || !tilesetTiles) {
    alert('Please provide a name and tiles for the tile pool.');
    return;
  }

  const tiles = tilesetTiles
    .split('\n')
    .map(tile => tile.trim())
    .filter(tile => tile !== '');

  if (tiles.length < 24) {
    alert('Please enter at least 24 tiles.');
    return;
  }

  const newTilePool = {
    name: tilesetName,
    tiles: tiles.map(tile => ({ type: 'text', content: tile, tags: [] })),
    free_tile: {
      type: 'text',
      content: 'FREE',
      tags: [],
    },
  };

  await createNewTileset(newTilePool);
});


  // Function to show the bingo section and hide the welcome section
  function showBingoSection() {
    const welcomeSection = document.getElementById('welcome-section');
    if (welcomeSection) {
      welcomeSection.style.display = 'none';
    }
    const bingoSection = document.getElementById('bingo-section');
    if (bingoSection) {
      bingoSection.style.display = 'block';
    }
  }

  // TODO: tilepool browser
// TODO: bingocard play

(function () {
  // Wait for the DOM to fully load before running scripts
  document.addEventListener('DOMContentLoaded', async () => {
    await initPage();

    document.getElementById('login-btn').addEventListener('click', login);

    // Initialize Bootstrap modals
    initModals();

      document.getElementById('createTilesetForm')
          .addEventListener('submit', async (event) => {
              event.preventDefault();

              const tilesetName = document.getElementById('tileset-name').value.trim();
              const tilesetTiles = document.getElementById('tileset-tiles').value.trim();

              if (!tilesetName || !tilesetTiles) {
                  alert('Please provide a name and tiles for the tile pool.');
                  return;
              }

              const tiles = tilesetTiles
                  .split('\n')
                  .map(tile => tile.trim())
                  .filter(tile => tile !== '');

              if (tiles.length < 24) {
                  alert('Please enter at least 24 tiles.');
                  return;
              }

              const newTilePool = {
                  name: tilesetName,
                  tiles: tiles.map(tile => ({ type: 'text', content: tile, tags: [] })),
                  free_tile: {
                      type: 'text',
                      content: 'FREE',
                      tags: []
                  }
              };
              await createNewTileset(newTilePool);
              createTilesetModal.hide();
          });

      document.getElementById('print-btn')
          .addEventListener('click', () => {
              window.print();
          });

      document.getElementById('view-saved-btn')
          .addEventListener('click', () => {
              displaySavedCards(); 
              modals.savedCard.show();
          });
      document.getElementById('save-card-btn')
          .addEventListener('click', () => {
              saveCurrentBingoCard();
          });

      document.getElementById('bingo-board')
          .addEventListener('click', (event) => {
              const cell = event.target;
              if (cell.classList.contains('bingo-cell')) {
                  cell.classList.toggle('marked');
                  checkBingoWin();
              }
          });
  });
  function generateBingoCard(bingocard) {
    const bingoBoard = document.getElementById('bingo-board');
    bingoBoard.innerHTML = ''; // Clear previous cells
  
    const { tiles, size } = bingocard;
  
    // Validate that the board will have exactly size * size tiles
    if (tiles.length < size * size) {
      console.error('Not enough tiles for the specified size');
      return;
    }
  
    // Use only the first size * size tiles
    const boardTiles = tiles.slice(0, size * size);
  
    // Set the grid layout to create a 5x5 bingo board
    bingoBoard.style.gridTemplateColumns = `repeat(${size}, 1fr)`;
    bingoBoard.style.gridTemplateRows = `repeat(${size}, 1fr)`;
  
    // Populate the board with tiles
    boardTiles.forEach((tile, index) => {
      const cell = document.createElement('div');
      cell.className = 'col bingo-cell';
  
      if (tile.type === 'text') {
        cell.textContent = tile.content;
      } else if (tile.type === 'image') {
        const img = document.createElement('img');
        img.src = tile.content;
        img.alt = 'Bingo Tile';
        img.classList.add('img-fluid');
        cell.appendChild(img);
      }
  
      // Mark the free tile if applicable
      if (tile.content === FREE_TILE_CONTENT) {
        cell.classList.add('free-cell', 'marked');
      }
  
      bingoBoard.appendChild(cell);
    });
  
    showSection()
  }
  


async function fetchAndGenerateBingoCard(tilepoolId, size, seed) {
  try {
    const bingocard = await getBingoCard(tilepoolId, size, seed);
    generateBingoCard(bingocard);
  } catch (error) {
    console.error('Error fetching or generating bingo card:', error);
  }
}

  // Function to show the bingo section and hide the welcome section
  function showBingoSection() {
    const welcomeSection = document.getElementById('welcome-section');
    if (welcomeSection) {
      welcomeSection.style.display = 'none';
    }
    const bingoSection = document.getElementById('bingo-section');
    if (bingoSection) {
      bingoSection.style.display = 'block';
    }
  }
  

  

  async function initPage() {
    // Show the welcome section and hide the bingo section
    const welcomeSection = document.getElementById('welcome-section');
    if (welcomeSection) {
      welcomeSection.style.display = 'block';
    }
    const bingoSection = document.getElementById('bingo-section');
    if (bingoSection) {
      bingoSection.style.display = 'none';
    }
  
  }

  // Function to create a new tile pool via the API
  async function createNewTileset(tileset) {
    try {
      const response = await fetch(`${server_ip}/tilepools`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(tileset),
      });
      if (!response.ok) {
        throw new Error('Failed to create tile pool');
      }
      const data = await response.json();
      alert('Tile pool created successfully!');
      console.log('Created Tile Pool:', data);
  
      // Fetch and generate the bingo card using the new tile pool
      await fetchAndGenerateBingoCard(data.id, 5);
    } catch (error) {
      console.error('Error:', error);
      alert('An error occurred while creating the tile pool. Please try again later.');
    }
  }
    
  window.createNewTileset = createNewTileset;

})();
