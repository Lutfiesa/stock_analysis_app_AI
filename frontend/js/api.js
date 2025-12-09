/**
 * API Communication Module
 * Handles all backend API calls
 */

const API_BASE_URL = '/api';

class API {
    constructor() {
        this.baseUrl = API_BASE_URL;
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;

        try {
            const response = await fetch(url, {
                headers: {
                    'Content-Type': 'application/json',
                    ...options.headers,
                },
                ...options,
            });

            if (!response.ok) {
                const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
                throw new Error(error.detail || `HTTP error! status: ${response.status}`);
            }

            return await response.json();

        } catch (error) {
            console.error(`API Error (${endpoint}):`, error);
            throw error;
        }
    }

    // Search stocks
    async searchStocks(query) {
        const data = await this.request(`/stocks/search?q=${encodeURIComponent(query)}`);
        return data.results || [];
    }

    // Get all stocks
    async getAllStocks() {
        const data = await this.request('/stocks/all');
        return data.stocks || [];
    }

    // Get stock data
    async getStockData(symbol, interval = '1d', startDate = null, endDate = null) {
        let url = `/stock/${symbol.toUpperCase()}?interval=${interval}`;

        if (startDate) {
            url += `&start_date=${startDate}`;
        }
        if (endDate) {
            url += `&end_date=${endDate}`;
        }

        return await this.request(url);
    }

    // Get company info
    async getCompanyInfo(symbol) {
        return await this.request(`/stock/${symbol.toUpperCase()}/info`);
    }

    // Get technical analysis
    async getTechnicalAnalysis(symbol, interval = '1d', startDate = null, endDate = null) {
        let url = `/analysis/technical/${symbol.toUpperCase()}?interval=${interval}`;

        if (startDate) {
            url += `&start_date=${startDate}`;
        }
        if (endDate) {
            url += `&end_date=${endDate}`;
        }

        return await this.request(url);
    }

    // Get fundamental analysis
    async getFundamentalAnalysis(symbol) {
        return await this.request(`/analysis/fundamental/${symbol.toUpperCase()}`);
    }

    // Health check
    async healthCheck() {
        return await this.request('/health');
    }
}

export default API;
