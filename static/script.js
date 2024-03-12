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