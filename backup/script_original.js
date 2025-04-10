const startBtn = document.getElementById('startBtn');
const gameImage = document.getElementById('gameImage');
const guessInput = document.getElementById('guessInput');
const submitBtn = document.getElementById('submitBtn');
const result = document.getElementById('result');
const countdown = document.getElementById('countdown');
const nextBtn = document.getElementById('nextBtn');
const score = document.getElementById('score');

let images = [
    'images/10.jpg', 'images/8.jpg', 'images/15.jpg', 'images/6.webp', 'images/7.webp',
    'images/45.webp', 'images/26.webp', 'images/74.png', 'images/8.jpg', 'images/15.jpg'
]; // Add your image URLs here
let currentImage = 0;
let correctGuesses = 0;
let incorrectGuesses = 0;
let gameInProgress = false;
const totalImages = images.length;
let countdownTimer; // Declare a variable to hold the countdown timer

startBtn.addEventListener('click', startGame);
submitBtn.addEventListener('click', checkGuess);
nextBtn.addEventListener('click', nextImage);

function startGame() {
    startBtn.disabled = true;
    gameInProgress = true;
    loadNextImage();
}

function loadNextImage() {
    // Clear any existing countdown timer before starting a new one
    clearInterval(countdownTimer);

    gameImage.src = images[currentImage];
    guessInput.value = '';
    result.textContent = '';
    countdown.textContent = '10';
    countdown.style.color = 'black';

    // Slow down the countdown timer by changing the interval to 1000 milliseconds (1 second)
    countdownTimer = setInterval(updateCountdown, 1000);
}

function updateCountdown() {
    let remainingTime = parseInt(countdown.textContent);
    if (remainingTime > 0) {
        countdown.textContent = (remainingTime - 1).toString();
    } else {
        clearInterval(countdownTimer);
        checkGuess();
    }
}
// Add an event listener to the guessInput element to listen for the Enter key press
guessInput.addEventListener('keyup', function(event) {
    if (event.key === 'Enter') {
        checkGuess();
    }
});

function checkGuess() {
    if (!gameInProgress) {
        return; // Do nothing if the game is not in progress
    }

    let userGuess = parseInt(guessInput.value);
    let correctAnswer = getCorrectAnswer(currentImage);

    if (userGuess === correctAnswer) {
        result.textContent = 'Correct!';
        result.style.color = 'green';
        correctGuesses++;
    } else {
        result.textContent = 'Wrong!';
        result.style.color = 'red';
        incorrectGuesses++;
    }

    // Deduct one point for each incorrect guess
    if (incorrectGuesses > 0) {
        correctGuesses = Math.max(0, correctGuesses);
    }

    submitBtn.disabled = true;
    nextBtn.style.display = 'block';
    updateScore();

   ;
}



function updateScore() {
    score.textContent = `Score: ${correctGuesses} out of ${totalImages}`;
}

function nextImage() {
    currentImage++;
    if (currentImage < images.length) {
        loadNextImage();
        submitBtn.disabled = false;
        nextBtn.style.display = 'none';
    } else {
        endGame();
    }
}

function endGame() {
    gameInProgress = false;
    gameImage.src = '';
    guessInput.style.display = 'none';
    submitBtn.style.display = 'none';
    countdown.style.display = 'none';

    // Clear the countdown timer when the game ends
    clearInterval(countdownTimer);

    score.textContent = `Score: ${correctGuesses} out of ${totalImages}`;
    
  // Redirect to the score page with the player's score as a parameter
const scorePageURL = `score.html?score=${correctGuesses}`;
window.location.href = scorePageURL;

}


function getCorrectAnswer(imageIndex) {
    const correctAnswers = [10, 8, 15, 6, 7, 45, 26, 74, 8, 15]; // Example answers for each image

    if (imageIndex >= 0 && imageIndex < correctAnswers.length) {
        return correctAnswers[imageIndex];
    } else {
        return 0;
    }
}


