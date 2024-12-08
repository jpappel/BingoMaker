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

// Function to save words from the modal input and update the bingo card
// FIXME: this needs to be refactored
function saveWords() {
    const inputText = document.getElementById('create-card-input').value.trim();
    if (inputText !== '') {
        const words = inputText
            .split('\n')
            .map((word) => word.trim())
            .filter((word) => word !== '');

        if (words.length < 24) {
            alert('Please enter at least 24 words.');
            return;
        }

        currentTilePoolName = null; // Clear tile pool name
        generateBingoCard(words);
    } else {
        // If input is empty, fetch a random bingo card
        fetchBingoCard();
    }
    document.getElementById('create-card-input').value = ''; // Clear the input
}

function initModals() {
    // create bootstrap modals
    modals.savedCard = new bootstrap.Modal(document.getElementById('saved-cards-modal'))
    modals.createTilepool = new bootstrap.Modal(document.getElementById('createTilesetModal'));
    modals.edit = new bootstrap.Modal(document.getElementById('modal'));

    // add event listeners
    // NOTE: may not be correct, they all interacted with the edit modal
    //       originally, could not tell if this was a bug
    document.getElementById('create-btn')
        .addEventListener('click', () => {
            modals.createTilepool.show();
        });
    document.getElementById('edit-btn')
        .addEventListener('click', () => {
            modals.edit.show();
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

// TODO: new tilepool form
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
        grid = data.tiles;
    } else if (data && Array.isArray(data.grid)) {
        grid = data.grid;
    } else {
        console.error('Invalid input for generateBingoCard');
        return;
    }

    // Generate the bingo board
    grid.forEach((tile, index) => {
        const cell = document.createElement('div');
        cell.className = 'col bingo-cell';
        cell.textContent = tile.content || tile; // Handle both object and string types

        if (tile.content === 'FREE' || tile === 'FREE') {
            cell.classList.add('free-cell', 'marked');
        }

        bingoBoard.appendChild(cell);
    });

    showBingoSection();
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

  function displaySavedCards() {
    const savedCardsList = document.getElementById('saved-cards-list');
    if (!savedCardsList) return;
    savedCardsList.innerHTML = ''; // Clear previous list
  
    let savedCards = JSON.parse(localStorage.getItem('savedBingoCards')) || [];
  
    if (savedCards.length === 0) {
      savedCardsList.innerHTML = '<li class="list-group-item">No saved bingo cards.</li>';
      return;
    }
  
    savedCards.forEach((card, index) => {
      const cardName = card.name || `Bingo Card ${index + 1}`; // Use card name or default
  
      const listItem = document.createElement('li');
      listItem.textContent = cardName;
      listItem.classList.add('list-group-item');
      listItem.style.cursor = 'pointer';
      listItem.addEventListener('click', () => {
        loadBingoCard(card);
        savedCardsModal.hide();
        showBingoSection();
      });
      savedCardsList.appendChild(listItem);
    });
  }
  

  function loadBingoCard(card) {
    const cardData = card.data || card; // Handle both new and old formats
    const grid = cardData.map((content) => ({ content }));
    generateBingoCard({ tiles: grid }); // Generate the bingo board with the loaded card data
  
    // Set currentTilePoolName if available
    currentTilePoolName = card.name || null;
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
  
    currentTilePoolName = null; // Clear the tile pool name
  
    // Fetch list of tile pools to get a default tilepoolId
    let defaultTilepoolId = 'nouns'; // default to 'nouns'
  
      const response = await fetch(`${server_ip}/tilepools`);
      if (!response.ok) {
      }
      const tilepools = await response.json();
      console.log(tilepools)
      if (tilepools.length > 0) {
        defaultTilepoolId = tilepools[0].id;
      }
      // Use default 'nouns' if fetching tile pools fails
  
    // Store defaultTilepoolId for use in fetchBingoCard
    window.defaultTilepoolId = defaultTilepoolId;
  }

  // Function to create a new tile pool via the API
  async function createNewTileset(tileset) {
    // console log to inspect the data
    console.log('Sending new tile pool:', tileset);
  
    try {
      const response = await fetch(`${server_ip}/tilepools`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(tileset)
      });
  
      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`Failed to create tile pool: ${response.status} ${errorText}`);
      }
  
      const data = await response.json();
      alert('Tile pool created successfully!');
      console.log('Created Tile Pool:', data);
  
      currentTilePoolName = data.name; // Set the current tile pool name
  
      // Generate a bingo card using the new tile pool
      fetchBingoCard(data.id);
    } catch (error) {
      console.error('Error:', error);
      alert(`Error creating tile pool: ${error.message}`);
    }
  }
  

})();
