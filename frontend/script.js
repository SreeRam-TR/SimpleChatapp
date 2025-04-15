async function login() {
    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
  
    const res = await fetch("http://localhost:8000/login", {
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
  }
  
  async function signup() {
    const username = document.getElementById("newUsername").value;
    const email = document.getElementById("email").value;
    const password = document.getElementById("newPassword").value;
  
    const res = await fetch("http://localhost:8000/signup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username, email, password })
    });
  
    const data = await res.json();
    if (res.ok) {
      alert("Signup successful! Now login.");
    } else {
      alert(data.detail);
    }
  }