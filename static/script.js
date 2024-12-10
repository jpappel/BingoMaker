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
  
  function generateBingoCard(data) {
    const bingoBoard = document.getElementById('bingo-board');
    bingoBoard.innerHTML = ''; // Clear previous cells
  
    let grid = [];
  
    if (Array.isArray(data)) {
      // Input is an array of words
      let words = data.slice(0, 24); 
      words.splice(12, 0, 'FREE'); // Insert 'FREE' at the center
      grid = words.map((word) => ({ content: word }));
    } else if (data && Array.isArray(data.tiles)) {
      grid = data.tiles.slice(0, 25); // Ensure exactly 25 tiles for 5x5 grid
    } else if (data && Array.isArray(data.grid)) {
      grid = data.grid.slice(0, 25); // Ensure exactly 25 tiles for 5x5 grid
    } else {
      console.error('Invalid input for generateBingoCard');
      return;
    }
  
    // Generate the bingo board
    grid.forEach((tile) => {
      const cell = document.createElement('div');
      cell.className = 'bingo-cell';
      cell.textContent = tile.content || tile; // Handle both object and string types
  
      if (tile.content === 'FREE' || tile === 'FREE') {
        cell.classList.add('free-cell', 'marked');
      }
  
      bingoBoard.appendChild(cell);
    });
  
    showBingoSection();
  }
  
  // Update the click handler to use event delegation
  document.addEventListener('DOMContentLoaded', () => {
    const bingoBoard = document.getElementById('bingo-board');
    
    bingoBoard.addEventListener('click', (event) => {
      const cell = event.target;
      if (cell.classList.contains('bingo-cell') && !cell.classList.contains('free-cell')) {
        cell.classList.toggle('marked');
        checkBingoWin();
      }
    });
  });

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
