const config = {
    backendUrl: window.location.hostname === 'localhost' 
        ? 'http://localhost:8000'
        : 'https://chatapp-backend.onrender.com',
    wsUrl: window.location.hostname === 'localhost'
        ? 'ws://localhost:8000'
        : 'wss://chatapp-backend.onrender.com'
}; 