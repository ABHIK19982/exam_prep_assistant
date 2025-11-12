const messagesContainer = document.getElementById('messagesContainer');
const chatForm = document.getElementById('chatForm');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const recentMessagesContainer = document.getElementById('recentMessages');

let userMessages = [];

function createTypingIndicator() {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message ai-message';
    messageDiv.id = 'typingIndicator';

    const bubbleDiv = document.createElement('div');
    bubbleDiv.className = 'message-bubble';

    const typingDiv = document.createElement('div');
    typingDiv.className = 'typing-indicator';

    for (let i = 0; i < 3; i++) {
        const dot = document.createElement('div');
        dot.className = 'dot';
        typingDiv.appendChild(dot);
    }

    bubbleDiv.appendChild(typingDiv);
    messageDiv.appendChild(bubbleDiv);

    return messageDiv;
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) {
        indicator.remove();
    }
}

function createMessageElement(message, isUser) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${isUser ? 'user-message' : 'ai-message'}`;

    const bubbleDiv = document.createElement('div');
    bubbleDiv.className = 'message-bubble';

    if (isUser) {
        const textP = document.createElement('p');
        textP.textContent = message;
        bubbleDiv.appendChild(textP);
    } else {
        bubbleDiv.innerHTML = marked.parse(message);
    }

    messageDiv.appendChild(bubbleDiv);

    return messageDiv;
}

function scrollToBottom() {
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function autoResizeTextarea() {
    messageInput.style.height = 'auto';
    const newHeight = Math.min(messageInput.scrollHeight, 150);
    messageInput.style.height = newHeight + 'px';
}

function updateRecentMessages(message) {
    userMessages.unshift(message);

    if (userMessages.length > 5) {
        userMessages = userMessages.slice(0, 5);
    }

    recentMessagesContainer.innerHTML = '';

    if (userMessages.length === 0) {
        const emptyState = document.createElement('p');
        emptyState.className = 'empty-state';
        emptyState.textContent = 'No messages yet';
        recentMessagesContainer.appendChild(emptyState);
    } else {
        userMessages.forEach((msg) => {
            const messageItem = document.createElement('div');
            messageItem.className = 'recent-message-item';

            const messageText = document.createElement('p');
            messageText.textContent = msg;

            messageItem.appendChild(messageText);
            recentMessagesContainer.appendChild(messageItem);
        });
    }
}

async function sendMessage(message) {
    try {
        sendButton.disabled = true;

        updateRecentMessages(message);

        const userMessageElement = createMessageElement(message, true);
        messagesContainer.appendChild(userMessageElement);
        scrollToBottom();

        const typingIndicator = createTypingIndicator();
        messagesContainer.appendChild(typingIndicator);
        scrollToBottom();

        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: message })
        });

        removeTypingIndicator();

        if (!response.ok) {
            throw new Error('Failed to send message');
        }

        const data = await response.json();

        const aiMessageElement = createMessageElement(data.ai_response.message, false);
        messagesContainer.appendChild(aiMessageElement);
        scrollToBottom();

    } catch (error) {
        console.error('Error sending message:', error);

        removeTypingIndicator();

        const errorMessageElement = createMessageElement(
            "Sorry. Due to some technical issues i am not able to respond to your question now. ",
            false
        );
        messagesContainer.appendChild(errorMessageElement);
        scrollToBottom();
    } finally {
        sendButton.disabled = false;
    }
}

chatForm.addEventListener('submit', (e) => {
    e.preventDefault();

    const message = messageInput.value.trim();

    if (message) {
        sendMessage(message);
        messageInput.value = '';
        messageInput.style.height = 'auto';
        messageInput.focus();
    }
});

messageInput.addEventListener('input', autoResizeTextarea);

messageInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        chatForm.dispatchEvent(new Event('submit'));
    }
});

scrollToBottom();
