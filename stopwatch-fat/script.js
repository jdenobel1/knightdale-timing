let audioContext = new (window.AudioContext || window.webkitAudioContext)();
let analyser = audioContext.createAnalyser();
let microphoneStream;
let isListening = true;
let startTime, timerInterval;
let stopwatchRunning = false;
let loggedTimes = [];
let mediaRecorder;
let recordedChunks = [];
let stopwatchColor = "#ff0000";
let bookmarks = [];
let frameRate = 60;

const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
const videoElement = document.createElement('video');
videoElement.autoplay = true;
videoElement.muted = true;

navigator.mediaDevices.getUserMedia({ video: true, audio: true }).then(stream => {
    videoElement.srcObject = stream;
    setupAudioProcessing(stream);
    startCanvasRendering();
    setupRecorder(stream);
}).catch(error => console.error('Error accessing media:', error));

function setupAudioProcessing(stream) {
    microphoneStream = audioContext.createMediaStreamSource(stream);
    microphoneStream.connect(analyser);
    analyser.fftSize = 256;
    checkNoiseLevel();
}

function checkNoiseLevel() {
    let dataArray = new Uint8Array(analyser.frequencyBinCount);
    function analyze() {
        analyser.getByteFrequencyData(dataArray);
        let average = getAverageVolume(dataArray);
        document.getElementById('status').innerText = `Noise Level: ${average.toFixed(2)} dB`;
        if (average > 90 && !stopwatchRunning) {
            startStopwatch();
        }
        requestAnimationFrame(analyze);
    }
    analyze();
}

function getAverageVolume(array) {
    let values = 0;
    for (let i = 0; i < array.length; i++) {
        values += array[i];
    }
    return values / array.length;
}

document.getElementById('colorPicker').addEventListener('input', event => {
    stopwatchColor = event.target.value;
});

function startCanvasRendering() {
    function render() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(videoElement, 0, 0, canvas.width, canvas.height);
        ctx.font = '32px Arial';
        ctx.fillStyle = stopwatchColor;
        ctx.fillText(getCurrentStopwatchTime(), 10, 40);
        setTimeout(() => requestAnimationFrame(render), 1000 / frameRate);
    }
    render();
}

function getCurrentStopwatchTime() {
    if (!startTime) return '00:00:00.000';
    let elapsedTime = Date.now() - startTime;
    let milliseconds = (elapsedTime % 1000).toString().padStart(3, '0');
    let seconds = Math.floor((elapsedTime / 1000) % 60).toString().padStart(2, '0');
    let minutes = Math.floor((elapsedTime / (1000 * 60)) % 60).toString().padStart(2, '0');
    let hours = Math.floor(elapsedTime / (1000 * 60 * 60)).toString().padStart(2, '0');
    return `${hours}:${minutes}:${seconds}.${milliseconds}`;
}

function startStopwatch() {
    if (stopwatchRunning) return;
    startTime = Date.now();
    stopwatchRunning = true;
}

function resetStopwatch() {
    stopwatchRunning = false;
    startTime = null;
    bookmarks = [];
}

document.getElementById('startButton').addEventListener('click', startStopwatch);
document.getElementById('resetButton').addEventListener('click', resetStopwatch);

document.addEventListener('keydown', event => {
    if (event.code === 'Space') {
        logTime();
        addBookmark();
    } else if (event.ctrlKey && event.shiftKey) {
        downloadLoggedTimes();
    }
});

function logTime() {
    let currentTime = getCurrentStopwatchTime();
    loggedTimes.push(currentTime);
    let timeList = document.getElementById('timeList');
    let li = document.createElement('li');
    li.textContent = `${loggedTimes.length}. ${currentTime}`;
    timeList.appendChild(li);
}

function addBookmark() {
    let currentTime = getCurrentStopwatchTime();
    bookmarks.push(currentTime);
}

function downloadLoggedTimes() {
    let csvContent = 'Place,Time\n';
    loggedTimes.forEach((time, index) => {
        csvContent += `${index + 1},${time}\n`;
    });

    let blob = new Blob([csvContent], { type: 'text/csv' });
    let url = URL.createObjectURL(blob);
    let a = document.createElement('a');
    a.href = url;
    a.download = 'logged_times.csv';
    a.click();
}

function setupRecorder(stream) {
    let combinedStream = new MediaStream();
    let videoStream = canvas.captureStream(frameRate);
    let audioTracks = stream.getAudioTracks();

    videoStream.getVideoTracks().forEach(track => combinedStream.addTrack(track));
    audioTracks.forEach(track => combinedStream.addTrack(track));

    mediaRecorder = new MediaRecorder(combinedStream, { mimeType: 'video/mp4' });
    mediaRecorder.ondataavailable = event => {
        if (event.data.size > 0) recordedChunks.push(event.data);
    };
    mediaRecorder.onstop = downloadVideo;
}

document.getElementById('recordButton').addEventListener('click', () => {
    if (mediaRecorder && mediaRecorder.state === 'inactive') {
        recordedChunks = [];
        mediaRecorder.start();
    }
});

document.getElementById('stopRecordingButton').addEventListener('click', () => {
    if (mediaRecorder && mediaRecorder.state === 'recording') {
        mediaRecorder.stop();
    }
});

function downloadVideo() {
    let blob = new Blob(recordedChunks, { type: 'video/mp4' });
    let url = URL.createObjectURL(blob);
    let a = document.createElement('a');
    a.href = url;
    a.download = 'recorded_video_with_stopwatch.mp4';
    a.click();
}

// Modal functionality
document.getElementById('directionsButton').addEventListener('click', () => {
    document.getElementById('directionsModal').style.display = 'block';
});

document.getElementById('closeModal').addEventListener('click', () => {
    document.getElementById('directionsModal').style.display = 'none';
});
