document.getElementById("loginForm").addEventListener("submit", async function (e) {
    e.preventDefault();

    const email = document.getElementById("email").value;
    const password = document.getElementById("password").value;

    try {
        const res = await fetch("http://127.0.0.1:8000/auth/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ email, password }),
            credentials: "include" // Pastikan untuk mengirimkan cookie
        });

        if (!res.ok) {
            throw new Error("Login failed: " + res.statusText);
        }

        // const data = await res.json();
        // console.log("Response from backend:", data);

        // Token sudah disimpan dalam cookie jika login berhasil
        alert("Login berhasil!");
        window.location.href = "index.html"; // Redirect setelah login sukses

    } catch (err) {
        console.error("Error:", err);
        alert("Terjadi kesalahan saat login.");
    }
});
