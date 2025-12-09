# 📈 Stock Analysis App - Indonesia Market

Aplikasi analisis saham lengkap untuk **Bursa Efek Indonesia (IDX)** dengan fitur technical analysis, fundamental analysis, backtesting, dan stock screening.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## ✨ Features

### 📊 Technical Analysis
- **Interactive Charts**: Candlestick, line, dan area charts dengan zoom & pan
- **Technical Indicators**: 
  - Moving Averages (SMA, EMA, WMA)
  - RSI, MACD, Bollinger Bands
  - Stochastic, ADX, Volume indicators
- **Pattern Recognition**: Deteksi candlestick patterns otomatis
- **Multi-Timeframe**: 1m, 5m, 15m, 1h, 1d, 1w, 1M

### 💼 Fundamental Analysis
- P/E Ratio, PEG Ratio, P/B Ratio
- ROE, ROA, Debt-to-Equity
- EPS growth, Dividend Yield
- Company profiles & financials

### 🔍 Stock Screening
- Filter saham berdasarkan technical indicators
- Filter berdasarkan fundamental ratios
- Custom screening criteria
- Rank & sort results
- Export to CSV/Excel

### 🧪 Backtesting
- Test strategi trading pada data historis
- Multiple strategy templates (MA Crossover, RSI, MACD)
- Custom strategy builder
- Performance metrics (Sharpe ratio, Max drawdown, Win rate)
- Equity curve & trade log visualization

### 🎨 Modern UI
- Clean & intuitive interface
- Dark mode dengan glassmorphism effects
- Responsive design (mobile-friendly)
- Real-time data updates
- Professional charts dengan TradingView library

## 🚀 Quick Start

### Prerequisites
- Python 3.10 atau lebih tinggi
- Node.js 16+ (untuk frontend build tools)
- API Keys (lihat Setup Guide)

### Installation

1. **Clone repository**
   ```bash
   cd stock-analysis-app
   ```

2. **Setup Python environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   npm install
   ```

4. **Configure API keys**
   ```bash
   cp .env.example .env
   # Edit .env dan masukkan API keys Anda
   ```

5. **Run the application**
   ```bash
   # Terminal 1: Start backend
   python backend/api/server.py
   
   # Terminal 2: Start frontend
   npm run dev
   ```

6. **Open browser**
   ```
   http://localhost:5173
   ```

## 📚 Documentation

- **[Python Setup Guide](PYTHON_SETUP.md)** - ⚡ Quick start & environment setup
- [Setup Guide](docs/SETUP.md) - Panduan instalasi lengkap
- [API Reference](docs/API_REFERENCE.md) - Dokumentasi API endpoints
- [Tutorial: Technical Analysis](docs/tutorials/01_technical_analysis.md)
- [Tutorial: Fundamental Analysis](docs/tutorials/02_fundamental_analysis.md)
- [Tutorial: Backtesting](docs/tutorials/03_backtesting.md)
- [Tutorial: Stock Screening](docs/tutorials/04_screening.md)
- [Best Practices](docs/BEST_PRACTICES.md)

## 🔧 Technology Stack

### Backend
- **Python 3.10+** - Core language
- **FastAPI** - High-performance web framework
- **Pandas** - Data manipulation
- **NumPy** - Numerical computations
- **SQLite** - Local data caching

### Frontend
- **Vite** - Fast build tool
- **Vanilla JavaScript (ES6+)** - No framework overhead
- **TradingView Lightweight Charts** - Professional charting
- **CSS Custom Properties** - Modern styling with dark mode

### Data Sources
- **Sectors.app** - Primary source untuk data saham IDX
- **Twelve Data** - Backup & additional data
- **Alpha Vantage** - Global market data (optional)

## 📖 Learning Resources

Aplikasi ini juga berfungsi sebagai **educational tool** untuk belajar:
- Analisis teknikal saham
- Analisis fundamental
- Strategi trading
- Risk management
- Python programming untuk finance

Setiap modul dilengkapi dengan:
- Dokumentasi lengkap
- Code examples
- Penjelasan konsep
- Best practices

## 🤝 Contributing

Contributions are welcome! Silakan buat issue atau pull request.

## 📄 License

MIT License - silakan gunakan untuk pembelajaran dan development.

## ⚠️ Disclaimer

Aplikasi ini dibuat untuk **tujuan edukasi dan riset**. Bukan sebagai financial advice. Selalu lakukan riset sendiri dan konsultasi dengan financial advisor sebelum membuat keputusan investasi.

---

**Happy Trading! 📈🚀**
