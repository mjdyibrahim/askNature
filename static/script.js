const chatForm = document.getElementById('chat-form');
const chatBody = document.getElementById('chat-body');

chatForm.addEventListener('submit', (event) => {
    event.preventDefault();
    const messageInput = event.target.elements.message;
    const message = messageInput.value.trim();

    if (message) {
        addMessage('user', message);
        sendMessage(message);
        messageInput.value = '';
    }
});

function addMessage(sender, text) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', `${sender}-message`);
    messageElement.innerHTML = `
	
	        			<div class="${sender}-message-icon">
						    <img src="../static/${sender}.png" alt="${sender} icon">
						</div> 
						<div class="${sender}-message-content">
                                <p>${text}</p>

						</div>
    `;
    chatBody.appendChild(messageElement);
    chatBody.scrollTop = chatBody.scrollHeight;

}

function sendMessage(message) {
    fetch('/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            'message': message
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data && data.message) {
            addMessage('ai', data.message);
        } else {
            console.error('Invalid response from API');
            addMessage('ai', 'Sorry, there was an error with my response. Please try again later.');
        }
    })
    .catch(error => {
        console.error(error);
        addMessage('ai', 'Sorry, there was an error with my response. Please try again later.');
    });
}

// Add code to play the voice output using the Web Speech API
function playVoiceOutput(voiceOutput) {
    let audio = new Audio("data:audio/mp3;base64," + voiceOutput);
    audio.play();
  }
  
  var recognition;

function startDictation() {
    if (window.hasOwnProperty('webkitSpeechRecognition')) {
        recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = "en-US";
        recognition.start();

        recognition.onresult = function(e) {
            const transcript = e.results[0][0].transcript;
            addMessage('user', transcript);
            sendMessage(transcript);
            recognition.stop();
        };

        recognition.onerror = function(e) {
            recognition.stop();
        }
    }
}

function stopDictation() {
    if (recognition) {
        recognition.stop();
        recognition = null;
    }
}

var isVoiceInputEnabled = false;
function toggleVoiceInput() {
    isVoiceInputEnabled = !isVoiceInputEnabled;
    if (isVoiceInputEnabled) {
        startDictation();
    } else {
        stopDictation();
    }
}