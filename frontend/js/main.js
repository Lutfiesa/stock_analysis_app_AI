/**
 * Main Application JavaScript
 * Stock Analysis App
 */

// Import modules
import API from './api.js';

// Initialize app
class StockAnalysisApp {
    constructor() {
        this.currentPage = 'dashboard';
        this.theme = localStorage.getItem('theme') || 'light';
        this.api = new API();

        this.init();
    }

    init() {
        this.setupTheme();
        this.setupNavigation();
        this.setupSearch();
        this.updateMarketStatus();
        this.loadDashboard();
        this.setupAnalysisPage();

        // Update market status every minute
        setInterval(() => this.updateMarketStatus(), 60000);
    }

    // Market Status based on IDX trading hours
    updateMarketStatus() {
        const statusEl = document.getElementById('marketStatus');
        if (!statusEl) return;

        const now = new Date();
        // Convert to WIB (UTC+7)
        const wibOffset = 7 * 60; // minutes
        const utcOffset = now.getTimezoneOffset();
        const wibTime = new Date(now.getTime() + (wibOffset + utcOffset) * 60000);

        const day = wibTime.getDay(); // 0 = Sunday, 6 = Saturday
        const hour = wibTime.getHours();
        const minute = wibTime.getMinutes();
        const timeInMinutes = hour * 60 + minute;

        // IDX Trading hours: Monday-Friday, 09:00-16:00 WIB
        // Pre-opening: 08:45-09:00
        // Session 1: 09:00-12:00 (lunch break 12:00-13:30)
        // Session 2: 13:30-16:00

        const isWeekday = day >= 1 && day <= 5;
        const isPreOpening = timeInMinutes >= 525 && timeInMinutes < 540; // 08:45-09:00
        const isSession1 = timeInMinutes >= 540 && timeInMinutes < 720; // 09:00-12:00
        const isLunchBreak = timeInMinutes >= 720 && timeInMinutes < 810; // 12:00-13:30
        const isSession2 = timeInMinutes >= 810 && timeInMinutes < 960; // 13:30-16:00

        let status = 'Closed';
        let statusClass = 'closed';

        if (isWeekday) {
            if (isPreOpening) {
                status = 'Pre-Opening';
                statusClass = 'pre-opening';
            } else if (isSession1 || isSession2) {
                status = 'Open';
                statusClass = 'open';
            } else if (isLunchBreak) {
                status = 'Lunch Break';
                statusClass = 'break';
            }
        }

        statusEl.textContent = status;
        statusEl.className = 'stat-value market-' + statusClass;
    }

    // Theme Management
    setupTheme() {
        document.documentElement.setAttribute('data-theme', this.theme);

        const themeToggle = document.getElementById('themeToggle');
        themeToggle.addEventListener('click', () => {
            this.theme = this.theme === 'light' ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', this.theme);
            localStorage.setItem('theme', this.theme);

            // Update icon
            themeToggle.querySelector('.icon').textContent =
                this.theme === 'dark' ? '☀️' : '🌙';
        });

        // Set initial icon
        themeToggle.querySelector('.icon').textContent =
            this.theme === 'dark' ? '☀️' : '🌙';
    }

