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
        this.loadDashboard();
        this.setupAnalysisPage();
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

        analyzeBtn.addEventListener('click', async () => {
            const symbol = symbolInput.value.trim().toUpperCase();

            if (!symbol) {
                alert('Please enter a stock symbol');
                return;
            }

            await this.analyzeStock(symbol);
        });

        // Enter key to analyze
        symbolInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                analyzeBtn.click();
            }
        });
    }

    async analyzeStock(symbol) {
        const chartContainer = document.getElementById('chartContainer');
        const indicatorsList = document.getElementById('indicatorsList');

        // Show loading
        chartContainer.innerHTML = '<div class="loading">Loading chart data...</div>';
        indicatorsList.innerHTML = '<div class="loading">Loading indicators...</div>';

        try {
            // Fetch technical analysis data
            const data = await this.api.getTechnicalAnalysis(symbol);

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

        // For now, display a simple chart placeholder
        // In a full implementation, we would use TradingView Lightweight Charts
        chartContainer.innerHTML = `
      <div style="padding: 2rem; text-align: center;">
        <h3>${data.symbol} Price Chart</h3>
        <p class="text-muted">Chart will be rendered with TradingView Lightweight Charts library</p>
        <p style="font-size: 2rem; margin: 2rem 0;">
          <strong>Current: Rp ${data.summary.price?.toFixed(2) || 'N/A'}</strong>
        </p>
        <p class="text-muted">Data points: ${data.data?.length || 0}</p>
      </div>
    `;
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
