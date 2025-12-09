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
        interval = interval_map.get(interval, interval)
        
        endpoint = f"{self.base_url}/time_series"
        params = {
            'symbol': symbol,
            'interval': interval,
            'apikey': self.api_key,
            'outputsize': 5000,
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
            
            if 'values' not in data:
                return pd.DataFrame()
            
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
            return pd.DataFrame()
    
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
        """Search for stocks"""
        cache_key = self._get_cache_key(query=query)
        
        cached_data = self._read_cache(cache_key, max_age_seconds=86400)
        if cached_data:
            return cached_data
        
        self._rate_limit()
        
        endpoint = f"{self.base_url}/symbol_search"
        params = {
            'symbol': query,
            'apikey': self.api_key
        }
        
        try:
            response = requests.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            results = data.get('data', [])
            self._write_cache(cache_key, results)
            
            return results
            
        except Exception as e:
            print(f"Error searching: {e}")
            return []