    // Navigation
    setupNavigation() {
        const navLinks = document.querySelectorAll('.nav-link');

        navLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = link.getAttribute('data-page');
                this.navigateTo(page);
            });
        });
    }

    navigateTo(page) {
        // Update active nav link
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('data-page') === page) {
                link.classList.add('active');
            }
        });

        // Update active page
        document.querySelectorAll('.page').forEach(pageEl => {
            pageEl.classList.remove('active');
        });

        const pageEl = document.getElementById(`${page}-page`);
        if (pageEl) {
            pageEl.classList.add('active');
            this.currentPage = page;
        }
    }

    // Search Functionality
    setupSearch() {
        const searchInput = document.getElementById('stockSearch');
        const searchResults = document.getElementById('searchResults');
        let searchTimeout;

        searchInput.addEventListener('input', (e) => {
            const query = e.target.value.trim();

            if (query.length < 2) {
                searchResults.classList.remove('show');
                return;
            }

            // Debounce search
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(async () => {
                await this.performSearch(query);
            }, 300);
        });

        // Close search results when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.search-container')) {
                searchResults.classList.remove('show');
            }
        });
    }

    async performSearch(query) {
        const searchResults = document.getElementById('searchResults');

        try {
            const results = await this.api.searchStocks(query);

            if (results.length === 0) {
                searchResults.innerHTML = '<div class="empty-state"><p>No results found</p></div>';
                searchResults.classList.add('show');
                return;
            }

            searchResults.innerHTML = results.slice(0, 10).map(stock => `
        <div class="search-result-item" data-symbol="${stock.symbol}">
          <strong>${stock.symbol}</strong> - ${stock.name || 'Unknown'}
        </div>
      `).join('');

            // Add click handlers
            searchResults.querySelectorAll('.search-result-item').forEach(item => {
                item.addEventListener('click', () => {
                    const symbol = item.getAttribute('data-symbol');
                    this.selectStock(symbol);
                    searchResults.classList.remove('show');
                });
            });

            searchResults.classList.add('show');

        } catch (error) {
            console.error('Search error:', error);
            searchResults.innerHTML = '<div class="empty-state"><p>Error performing search</p></div>';
            searchResults.classList.add('show');
        }
    }

    selectStock(symbol) {
        // Navigate to analysis page with selected stock
        document.getElementById('analysisSymbol').value = symbol;
        this.navigateTo('analysis');

        // Trigger analysis
        setTimeout(() => {
            document.getElementById('analyzeBtn').click();
        }, 100);
    }

    // Dashboard
    async loadDashboard() {
        try {
            // Load all stocks
            const stocks = await this.api.getAllStocks();

            // Update total stocks count
            document.getElementById('totalStocks').textContent = stocks.length;

            // Display popular stocks (first 8)
            this.displayPopularStocks(stocks.slice(0, 8));

        } catch (error) {
            console.error('Failed to load dashboard:', error);
            document.getElementById('popularStocks').innerHTML =
                '<div class="empty-state"><p>Failed to load stocks. Please check your API configuration.</p></div>';
        }
    }

    displayPopularStocks(stocks) {
        const container = document.getElementById('popularStocks');

        container.innerHTML = stocks.map(stock => `
      <div class="card" style="cursor: pointer;" data-symbol="${stock.symbol}">
        <h4>${stock.symbol}</h4>
        <p class="text-muted" style="font-size: 0.875rem; margin: 0;">
          ${stock.name || 'Unknown Company'}
        </p>
      </div>
    `).join('');

        // Add click handlers
        container.querySelectorAll('.card').forEach(card => {
            card.addEventListener('click', () => {
                const symbol = card.getAttribute('data-symbol');
                this.selectStock(symbol);
            });
        });
    }

    // Analysis Page
    setupAnalysisPage() {
        const analyzeBtn = document.getElementById('analyzeBtn');
        const symbolInput = document.getElementById('analysisSymbol');

        // Store current analysis settings
        this.currentSymbol = '';
        this.currentInterval = '1d';
        this.showSMA = true;
        this.showEMA = false;
        this.showBB = false;

        analyzeBtn.addEventListener('click', async () => {
            const symbol = symbolInput.value.trim().toUpperCase();

            if (!symbol) {
                alert('Please enter a stock symbol');
                return;
            }

            this.currentSymbol = symbol;
            await this.analyzeStock(symbol, this.currentInterval);
        });

        // Enter key to analyze
        symbolInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                analyzeBtn.click();
            }
        });

        // Timeframe buttons
        const timeframeButtons = document.querySelectorAll('.timeframe-buttons .btn');
        timeframeButtons.forEach(btn => {
            btn.addEventListener('click', async () => {
                // Update active state
                timeframeButtons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');

                // Map button text to interval
                const intervalMap = {
                    '1D': '1d',
                    '1W': '1d',  // Week of daily data
                    '1M': '1d',  // Month of daily data
                    '3M': '1d',  // 3 months of daily data
                    '1Y': '1d',  // Year of daily data
                };

                const buttonText = btn.textContent.trim();
                this.currentInterval = intervalMap[buttonText] || '1d';
                this.currentTimeframe = buttonText;

                // Re-analyze if symbol is set
                if (this.currentSymbol) {
                    await this.analyzeStock(this.currentSymbol, this.currentInterval, buttonText);
                }
            });
        });

        // Indicator toggles
        const toggleSMA = document.getElementById('toggleSMA');
        const toggleEMA = document.getElementById('toggleEMA');
        const toggleBB = document.getElementById('toggleBB');

        if (toggleSMA) {
            toggleSMA.addEventListener('change', () => {
                this.showSMA = toggleSMA.checked;
                if (this.currentChartData) {
                    this.renderChart(this.currentChartData);
                }
            });
        }

        if (toggleEMA) {
            toggleEMA.addEventListener('change', () => {
                this.showEMA = toggleEMA.checked;
                if (this.currentChartData) {
                    this.renderChart(this.currentChartData);
                }
            });
        }

        if (toggleBB) {
            toggleBB.addEventListener('change', () => {
                this.showBB = toggleBB.checked;
                if (this.currentChartData) {
                    this.renderChart(this.currentChartData);
                }
            });
        }
    }

    async analyzeStock(symbol, interval = '1d', timeframe = '1Y') {
        const chartContainer = document.getElementById('chartContainer');
        const indicatorsList = document.getElementById('indicatorsList');

        // Show loading
        chartContainer.innerHTML = '<div class="loading">Loading chart data...</div>';
        indicatorsList.innerHTML = '<div class="loading">Loading indicators...</div>';

        try {
            // Calculate date range based on timeframe
            const endDate = new Date();
            let startDate = new Date();

            switch (timeframe) {
                case '1D':
                    startDate.setDate(endDate.getDate() - 1);
                    break;
                case '1W':
                    startDate.setDate(endDate.getDate() - 7);
                    break;
                case '1M':
                    startDate.setMonth(endDate.getMonth() - 1);
                    break;
                case '3M':
                    startDate.setMonth(endDate.getMonth() - 3);
                    break;
                case '1Y':
                default:
                    startDate.setFullYear(endDate.getFullYear() - 1);
                    break;
            }

            // Fetch technical analysis data
            const data = await this.api.getTechnicalAnalysis(
                symbol,
                interval,
                startDate.toISOString().split('T')[0],
                endDate.toISOString().split('T')[0]
            );

            // Store for re-rendering with different indicator settings
            this.currentChartData = data;

            // Display chart
            this.renderChart(data);

            // Display indicators
            this.displayIndicators(data.summary);

        } catch (error) {
            console.error('Analysis error:', error);
            chartContainer.innerHTML = `
        <div class="empty-state">
          <p>❌ Failed to load data for ${symbol}</p>
          <p class="text-muted">Please check if the symbol is correct and try again.</p>
        </div>
      `;
            indicatorsList.innerHTML = '<p class="text-muted">No data available</p>';
        }
    }

    renderChart(data) {
        const chartContainer = document.getElementById('chartContainer');

        // Clear container
        chartContainer.innerHTML = '';

        // Check if we have data
        if (!data.data || data.data.length === 0) {
            chartContainer.innerHTML = `
                <div class="empty-state">
                    <p>📊 No chart data available for ${data.symbol}</p>
                </div>
            `;
            return;
        }

        // Create chart using TradingView Lightweight Charts
        const chart = LightweightCharts.createChart(chartContainer, {
            width: chartContainer.clientWidth,
            height: 500,
            layout: {
                background: { type: 'solid', color: 'transparent' },
                textColor: getComputedStyle(document.documentElement).getPropertyValue('--color-text-primary').trim() || '#333',
            },
            grid: {
                vertLines: { color: 'rgba(128, 128, 128, 0.1)' },
                horzLines: { color: 'rgba(128, 128, 128, 0.1)' },
            },
            crosshair: {
                mode: LightweightCharts.CrosshairMode.Normal,
            },
            rightPriceScale: {
                borderColor: 'rgba(128, 128, 128, 0.3)',
            },
            timeScale: {
                borderColor: 'rgba(128, 128, 128, 0.3)',
                timeVisible: true,
                secondsVisible: false,
            },
        });

        // Add candlestick series
        const candlestickSeries = chart.addCandlestickSeries({
            upColor: '#26a69a',
            downColor: '#ef5350',
            borderDownColor: '#ef5350',
            borderUpColor: '#26a69a',
            wickDownColor: '#ef5350',
            wickUpColor: '#26a69a',
        });

        // Format data for candlestick chart
        const candleData = data.data
            .filter(d => d.open && d.high && d.low && d.close)
            .map(d => {
                // Parse timestamp
                let time;
                if (d.timestamp) {
                    const date = new Date(d.timestamp);
                    time = Math.floor(date.getTime() / 1000);
                } else {
                    time = Math.floor(Date.now() / 1000);
                }

                return {
                    time: time,
                    open: parseFloat(d.open),
                    high: parseFloat(d.high),
                    low: parseFloat(d.low),
                    close: parseFloat(d.close),
                };
            })
            .sort((a, b) => a.time - b.time);

        // Set data
        if (candleData.length > 0) {
            candlestickSeries.setData(candleData);
        }

        // Add volume bars if available
        if (data.data[0] && data.data[0].volume) {
            const volumeSeries = chart.addHistogramSeries({
                color: '#26a69a',
                priceFormat: {
                    type: 'volume',
                },
                priceScaleId: '',
                scaleMargins: {
                    top: 0.8,
                    bottom: 0,
                },
            });

            const volumeData = data.data
                .filter(d => d.volume)
                .map(d => {
                    let time;
                    if (d.timestamp) {
                        const date = new Date(d.timestamp);
                        time = Math.floor(date.getTime() / 1000);
                    } else {
                        time = Math.floor(Date.now() / 1000);
                    }

                    const open = parseFloat(d.open) || 0;
                    const close = parseFloat(d.close) || 0;

                    return {
                        time: time,
                        value: parseFloat(d.volume),
                        color: close >= open ? 'rgba(38, 166, 154, 0.5)' : 'rgba(239, 83, 80, 0.5)',
                    };
                })
                .sort((a, b) => a.time - b.time);

            if (volumeData.length > 0) {
                volumeSeries.setData(volumeData);
            }
        }

        // Add SMA lines if available and enabled
        if (this.showSMA && data.data[0] && data.data[0].sma_20) {
            const sma20Series = chart.addLineSeries({
                color: '#2196F3',
                lineWidth: 2,
                title: 'SMA 20',
            });

            const sma20Data = data.data
                .filter(d => d.sma_20 != null)
                .map(d => {
                    let time;
                    if (d.timestamp) {
                        const date = new Date(d.timestamp);
                        time = Math.floor(date.getTime() / 1000);
                    } else {
                        time = Math.floor(Date.now() / 1000);
                    }
                    return {
                        time: time,
                        value: parseFloat(d.sma_20),
                    };
                })
                .sort((a, b) => a.time - b.time);

            if (sma20Data.length > 0) {
                sma20Series.setData(sma20Data);
            }
        }

        if (this.showSMA && data.data[0] && data.data[0].sma_50) {
            const sma50Series = chart.addLineSeries({
                color: '#FF9800',
                lineWidth: 2,
                title: 'SMA 50',
            });

            const sma50Data = data.data
                .filter(d => d.sma_50 != null)
                .map(d => {
                    let time;
                    if (d.timestamp) {
                        const date = new Date(d.timestamp);
                        time = Math.floor(date.getTime() / 1000);
                    } else {
                        time = Math.floor(Date.now() / 1000);
                    }
                    return {
                        time: time,
                        value: parseFloat(d.sma_50),
                    };
                })
                .sort((a, b) => a.time - b.time);

            if (sma50Data.length > 0) {
                sma50Series.setData(sma50Data);
            }
        }

        // Add EMA lines if enabled
        if (this.showEMA && data.data[0] && data.data[0].ema_12) {
            const ema12Series = chart.addLineSeries({
                color: '#9C27B0',
                lineWidth: 2,
                title: 'EMA 12',
            });

            const ema12Data = data.data
                .filter(d => d.ema_12 != null)
                .map(d => {
                    let time;
                    if (d.timestamp) {
                        const date = new Date(d.timestamp);
                        time = Math.floor(date.getTime() / 1000);
                    } else {
                        time = Math.floor(Date.now() / 1000);
                    }
                    return {
                        time: time,
                        value: parseFloat(d.ema_12),
                    };
                })
                .sort((a, b) => a.time - b.time);

            if (ema12Data.length > 0) {
                ema12Series.setData(ema12Data);
            }
        }

        if (this.showEMA && data.data[0] && data.data[0].ema_26) {
            const ema26Series = chart.addLineSeries({
                color: '#E91E63',
                lineWidth: 2,
                title: 'EMA 26',
            });

            const ema26Data = data.data
                .filter(d => d.ema_26 != null)
                .map(d => {
                    let time;
                    if (d.timestamp) {
                        const date = new Date(d.timestamp);
                        time = Math.floor(date.getTime() / 1000);
                    } else {
                        time = Math.floor(Date.now() / 1000);
                    }
                    return {
                        time: time,
                        value: parseFloat(d.ema_26),
                    };
                })
                .sort((a, b) => a.time - b.time);

            if (ema26Data.length > 0) {
                ema26Series.setData(ema26Data);
            }
        }

        // Add Bollinger Bands if enabled
        if (this.showBB && data.data[0] && data.data[0].bb_upper) {
            // Upper band
            const bbUpperSeries = chart.addLineSeries({
                color: 'rgba(33, 150, 243, 0.5)',
                lineWidth: 1,
                title: 'BB Upper',
            });

            const bbUpperData = data.data
                .filter(d => d.bb_upper != null)
                .map(d => {
                    let time;
                    if (d.timestamp) {
                        const date = new Date(d.timestamp);
                        time = Math.floor(date.getTime() / 1000);
                    } else {
                        time = Math.floor(Date.now() / 1000);
                    }
                    return {
                        time: time,
                        value: parseFloat(d.bb_upper),
                    };
                })
                .sort((a, b) => a.time - b.time);

            if (bbUpperData.length > 0) {
                bbUpperSeries.setData(bbUpperData);
            }

            // Middle band (SMA 20)
            const bbMiddleSeries = chart.addLineSeries({
                color: 'rgba(33, 150, 243, 0.8)',
                lineWidth: 1,
                title: 'BB Middle',
            });

            const bbMiddleData = data.data
                .filter(d => d.bb_middle != null)
                .map(d => {
                    let time;
                    if (d.timestamp) {
                        const date = new Date(d.timestamp);
                        time = Math.floor(date.getTime() / 1000);
                    } else {
                        time = Math.floor(Date.now() / 1000);
                    }
                    return {
                        time: time,
                        value: parseFloat(d.bb_middle),
                    };
                })
                .sort((a, b) => a.time - b.time);

            if (bbMiddleData.length > 0) {
                bbMiddleSeries.setData(bbMiddleData);
            }

            // Lower band
            const bbLowerSeries = chart.addLineSeries({
                color: 'rgba(33, 150, 243, 0.5)',
                lineWidth: 1,
                title: 'BB Lower',
            });

            const bbLowerData = data.data
                .filter(d => d.bb_lower != null)
                .map(d => {
                    let time;
                    if (d.timestamp) {
                        const date = new Date(d.timestamp);
                        time = Math.floor(date.getTime() / 1000);
                    } else {
                        time = Math.floor(Date.now() / 1000);
                    }
                    return {
                        time: time,
                        value: parseFloat(d.bb_lower),
                    };
                })
                .sort((a, b) => a.time - b.time);

            if (bbLowerData.length > 0) {
                bbLowerSeries.setData(bbLowerData);
            }
        }

        // Fit content
        chart.timeScale().fitContent();

        // Handle resize
        const resizeObserver = new ResizeObserver(entries => {
            const { width, height } = entries[0].contentRect;
            chart.applyOptions({ width, height: 500 });
        });
        resizeObserver.observe(chartContainer);

        // Store chart reference for cleanup
        this.currentChart = chart;
        this.resizeObserver = resizeObserver;
    }

    displayIndicators(summary) {
        const indicatorsList = document.getElementById('indicatorsList');

        if (!summary) {
            indicatorsList.innerHTML = '<p class="text-muted">No indicators available</p>';
            return;
        }

        const indicators = [
            { label: 'Price', value: summary.price, format: 'currency' },
            { label: 'RSI (14)', value: summary.rsi, format: 'number' },
            { label: 'MACD', value: summary.macd, format: 'number' },
            { label: 'MACD Signal', value: summary.macd_signal, format: 'number' },
            { label: 'SMA (20)', value: summary.sma_20, format: 'currency' },
            { label: 'SMA (50)', value: summary.sma_50, format: 'currency' },
        ];

        indicatorsList.innerHTML = indicators.map(ind => {
            if (ind.value === null || ind.value === undefined) {
                return `
          <div style="display: flex; justify-content: space-between; padding: 0.75rem 0; border-bottom: 1px solid var(--color-border);">
            <span>${ind.label}</span>
            <span class="text-muted">N/A</span>
          </div>
        `;
            }

            const formattedValue = ind.format === 'currency'
                ? `Rp ${ind.value.toFixed(2)}`
                : ind.value.toFixed(2);

            return `
        <div style="display: flex; justify-content: space-between; padding: 0.75rem 0; border-bottom: 1px solid var(--color-border);">
          <span>${ind.label}</span>
          <strong>${formattedValue}</strong>
        </div>
      `;
        }).join('');
    }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.app = new StockAnalysisApp();
});
