const messagesContainer = document.getElementById('messagesContainer');
const chatForm = document.getElementById('chatForm');
const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const recentMessagesContainer = document.getElementById('recentMessages');
const modelSelect = document.getElementById('modelSelect');

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

            const messageButton = document.createElement('button');
            messageButton.type = 'button';
            messageButton.className = 'recent-message-button';
            messageButton.textContent = msg;
            messageButton.addEventListener('click', () => {
                messageInput.value = msg;
                autoResizeTextarea();
                messageInput.focus();
            });

            messageItem.appendChild(messageButton);
            recentMessagesContainer.appendChild(messageItem);
        });
    }
}

function getPlainTextFromMarkdown(markdown) {
    if (!markdown) return '';
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = marked.parse(markdown);
    return tempDiv.textContent || tempDiv.innerText || '';
}

function countWords(text) {
    if (!text) return 0;
    return text.trim().split(/\s+/).filter(Boolean).length;
}

function attachDownloadButton(messageElement, markdown, timestamp) {
    const plainText = getPlainTextFromMarkdown(markdown);
    if (countWords(plainText) <= 500) {
        return;
    }

    const downloadContainer = document.createElement('div');
    downloadContainer.className = 'download-container';

    const downloadButton = document.createElement('button');
    downloadButton.type = 'button';
    downloadButton.className = 'download-button';
    downloadButton.textContent = 'Download response (.txt)';
    downloadButton.addEventListener('click', () => {
        const blob = new Blob([plainText], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        const safeTimestamp = timestamp ? timestamp.replace(/[:.]/g, '-') : Date.now();
        link.download = `response-${safeTimestamp}.txt`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        setTimeout(() => URL.revokeObjectURL(url), 1000);
    });

    downloadContainer.appendChild(downloadButton);
    messageElement.appendChild(downloadContainer);
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

        const payload = { message };
        if (modelSelect && modelSelect.value) {
            payload.model = modelSelect.value;
        }

        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(payload)
        });

        removeTypingIndicator();

        if (!response.ok) {
            throw new Error('Failed to send message');
        }

        const data = await response.json();

        const aiMessageElement = createMessageElement(data.ai_response.message, false);
        messagesContainer.appendChild(aiMessageElement);
        attachDownloadButton(aiMessageElement, data.ai_response.message, data.ai_response.timestamp);
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
