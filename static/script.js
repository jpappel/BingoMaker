// script.js

let savedCardsModal;
let createTilesetModal;
let editModal;
let currentTilePoolName = null; 

(function () {
  // Wait for the DOM to fully load before running scripts
  document.addEventListener('DOMContentLoaded', async () => {
    await initPage();

    function login() {
      window.location.href = `${cognito_ip}/login`;
    }
    document.getElementById('login-btn').addEventListener('click', login);

    // Initialize Bootstrap modals
    const createTilesetModalElement = document.getElementById('createTilesetModal');
    if (createTilesetModalElement) {
      createTilesetModal = new bootstrap.Modal(createTilesetModalElement);
    }

    const editModalElement = document.getElementById('modal');
    if (editModalElement) {
      editModal = new bootstrap.Modal(editModalElement);
    }

    const savedCardsModalElement = document.getElementById('saved-cards-modal');
    if (savedCardsModalElement) {
      savedCardsModal = new bootstrap.Modal(savedCardsModalElement);
    }
    const createBtn = document.getElementById('create-btn');
    if (createBtn) {
      createBtn.addEventListener('click', () => {
        editModal.show();
      });
    }
    const editBtn = document.getElementById('edit-btn');
    if (editBtn) {
      editBtn.addEventListener('click', () => {
        editModal.show();
      });
    }
    const saveBtn = document.getElementById('save-btn');
    if (saveBtn) {
      saveBtn.addEventListener('click', () => {
        saveWords();
        editModal.hide();
      });
    }
    const createTilesetForm = document.getElementById('createTilesetForm');
    if (createTilesetForm) {
      createTilesetForm.addEventListener('submit', async (event) => {
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
    }

    const printBtn = document.getElementById('print-btn');
    if (printBtn) {
      printBtn.addEventListener('click', () => {
        window.print();
      });
    }

    const viewSavedBtn = document.getElementById('view-saved-btn');
    if (viewSavedBtn) {
      viewSavedBtn.addEventListener('click', () => {
        displaySavedCards(); 
        savedCardsModal.show();
      });
    }
    const saveCardBtn = document.getElementById('save-card-btn');
    if (saveCardBtn) {
      saveCardBtn.addEventListener('click', () => {
        saveCurrentBingoCard();
      });
    }

    const bingoBoard = document.getElementById('bingo-board');
    if (bingoBoard) {
      bingoBoard.addEventListener('click', (event) => {
        const cell = event.target;
        if (cell.classList.contains('bingo-cell')) {
          cell.classList.toggle('marked');
          checkBingoWin();
        }
      });
    }
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


  // Function to save words from the modal input and update the bingo card
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
  
      const response = await fetch(`https://nas8lsehb7.execute-api.us-east-1.amazonaws.com/test/tilesets`,
      );
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

  function checkBingoWin() {
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

  function displayWinMessage() {
    alert('BINGO! You have a winning card!');
  }

  async function fetchBingoCard(tilepoolId) {
    tilepoolId = tilepoolId || window.defaultTilepoolId || 'nouns';
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