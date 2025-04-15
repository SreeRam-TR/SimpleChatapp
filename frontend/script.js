async function login() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
  
    try {
        const res = await fetch(`${config.backendUrl}/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password })
        });
  
        const data = await res.json();
        if (res.ok) {
            localStorage.setItem("user_id", data.user_id);
            window.location.href = "chat.html";
        } else {
            alert(data.detail);
        }
    } catch (error) {
        console.error('Login error:', error);
        alert('Failed to connect to server. Please try again.');
    }
}
  
async function signup() {
    const username = document.getElementById("newUsername").value;
    const email = document.getElementById("email").value;
    const password = document.getElementById("newPassword").value;
  
    try {
        const res = await fetch(`${config.backendUrl}/signup`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, email, password })
        });
  
        const data = await res.json();
        if (res.ok) {
            alert("Signup successful! Please login.");
        } else {
            alert(data.detail);
        }
    } catch (error) {
        console.error('Signup error:', error);
        alert('Failed to connect to server. Please try again.');
    }
}