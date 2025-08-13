document.getElementById("registerForm").addEventListener("submit", async function (e) {
    e.preventDefault();
  
    const username = document.getElementById("username").value;
    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;
    const message = document.getElementById("message");
  
    try {
      const res = await fetch("https://nhkdqrpw-8000.asse.devtunnels.ms/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, email, password }),
      });
  
      const data = await res.json();
  
      if (res.ok) {
        alert("Registrasi berhasil!");
        window.location.href = "login.html"; // arahkan ke halaman home setelah login berhasil
      } else {
        alert("Registrasi Gagal")
        message.textContent = data.detail || "daftar gagal";
      }
    } catch (err) {
      message.textContent = "Gagal terhubung ke server";
    }
  });
  