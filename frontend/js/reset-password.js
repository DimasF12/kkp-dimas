document.getElementById("resetForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  const email = document.getElementById("email").value;
  const newPassword = document.getElementById("newPassword").value;
  const confirmPassword = document.getElementById("confirmPassword").value;

  if (newPassword !== confirmPassword) {
    alert("Password tidak cocok!");
    return;
  }

  // if (newPassword.length < 8) {
  //   alert("Password baru minimal 8 karakter!"); 
  //   return;
  // }

  try {
    const response = await fetch("/auth/reset-password-langsung", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, new_password: newPassword }),
    });

    if (response.ok) {
      alert("Password berhasil diubah!");
      setTimeout(() => {
        window.location.href = "login.html";
      }, 1500);
    } else {
      const res = await response.json();
      alert(res.detail || "Terjadi kesalahan.");
    }
  } catch (err) {
    alert("Gagal menghubungi server.");
  }
});

document.getElementById("backToLoginBtn").addEventListener("click", function() {
    window.location.href = "login.html";
});