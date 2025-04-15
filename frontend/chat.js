let currentChatUser = null;
let ws = null;
const userId = localStorage.getItem('user_id');

if (!userId) {
    window.location.href = 'index.html';
}

// Initialize WebSocket connection
function initializeWebSocket() {
    ws = new WebSocket(`ws://localhost:8000/ws/${userId}`);
    
    ws.onopen = () => {
        console.log('WebSocket connected');
    };
    
    ws.onmessage = (event) => {
        try {
            const message = JSON.parse(event.data);
            console.log('Received message:', message);
            
            // Display message if it's part of the current chat
            if (currentChatUser && 
                (message.sender_id === currentChatUser.id || 
                 message.receiver_id === currentChatUser.id)) {
                displayMessage(message);
            }
            
            // Update recent chats
            updateRecentChats();
        } catch (error) {
            console.error('Error processing message:', error);
        }
    };

    ws.onclose = () => {
        console.log('WebSocket disconnected. Reconnecting...');
        setTimeout(initializeWebSocket, 2000);
    };

    ws.onerror = (error) => {
        console.error('WebSocket error:', error);
    };
}

// Search users function
async function searchUsers(query) {
    const searchResults = document.getElementById('searchResults');
    
    if (!query.trim()) {
        searchResults.style.display = 'none';
        return;
    }

    try {
        const response = await fetch(`http://localhost:8000/users/search?query=${query}`);
        const users = await response.json();
        
        searchResults.innerHTML = '';
        users.forEach(user => {
            if (user.id !== userId) {
                const div = document.createElement('div');
                div.className = 'search-result-item';
                div.textContent = user.username;
                div.onclick = () => selectUser(user);
                searchResults.appendChild(div);
            }
        });
        
        searchResults.style.display = users.length ? 'block' : 'none';
    } catch (error) {
        console.error('Error searching users:', error);
    }
}

// Select user to chat with
async function selectUser(user) {
    currentChatUser = user;
    
    // Update UI
    document.getElementById('searchResults').style.display = 'none';
    document.getElementById('userSearchInput').value = '';
    document.getElementById('chatHeader').innerHTML = `<h3>${user.username}</h3>`;
    document.getElementById('messagesList').innerHTML = '';
    
    // Load chat history
    await loadChatHistory();
}

// Load chat history
async function loadChatHistory() {
    if (!currentChatUser) return;
    
    try {
        const response = await fetch(`http://localhost:8000/messages/${userId}/${currentChatUser.id}`);
        if (!response.ok) {
            throw new Error('Failed to load chat history');
        }
        
        const messages = await response.json();
        
        const messagesList = document.getElementById('messagesList');
        messagesList.innerHTML = '';
        
        messages.forEach(message => {
            displayMessage(message);
        });
        
        messagesList.scrollTop = messagesList.scrollHeight;
    } catch (error) {
        console.error('Error loading chat history:', error);
        alert('Failed to load chat history. Please refresh the page.');
    }
}

// Display message function
function displayMessage(message) {
    const messagesList = document.getElementById('messagesList');
    const div = document.createElement('div');
    
    div.className = `message ${message.sender_id === userId ? 'sent' : 'received'}`;
    
    // Create message content
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.textContent = message.content;
    
    // Create timestamp
    const timeDiv = document.createElement('div');
    timeDiv.className = 'message-time';
    const messageTime = new Date(message.timestamp);
    timeDiv.textContent = messageTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    
    div.appendChild(contentDiv);
    div.appendChild(timeDiv);
    
    messagesList.appendChild(div);
    messagesList.scrollTop = messagesList.scrollHeight;
}

// Send message function
function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();
    
    if (!message || !currentChatUser || !ws || ws.readyState !== WebSocket.OPEN) {
        console.log('Cannot send message:', {
            hasMessage: !!message,
            hasCurrentUser: !!currentChatUser,
            hasWs: !!ws,
            wsState: ws ? ws.readyState : 'no ws'
        });
        return;
    }
    
    const messageData = {
        sender_id: userId,
        receiver_id: currentChatUser.id,
        content: message,
        timestamp: new Date().toISOString()
    };
    
    try {
        ws.send(JSON.stringify(messageData));
        input.value = '';
    } catch (error) {
        console.error('Error sending message:', error);
        alert('Failed to send message. Please try again.');
    }
}

// Handle Enter key press
function handleKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

// Update recent chats
async function updateRecentChats() {
    try {
        const response = await fetch(`http://localhost:8000/recent-chats/${userId}`);
        const recentChats = await response.json();
        
        const recentChatsDiv = document.getElementById('recentChats');
        recentChatsDiv.innerHTML = '';
        
        recentChats.forEach(chat => {
            const div = document.createElement('div');
            div.className = 'chat-item';
            div.textContent = chat.username;
            div.onclick = () => selectUser(chat);
            recentChatsDiv.appendChild(div);
        });
    } catch (error) {
        console.error('Error updating recent chats:', error);
    }
}

// Initial load of recent chats
updateRecentChats();

// Initialize the WebSocket connection
initializeWebSocket();

// Add event listeners
document.getElementById('messageInput').addEventListener('keypress', handleKeyPress); 