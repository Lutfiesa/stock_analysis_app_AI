"""
Twelve Data API Fetcher
Backup data source with global market coverage including IDX
"""
import requests
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import pandas as pd
from .base_fetcher import BaseFetcher


class TwelveDataFetcher(BaseFetcher):
    """Fetcher for Twelve Data API"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.base_url = 'https://api.twelvedata.com'
    
    def get_stock_data(
        self,
        symbol: str,
        interval: str = '1day',
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """Fetch time series data"""
        cache_key = self._get_cache_key(
            symbol=symbol,
            interval=interval,
            start=start_date,
            end=end_date
        )
        
        # Try cache
        cached_data = self._read_cache(cache_key, max_age_seconds=3600)
        if cached_data:
            return pd.DataFrame(cached_data)
        
        self._rate_limit()
        
        # Map interval format
        interval_map = {
            '1d': '1day',
            '1h': '1h',
            '15m': '15min',
            '5m': '5min',
            '1m': '1min'
        }
        mapped_interval = interval_map.get(interval, interval)
        
        # Check if we have a valid API key
        if not self.api_key or self.api_key == 'your_twelvedata_api_key_here':
            print(f"No valid API key, generating demo data for {symbol}")
            return self._generate_demo_data(symbol)
        
        endpoint = f"{self.base_url}/time_series"
        params = {
            'symbol': symbol,
            'interval': mapped_interval,
            'apikey': self.api_key,
            'outputsize': 365,
            'format': 'JSON'
        }
        
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        
        try:
            response = requests.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Check for API errors
            if 'code' in data and data['code'] != 200:
                print(f"Twelve Data API error: {data.get('message', 'Unknown error')}")
                return self._generate_demo_data(symbol)
            
            if 'values' not in data:
                print(f"No data from API for {symbol}, using demo data")
                return self._generate_demo_data(symbol)
            
            df = pd.DataFrame(data['values'])
            
            # Convert types
            if 'datetime' in df.columns:
                df['timestamp'] = pd.to_datetime(df['datetime'])
            
            numeric_cols = ['open', 'high', 'low', 'close', 'volume']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            df = self._normalize_dataframe(df)
            
            # Cache
            self._write_cache(cache_key, df.to_dict('records'))
            
            return df
            
        except Exception as e:
            print(f"Error fetching from Twelve Data: {e}")
            print(f"Using demo data for {symbol}")
            return self._generate_demo_data(symbol)
    
    def _generate_demo_data(self, symbol: str) -> pd.DataFrame:
        """Generate demo stock data for testing without API key"""
        import random
        import numpy as np
        
        # Get base price based on symbol
        base_prices = {
            'BBCA': 9500, 'BBRI': 4800, 'BMRI': 6200, 'TLKM': 3800,
            'ASII': 5500, 'UNVR': 4200, 'ICBP': 10500, 'INDF': 6800,
            'GGRM': 24000, 'HMSP': 1100, 'KLBF': 1600, 'PGAS': 1400,
            'SMGR': 7500, 'PTBA': 2800, 'ADRO': 2600, 'ANTM': 1800,
            'INCO': 4500, 'BBNI': 5200, 'EXCL': 2300, 'ISAT': 8500,
        }
        
        # Extract base symbol (remove .JK suffix)
        base_symbol = symbol.replace('.JK', '').upper()
        base_price = base_prices.get(base_symbol, 5000)
        
        # Generate 365 days of data
        dates = pd.date_range(end=datetime.now(), periods=365, freq='D')
        
        # Generate realistic price movement
        np.random.seed(hash(symbol) % (2**32))
        returns = np.random.normal(0.0005, 0.02, len(dates))  # 0.05% daily mean, 2% volatility
        price_multipliers = np.cumprod(1 + returns)
        
        prices = base_price * price_multipliers
        
        data = []
        for i, date in enumerate(dates):
            price = prices[i]
            daily_volatility = price * 0.015  # 1.5% daily range
            
            open_price = price + random.uniform(-daily_volatility/2, daily_volatility/2)
            high_price = max(open_price, price) + random.uniform(0, daily_volatility)
            low_price = min(open_price, price) - random.uniform(0, daily_volatility)
            close_price = price
            volume = random.randint(10000000, 100000000)
            
            data.append({
                'timestamp': date,
                'open': round(open_price, 0),
                'high': round(high_price, 0),
                'low': round(low_price, 0),
                'close': round(close_price, 0),
                'volume': volume
            })
        
        df = pd.DataFrame(data)
        df = self._normalize_dataframe(df)
        return df
    
    def get_company_info(self, symbol: str) -> Dict[str, Any]:
        """Get company profile"""
        cache_key = self._get_cache_key(symbol=symbol, profile=True)
        
        cached_data = self._read_cache(cache_key, max_age_seconds=86400)
        if cached_data:
            return cached_data
        
        self._rate_limit()
        
        endpoint = f"{self.base_url}/profile"
        params = {
            'symbol': symbol,
            'apikey': self.api_key
        }
        
        try:
            response = requests.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            self._write_cache(cache_key, data)
            return data
            
        except Exception as e:
            print(f"Error fetching profile: {e}")
            return {}
    
    def search_stocks(self, query: str) -> List[Dict[str, Any]]:
        """Search for stocks - uses local IDX list for reliability"""
        # Always use local search for IDX stocks (more reliable than API)
        query_lower = query.lower()
        all_stocks = self.get_all_stocks()
        
        results = [
            stock for stock in all_stocks
            if query_lower in stock.get('symbol', '').lower() or
               query_lower in stock.get('name', '').lower()
        ]
        
        return results
    
    def get_all_stocks(self) -> List[Dict[str, Any]]:
        """Get list of popular IDX stocks (Indonesia Stock Exchange)"""
        # Hardcoded list of popular Indonesian stocks
        idx_stocks = [
            {"symbol": "BBCA", "name": "Bank Central Asia"},
            {"symbol": "BBRI", "name": "Bank Rakyat Indonesia"},
            {"symbol": "BMRI", "name": "Bank Mandiri"},
            {"symbol": "TLKM", "name": "Telkom Indonesia"},
            {"symbol": "ASII", "name": "Astra International"},
            {"symbol": "UNVR", "name": "Unilever Indonesia"},
            {"symbol": "ICBP", "name": "Indofood CBP"},
            {"symbol": "INDF", "name": "Indofood Sukses Makmur"},
            {"symbol": "GGRM", "name": "Gudang Garam"},
            {"symbol": "HMSP", "name": "HM Sampoerna"},
            {"symbol": "KLBF", "name": "Kalbe Farma"},
            {"symbol": "PGAS", "name": "Perusahaan Gas Negara"},
            {"symbol": "SMGR", "name": "Semen Indonesia"},
            {"symbol": "PTBA", "name": "Bukit Asam"},
            {"symbol": "ADRO", "name": "Adaro Energy"},
            {"symbol": "ANTM", "name": "Aneka Tambang"},
            {"symbol": "INCO", "name": "Vale Indonesia"},
            {"symbol": "BBNI", "name": "Bank Negara Indonesia"},
            {"symbol": "EXCL", "name": "XL Axiata"},
            {"symbol": "ISAT", "name": "Indosat Ooredoo"},
            {"symbol": "JSMR", "name": "Jasa Marga"},
            {"symbol": "MEDC", "name": "Medco Energi"},
            {"symbol": "MNCN", "name": "Media Nusantara Citra"},
            {"symbol": "SCMA", "name": "Surya Citra Media"},
            {"symbol": "TOWR", "name": "Sarana Menara Nusantara"},
            {"symbol": "TBIG", "name": "Tower Bersama Infrastructure"},
            {"symbol": "ACES", "name": "Ace Hardware Indonesia"},
            {"symbol": "ERAA", "name": "Erajaya Swasembada"},
            {"symbol": "MAPI", "name": "Mitra Adiperkasa"},
            {"symbol": "LPPF", "name": "Matahari Department Store"},
        ]
        return idx_stocks
    
    def get_financials(self, symbol: str) -> Dict[str, Any]:
        """Get financial data (limited in free tier)"""
        cache_key = self._get_cache_key(symbol=symbol, financials=True)
        
        cached_data = self._read_cache(cache_key, max_age_seconds=86400)
        if cached_data:
            return cached_data
        
        self._rate_limit()
        
        # Twelve Data has limited financial data in free tier
        # Return basic info from profile endpoint
        endpoint = f"{self.base_url}/profile"
        params = {
            'symbol': symbol,
            'apikey': self.api_key
        }
        
        try:
            response = requests.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            # Transform to financial-like structure
            financials = {
                'symbol': symbol,
                'name': data.get('name', ''),
                'sector': data.get('sector', ''),
                'industry': data.get('industry', ''),
                'employees': data.get('employees', 0),
                'description': data.get('description', ''),
                'note': 'Full financial data requires premium API subscription'
            }
            
            self._write_cache(cache_key, financials)
            return financials
            
        except Exception as e:
            print(f"Error fetching financials: {e}")
            return {}
