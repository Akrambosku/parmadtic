# PARMADTIC - Spaceman Game (Django Edition)

Game crash multiplier bertema luar angkasa (Spaceman) interaktif yang dilengkapi dengan sistem akun, riwayat taruhan, deposit/withdraw, dan fitur customer service. Aplikasi ini dibangun dengan menggunakan **Django** sebagai backend dan **HTML, Vanilla CSS, serta Vanilla JavaScript** di sisi frontend.

---

## 🚀 Fitur Utama

1. **Autentikasi & Akun**:
   - Register akun baru (saldo awal otomatis Rp 1.000,00).
   - Login & Logout aman terintegrasi dengan Django Auth.
2. **Game Spaceman (Crash Game)**:
   - Pasang taruhan sebelum pesawat lepas landas.
   - Multiplier naik secara dinamis secara real-time.
   - Tombol **Cash Out** untuk mencairkan kemenangan sebelum terjadi *Crash*.
3. **Dashboard Pengguna**:
   - **Deposit**: Menambahkan saldo ke akun secara instan.
   - **Withdraw**: Menarik saldo dari akun.
   - **Riwayat Taruhan (Bet History)**: Daftar taruhan yang pernah dipasang beserta status menang/kalah.
   - **Riwayat Transaksi (Transaction History)**: Riwayat setoran dan penarikan dana.
   - **Customer Service**: Form pengajuan tiket bantuan/keluhan kepada admin.
4. **Django Admin Panel**:
   - Panel manajemen untuk mengelola transaksi pengguna, menyetujui transaksi secara manual (jika diperlukan), melihat tiket bantuan, serta memantau statistik game.

---

## 🛠️ Stack Teknologi

- **Backend**: Django (Python) dengan `PyMySQL` untuk konektor MySQL.
- **Frontend**: HTML5, Vanilla CSS (Glassmorphism design), & Vanilla JavaScript.
- **Database**: MySQL / MariaDB (Laragon / XAMPP).

---

## 📥 Panduan Instalasi & Setup

Ikuti langkah-langkah di bawah ini untuk menjalankan aplikasi di komputer lokal Anda:

### 1. Prasyarat
- Pastikan Anda sudah menginstal **Python** (versi 3.10 ke atas direkomendasikan).
- Pastikan MySQL Server Anda aktif (bisa via **Laragon**, **XAMPP**, atau MySQL Standalone).

### 2. Buat Database Baru
Buat database kosong bernama `spaceman_db` di server MySQL Anda:
```sql
CREATE DATABASE spaceman_db;
```

### 3. Masuk ke Direktori Project
Buka terminal (PowerShell / Command Prompt) dan arahkan ke folder project:
```powershell
cd c:\Users\User\Documents\Coding\Codingan
```

### 4. Migrasi Database Django
Jalankan perintah berikut untuk membuat tabel-tabel database yang diperlukan oleh aplikasi:
```powershell
# Jalankan makemigrations
..\.venv\Scripts\python.exe manage.py makemigrations

# Jalankan migrate untuk menerapkan perubahan ke database
..\.venv\Scripts\python.exe manage.py migrate
```

### 5. Membuat Akun Admin (Superuser)
Buat akun administrator agar bisa masuk ke Django Admin Panel:
```powershell
..\.venv\Scripts\python.exe manage.py createsuperuser
```
*Ikuti instruksi di layar untuk mengisi username, email, dan password admin.*

### 6. Menjalankan Server
Nyalakan server pengembangan lokal:
```powershell
..\.venv\Scripts\python.exe manage.py runserver
```

Server Anda sekarang berjalan di: **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

---

## 📂 Struktur Folder Utama

```text
Codingan/
├── backend/                  # Pengaturan utama project Django (settings.py, urls.py, wsgi.py)
├── game/                     # Folder Django App untuk logika game utama
│   ├── static/game/          # File static frontend (style.css, script.js)
│   ├── templates/game/       # Template HTML (base, login, register, dashboard, index)
│   ├── admin.py              # Konfigurasi halaman Django Admin
│   ├── models.py             # Definisi skema database (UserProfile, Bet, Transaction, Ticket)
│   ├── urls.py               # Rute routing URL untuk app game
│   └── views.py              # Logika backend & API endpoint game
├── manage.py                 # File entry point Django command-line
└── README.md                 # Dokumentasi project (file ini)
```

---

## 🔗 Rute URL Aplikasi

Setelah server menyala, Anda dapat mengakses URL berikut:
- **Halaman Utama Game**: `http://127.0.0.1:8000/` *(membutuhkan login)*
- **Login Akun**: `http://127.0.0.1:8000/login/`
- **Register Akun**: `http://127.0.0.1:8000/register/`
- **Dashboard & Fitur Akun**: `http://127.0.0.1:8000/dashboard/`
- **Admin Panel**: `http://127.0.0.1:8000/admin/`
