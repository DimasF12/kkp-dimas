function checkAuth() {
    const token = localStorage.getItem("token");
    if (!token) {
      alert("Silakan login terlebih dahulu!");
      window.location.href = "login.html";
    }
}
// Logout function
function logout() {
  localStorage.removeItem("token");
  alert("Logout berhasil!");
  window.location.href = "login.html";
}
  
function calculator() {
  window.location.href='calculator.html';
}
function moneyTracker() {
  window.location.href='index.html';
}
function danaDarurat(){
  window.location.href='dandur.html';
}
function danaPensiun(){
  window.location.href='danpen.html';
}
function barangImpian(){
  window.location.href='barangimpian.html';
}