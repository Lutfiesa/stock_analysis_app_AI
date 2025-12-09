# Setup Guide - Stock Analysis App

Panduan lengkap untuk menginstall dan menjalankan aplikasi analisis saham Indonesia.

## 📋 Prerequisites

Sebelum memulai, pastikan Anda sudah menginstall:

- **Python 3.10 atau lebih tinggi** - [Download Python](https://www.python.org/downloads/)
- **Node.js 16+ dan npm** - [Download Node.js](https://nodejs.org/)
- **Git** (optional) - Untuk version control
- **Text Editor/IDE** - Recommended: VS Code

## 🔑 API Keys Setup

Aplikasi ini memerlukan API key dari Sectors.app atau Twelve Data untuk mengakses data saham IDX.

### Option 1: Sectors.app (Recommended untuk IDX)

1. Kunjungi [sectors.app/api](https://sectors.app/api)
2. Daftar dan dapatkan API key
3. Simpan API key Anda

### Option 2: Twelve Data (Support IDX + Global)

1. Kunjungi [twelvedata.com](https://twelvedata.com)
2. Sign up untuk free tier (800 requests/day)
3. Generate API key dari dashboard
4. Simpan API key Anda

---

## 🚀 Installation Steps

### 1. Navigasi ke Project Directory

```powershell
cd "c:\Users\lutfi\OneDrive\Dokumen\Bug Bounty\stock-analysis-app"
```

### 2. Python Environment Setup

#### Create Virtual Environment

```powershell
python -m venv venv
```

#### Activate Virtual Environment

**Windows:**
```powershell
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

You should see `(venv)` di awal command prompt Anda.

#### Install Python Dependencies

```powershell
pip install -r requirements.txt
```

Ini akan menginstall:
- FastAPI (web framework)
- Uvicorn (ASGI server)
- Pandas & NumPy (data processing)
- Requests (HTTP client)
- SQLAlchemy (database)
- Dan lainnya...

### 3. Frontend Setup

Install Node.js dependencies:

```powershell
npm install
```

Ini akan menginstall:
- Vite (build tool)
- TradingView Lightweight Charts (charting library)

### 4. Environment Configuration

#### Copy Template

```powershell
Copy-Item .env.example .env
```

#### Edit .env File

Buka file `.env` dengan text editor dan masukkan API keys Anda:

```env
# Sectors.app API (untuk IDX data)
SECTORS_API_KEY=your_sectors_api_key_here

# Twelve Data API (optional, sebagai backup)
TWELVEDATA_API_KEY=your_twelvedata_api_key_here
```

**Minimal requirement:** Isi salah satu dari API keys di atas.

#### Konfigurasi Lainnya (Optional)

```env
# Environment
APP_ENV=development
DEBUG=true

# Server Settings
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000
FRONTEND_PORT=5173

# Cache Settings
CACHE_EXPIRATION=3600
ENABLE_CACHE=true

# Logging
LOG_LEVEL=INFO
LOG_API_REQUESTS=true
```

---

## ▶️ Running the Application

Anda perlu menjalankan 2 server secara bersamaan:

### Terminal 1: Backend Server

```powershell
# Ensure virtual environment is activated
venv\Scripts\activate

# Run backend
python backend/api/server.py
```

Anda akan melihat output seperti ini:
```
╔══════════════════════════════════════╗
║   Stock Analysis API Server          ║
║   Indonesia Market (IDX)             ║
╚══════════════════════════════════════╝

🌐 Server: http://127.0.0.1:8000
📚 API Docs: http://127.0.0.1:8000/docs
```

Backend server sekarang berjalan di **http://127.0.0.1:8000**

### Terminal 2: Frontend Server

Buka terminal/PowerShell baru:

```powershell
# Run frontend
npm run dev
```

Output:
```
VITE v5.0.11  ready in 234 ms

➜  Local:   http://localhost:5173/
➜  Network: use --host to expose
```

Frontend sekarang berjalan di **http://localhost:5173**

---

## 🌐 Accessing the Application

1. **Buka browser** (Chrome, Firefox, atau Edge recommended)

2. **Navigate to:**
   ```
   http://localhost:5173
   ```

3. **Explore the App:**
   - **Dashboard**: Search dan browse saham IDX
   - **Analysis**: Analisis teknikal dengan indicators
   - **Screener**: Filter saham berdasarkan kriteria
   - **Learning**: Tutorial dan best practices

4. **Test dengan Stock Symbol IDX:**
   - BBCA (Bank Central Asia)
   - TLKM (Telkom Indonesia)
   - BBRI (Bank Rakyat Indonesia)
   - ASII (Astra International)
   - GOTO (GoTo Gojek Tokopedia)

---

## 🔍 Verification & Testing

### 1. Test Backend API

Buka browser dan test endpoints:

**Health Check:**
```
http://127.0.0.1:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "services": {
    "sectors_api": true,
    "twelve_data_api": false
  }
}
```

**API Documentation (Interactive):**
```
http://127.0.0.1:8000/docs
```

Ini akan membuka Swagger UI di mana Anda bisa test semua endpoints.

### 2. Test Frontend

1. **Search Functionality:**
   - Ketik "BBCA" di search box
   - Seharusnya muncul hasil

2. **Analysis:**
   - Click "Analysis" tab
   - Enter "TLKM"
   - Click "Analyze"
   - Seharusnya muncul price data dan indicators

3. **Dark Mode:**
   - Click toggle button (🌙/☀️) di navbar
   - Theme seharusnya berubah smooth

### 3. Check Browser Console

Buka Developer Tools (F12) dan check:
- Console: Seharusnya tidak ada error merah
- Network: Seharusnya ada successful API calls (status 200)

---

## 🐛 Troubleshooting

### Issue: "Module not found" Error

**Solution:**
```powershell
# Reinstall Python dependencies
pip install --upgrade -r requirements.txt

# Reinstall Node dependencies
npm install
```

### Issue: "API key not configured"

**Solution:**
- Check file `.env` sudah di-copy dari `.env.example`
- Pastikan API key sudah diisi dengan benar
- Restart backend server

### Issue: Port Already in Use

**Backend (8000):**
```powershell
# Find and kill process using port 8000
netstat -ano | findstr :8000
taskkill /PID <process_id> /F
```

**Frontend (5173):**
```powershell
# Change port in vite.config.js or:
npm run dev -- --port 3000
```

### Issue: CORS Errors

**Solution:**
- Pastikan frontend mengakses melalui `http://localhost:5173`
- Check `CORS_ORIGINS` di `.env`
- Restart backend server

### Issue: "No data found for symbol"

**Possible causes:**
1. Symbol tidak ada di IDX (pastikan menggunakan symbol yang valid)
2. API quota habis (free tier memiliki limits)
3. API key tidak valid
4. Network issues

**Solution:**
- Test dengan symbol populer: BBCA, TLKM, BBRI
- Check API key masih aktif
- Check console untuk error messages

---

## 📊 Data Sources Information

### Sectors.app

- **Coverage**: 99% saham di IDX
- **Update Frequency**: Daily
- **Rate Limits**: Tergantung tier yang dipilih
- **Best For**: Analisis saham Indonesia

### Twelve Data

- **Free Tier**: 800 requests/day
- **Coverage**: IDX + Global markets
- **Features**: 100+ technical indicators
- **Best For**: Backup data source

---

## 🔄 Updating the Application

```powershell
# Update Python dependencies
pip install --upgrade -r requirements.txt

# Update Node dependencies
npm update

# Clear cache
rm -rf data/cache/*
```

---

## 🛑 Stopping the Application

### Stop Backend

Di terminal yang menjalankan backend:
- Press `Ctrl + C`

### Stop Frontend

Di terminal yang menjalankan frontend:
- Press `Ctrl + C`

### Deactivate Virtual Environment

```powershell
deactivate
```

---

## 📝 Next Steps

Setelah aplikasi berjalan dengan baik:

1. **Explore Features:**
   - Try different stocks
   - Experiment dengan indicators
   - Test screening functionality

2. **Learn:**
   - Read tutorials di Learning Center
   - Understand technical indicators
   - Practice fundamental analysis

3. **Customize:**
   - Modify indicators parameters
   - Add watchlist stocks
   - Adjust chart timeframes

4. **Contribute:**
   - Report bugs
   - Suggest features
   - Improve documentation

---

## 💡 Tips for Best Experience

1. **Use Latest Browser:** Chrome atau Edge untuk performance terbaik
2. **Enable Caching:** Set `ENABLE_CACHE=true` untuk faster responses
3. **Monitor API Quota:** Free tiers memiliki daily limits
4. **Start with Popular Stocks:** BBCA, TLKM, BBRI untuk testing
5. **Check Logs:** Jika ada masalah, check `logs/app.log`

---

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Sectors.app API Docs](https://sectors.app/api)
- [Twelve Data API Docs](https://twelvedata.com/docs)
- [TradingView Charts](https://www.tradingview.com/lightweight-charts/)

---

## ❓ Need Help?

Jika mengalami kesulitan:

1. Check **Troubleshooting** section di atas
2. Review console logs untuk error messages
3. Verify API keys sudah benar
4. Test dengan different stock symbols
5. Try restarting both servers

---

**Happy Analyzing! 📈🚀**
