const startBtn = document.getElementById('startBtn');
const gameImage = document.getElementById('gameImage');
const guessInput = document.getElementById('guessInput');
const submitBtn = document.getElementById('submitBtn');
const result = document.getElementById('result');
const countdown = document.getElementById('countdown');
const nextBtn = document.getElementById('nextBtn');
const score = document.getElementById('score');




let currentImage = 0;
const correctAnswers = [];
let correctGuesses = 0;
let incorrectGuesses = 0;
let gameInProgress = false;
const totalImages = 10;
let countdownTimer; // Declare a variable to hold the countdown timer
//let number = 0;

startBtn.addEventListener('click', startGame);
submitBtn.addEventListener('click', checkGuess);
//nextBtn.addEventListener('click', nextImage);

// static/script.js

async function generatePlate() {
    number = Math.floor(Math.random() * 99) + 1;
    imageIndex = correctAnswers.length;
    getCorrectAnswer(number, imageIndex);

    const response = await fetch('https://cbsite.onrender.com/generate_plate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ number: number })
    });

    if (response.ok) {
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        const img = gameImage;
        await new Promise((resolve, reject) => {
            img.onload = resolve; // When the image loads, resolve the promise
            img.onerror = reject; // If there is an error, reject the promise

            img.src = url;
            img.style.display = 'block'; // Ensure image is visible
        });
    } else {
        alert('Failed to generate Ishihara plate');
    }
}
//Function Above is to send the script the info



function startGame() {
    startBtn.disabled = true;
    gameInProgress = true;
    loadNextImage();
}

async function loadNextImage() {
    await generatePlate();
    // Clear any existing countdown timer before starting a new one
    clearInterval(countdownTimer);

    //gameImage.src = images[currentImage];
    guessInput.value = '';
    result.textContent = '';
    countdown.textContent = '10';
    countdown.style.color = 'black';

    // Slow down the countdown timer by changing the interval to 1000 milliseconds (1 second)
    countdownTimer = setInterval(updateCountdown, 1000);
}

function updateCountdown() {
    let remainingTime = parseInt(countdown.textContent);
    console.log("Remaining time: ", remainingTime);
    if (remainingTime > 0) {
        countdown.textContent = (remainingTime - 1).toString();
    } else {
        //clearInterval(countdownTimer);
        checkGuess();
    }
}
// Add an event listener to the guessInput element to listen for the Enter key press
guessInput.addEventListener('keyup', function(event) {
    console.log("Key pressed:", event.key)
    if (event.key === 'Enter') {
        //clearInterval(countdownTimer);
        //console.log("Timer stopped by Enter key press");
        checkGuess();
    }
});


function checkGuess() {
    if (!gameInProgress) {
        return; // Do nothing if the game is not in progress
    }
    
    clearInterval(countdownTimer);
    let userGuess = parseInt(guessInput.value);
    let correctAnswer = correctAnswers[correctAnswers.length - 1];
    

    if (userGuess === correctAnswer) {
        result.textContent = 'Correct!';
        result.classList.remove('d-none', 'alert-danger');
        result.classList.add('alert-success');
        correctGuesses++;
    } else {
        result.textContent = 'Wrong!';
        result.classList.remove('d-none', 'alert-success');
        result.classList.add('alert-danger');
        incorrectGuesses++;
    }

    setTimeout(() => {

    // Deduct one point for each incorrect guess
    if (incorrectGuesses > 0) {
        correctGuesses = Math.max(0, correctGuesses);
    }

    if(parseInt(countdown.textContent) == 0){
        submitBtn.disabled = true;
       // nextBtn.style.display = 'block';
        updateScore();
        

    }

    submitBtn.disabled = true;
   // nextBtn.style.display = 'block';
    updateScore();
    nextImage();
    

   ;
}, 2000);}



function updateScore() {
    score.textContent = `Score: ${correctGuesses} out of ${totalImages}`;
}

async function nextImage() {
    currentImage++;
    if (currentImage <= 10) {
        await loadNextImage();
        submitBtn.disabled = false;
        //nextBtn.style.display = 'none';
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


function getCorrectAnswer(val, imageIndex) {
    correctAnswers[imageIndex] = val;
    console.log("value of val", val);
    console.log("Updated correctAnswers array:", correctAnswers);

    if (imageIndex >= 0 && imageIndex < correctAnswers.length) {
        return correctAnswers[imageIndex];
    } else {
        return 0;
    }
}




