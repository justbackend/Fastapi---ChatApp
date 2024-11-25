const ws = new WebSocket(`ws://${window.location.host}/ws/chat`);

const messagesDiv = document.getElementById('messages');
const input = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');

const appendMessage = (message, isOwnMessage) => {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', isOwnMessage ? 'own' : 'other');

    const messageContent = document.createElement('div');
    messageContent.classList.add('message-content');
    messageContent.textContent = message;

    messageDiv.appendChild(messageContent);
    messagesDiv.appendChild(messageDiv);
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
};

ws.onmessage = (event) => {
    appendMessage(event.data, false);
};

sendButton.onclick = () => {
    if (input.value) {
        ws.send(input.value);
        appendMessage(input.value, true);
        input.value = '';
    }
};

input.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && input.value) {
        ws.send(input.value);
        appendMessage(input.value, true);
        input.value = '';
    }
});
