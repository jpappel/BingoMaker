// Generate the bingo card on page load with random numbers, 
fetchBingoCard();

// Event listener for the "Edit" button
document.getElementById('edit-btn').addEventListener('click', openModal);

// Event listener for the "Save" button in the modal
document.getElementById('save-btn').addEventListener('click', saveWords);

// Event listener for closing the modal
document.getElementById('close-modal').addEventListener('click', closeModal);

// Event listener for clicking outside the modal content to close it
window.addEventListener('click', outsideClick);

// Event listener for the "Print" button
document.getElementById('print-btn').addEventListener('click', () => {
  window.print();
});


function fetchBingoCard() {
  console.log("Fetching Bingo Card");
  fetch(`/api/v1/bingocard/${Math.floor(Math.random() * 1000)}`)
  .then(response => response.json())
  .then(data => {
    // get data.tiles, and only content from each tile
    return data.tiles.map(tile => tile.content);
  })
  .then (data => {console.log(data); return data;})
  .then (data => generateBingoCard(data));
}

// generates bingo card with random numbers at startup and 
function generateBingoCard(words = []) {
  const bingoCells = document.querySelectorAll('.bingo-cell');

  let items = [];

  if (words.length > 0) {
    items = words;
  } else {
    // Default numbers 1-75
    items = Array.from({ length: 75 }, (_, i) => i + 1).map(String);
  }

  // Shuffle and select 24 items (excluding the center "FREE" cell)
  items = shuffleArray(items).slice(0, 24);

  // Update cells with items
  bingoCells.forEach((cell, index) => {
    // Set center cell as "FREE" , will add an option to change it to a random word later
    if (index === 12) { // Cell 13 (center cell)
      cell.textContent = 'FREE';
    } else {
      // Adjust index to skip the center cell when assigning items
      const itemIndex = index < 12 ? index : index - 1;
      cell.textContent = items[itemIndex];
    }

    // Remove previous event listeners to prevent duplication
    const newCell = cell.cloneNode(true);
    cell.parentNode.replaceChild(newCell, cell);
  });

  // Re-select cells to add event listeners
  document.querySelectorAll('.bingo-cell').forEach(cell => {
    cell.addEventListener('click', () => {
      cell.classList.toggle('marked');
    });
  });
}

// Function to shuffle an array
function shuffleArray(array) {
  return array.sort(() => Math.random() - 0.5);
}

// Function to open the modal dialog
function openModal() {
  document.getElementById('modal').style.display = 'block';
}

// Function to close the modal dialog
function closeModal() {
  document.getElementById('modal').style.display = 'none';
}

// Function to handle clicks outside the modal content
function outsideClick(event) {
  if (event.target == document.getElementById('modal')) {
    closeModal();
  }
}

// Function to save words from the modal input and update the bingo card
function saveWords() {
  const inputText = document.getElementById('modal-input').value.trim();
  if (inputText !== '') {
    // Split input by new lines and trim each word
    const words = inputText.split('\n').map(word => word.trim()).filter(word => word !== '');
    generateBingoCard(words);
  } else {
    // If input is empty, generate with random numbers
    generateBingoCard();
  }
  closeModal();
  document.getElementById('modal-input').value = ''; // Clear the input
}
