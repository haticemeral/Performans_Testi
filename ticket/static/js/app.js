// POSTER RESİMLERİ
const posters = {
    "Duman": "/static/images/duman.jpg",
    "Adamlar": "/static/images/adamlar.jpg",
    "Yüzyüzeyken Konuşuruz": "/static/images/yyk.jpg",
    "Manifest": "/static/images/manifest.jpg",
    "Dedublüman": "/static/images/dedubluman.jpg",
    "Göksel": "/static/images/goksel.jpg"
};

// TOAST BİLDİRİM FONKSİYONU
function showToast(message, type = 'success') {
    const container = document.getElementById('toastContainer') || createToastContainer();

    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };

    const toast = document.createElement('div');
    toast.className = `custom-toast ${type}`;
    toast.innerHTML = `
        <span class="toast-icon">${icons[type]}</span>
        <span class="toast-message">${message}</span>
        <button class="toast-close" onclick="this.parentElement.remove()">×</button>
    `;

    container.appendChild(toast);

    // 3 saniye sonra otomatik kapat
    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toastContainer';
    container.className = 'toast-container';
    document.body.appendChild(container);
    return container;
}

// ETKİNLİKLERİ YÜKLE
function loadEvents() {
    fetch('/api/events')
        .then(res => res.json())
        .then(events => {
            let html = "";

            if (events.length === 0) {
                html = `
                    <div class="col-12 text-center">
                        <div class="alert alert-info">
                            <h4>Henüz etkinlik eklenmemiş</h4>
                            <p>Lütfen daha sonra tekrar kontrol edin.</p>
                        </div>
                    </div>
                `;
            } else {
                events.forEach(e => {
                    let img = posters[e.name] || "/static/images/dedubluman.jpg";

                    html += `
                    <div class="col-md-4 mb-4">
                        <div class="concert-card">
                            <button class="fav-btn" onclick="addFavorite(${e.id}, this)" title="Favorilere Ekle">
                                ♡
                            </button>
                            <img src="${img}" class="poster" alt="${e.name}">

                            <div class="p-3">
                                <h5 class="fw-bold mb-2">${e.name}</h5>
                                <p class="text-muted mb-1" style="font-size: 14px;">📍 ${e.location}</p>
                                <p class="text-muted mb-2" style="font-size: 14px;">📅 ${e.date}</p>
                                <p class="fw-semibold mb-3" style="font-size: 14px;">🎫 Kalan: ${e.stock} bilet</p>

                                <a href="/event/${e.id}" class="btn btn-primary w-100">Bilet Al</a>
                            </div>
                        </div>
                    </div>`;
                });
            }

            document.getElementById("eventList").innerHTML = html;
        })
        .catch(err => {
            console.error('Etkinlikler yüklenirken hata:', err);
            showToast('Etkinlikler yüklenemedi', 'error');
        });
}

// GİRİŞ YAP
function login() {
    const username = document.getElementById("loginUser").value.trim();
    const password = document.getElementById("loginPass").value;

    if (!username || !password) {
        showToast('Lütfen tüm alanları doldurun', 'warning');
        return;
    }

    fetch("/api/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    })
        .then(r => r.json())
        .then(data => {
            if (data.error) {
                showToast(data.error, 'error');
            } else {
                showToast(data.message, 'success');
                setTimeout(() => window.location.href = "/", 1000);
            }
        })
        .catch(err => {
            console.error('Giriş hatası:', err);
            showToast('Bir hata oluştu', 'error');
        });
}

// KAYIT OL
function registerUser() {
    const username = document.getElementById("regUser").value.trim();
    const password = document.getElementById("regPass").value;
    const password2 = document.getElementById("regPass2").value;

    if (!username || !password || !password2) {
        showToast('Lütfen tüm alanları doldurun', 'warning');
        return;
    }

    if (password !== password2) {
        showToast('Şifreler uyuşmuyor', 'error');
        return;
    }

    if (password.length < 4) {
        showToast('Şifre en az 4 karakter olmalıdır', 'warning');
        return;
    }

    fetch("/api/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
    })
        .then(r => r.json())
        .then(data => {
            if (data.error) {
                showToast(data.error, 'error');
            } else {
                showToast(data.message, 'success');
                setTimeout(() => window.location.href = "/login", 1000);
            }
        })
        .catch(err => {
            console.error('Kayıt hatası:', err);
            showToast('Bir hata oluştu', 'error');
        });
}

// FAVORİYE EKLE - GİRİŞ KONTROLÜ İLE
function addFavorite(eventId, button) {
    fetch("/api/favorites/add", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ event_id: eventId })
    })
        .then(r => r.json())
        .then(data => {
            if (data.error) {
                if (data.error.includes("Giriş yapmanız gerekiyor")) {
                    showToast('Favori eklemek için giriş yapmalısınız', 'warning');
                    setTimeout(() => window.location.href = "/login", 1500);
                } else {
                    showToast(data.error, 'error');
                }
            } else {
                showToast(data.message, 'success');
                button.innerHTML = '♥';
                button.classList.add("active");
                button.style.pointerEvents = "none";
            }
        })
        .catch(err => {
            console.error('Favori ekleme hatası:', err);
            showToast('Bir hata oluştu', 'error');
        });
}

// BİLET SATIN AL - GİRİŞ KONTROLÜ İLE
function buyTicket(eventId) {
    // Önce kullanıcı giriş yapmış mı kontrol et
    fetch('/api/favorites')
        .then(r => r.json())
        .then(data => {
            if (data.error && data.error.includes("Giriş yapmanız gerekiyor")) {
                showToast('Bilet almak için giriş yapmalısınız', 'warning');
                setTimeout(() => window.location.href = "/login", 1500);
                return;
            }

            // Giriş yapılmışsa bilet al
            fetch(`/api/buy/${eventId}`, { method: 'POST' })
                .then(r => r.json())
                .then(data => {
                    if (data.error) {
                        showToast(data.error, 'error');
                    } else {
                        showToast(data.message, 'success');
                        const stockDisplay = document.getElementById('stockDisplay');
                        if (stockDisplay) {
                            stockDisplay.textContent = data.kalan;
                        }
                    }
                })
                .catch(err => {
                    console.error(err);
                    showToast('Bir hata oluştu', 'error');
                });
        });
}

// Enter tuşu ile giriş/kayıt
document.addEventListener('DOMContentLoaded', function () {
    const loginUser = document.getElementById("loginUser");
    const loginPass = document.getElementById("loginPass");

    if (loginUser && loginPass) {
        loginPass.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                login();
            }
        });
    }

    const regPass2 = document.getElementById("regPass2");

    if (regPass2) {
        regPass2.addEventListener('keypress', function (e) {
            if (e.key === 'Enter') {
                registerUser();
            }
        });
    }
});