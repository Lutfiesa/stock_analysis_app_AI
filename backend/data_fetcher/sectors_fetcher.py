"""
Sectors.app Data Fetcher
Primary data source for Indonesia Stock Exchange (IDX)
"""
import requests
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import pandas as pd
from .base_fetcher import BaseFetcher


class SectorsFetcher(BaseFetcher):
    """Fetcher for Sectors.app API (Indonesia IDX data)"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.base_url = 'https://api.sectors.app/v1'
        self.headers = {
            'Authorization': api_key
        }
    
    def get_stock_data(
        self,
        symbol: str,
        interval: str = '1d',
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Fetch historical stock data from Sectors.app
        
        Note: Sectors.app provides daily data for IDX stocks
        """
        # Generate cache key
        cache_key = self._get_cache_key(
            symbol=symbol,
            interval=interval,
            start=start_date,
            end=end_date
        )
        
        # Try to get from cache
        cached_data = self._read_cache(cache_key, max_age_seconds=3600)
        if cached_data:
            return pd.DataFrame(cached_data)
        
        # Set default dates if not provided
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if not start_date:
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        
        # Apply rate limiting
        self._rate_limit()
        
        # Fetch data from API
        endpoint = f"{self.base_url}/daily/{symbol}"
        params = {
            'start': start_date,
            'end': end_date
        }
        
        try:
            response = requests.get(
                endpoint,
                headers=self.headers,
                params=params,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            # Parse response
            if not data or len(data) == 0:
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(data)
            
            # Normalize columns
            if 'date' in df.columns:
                df['timestamp'] = pd.to_datetime(df['date'])
            
            df = self._normalize_dataframe(df)
            
            # Cache the result
            self._write_cache(cache_key, df.to_dict('records'))
            
            return df
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data from Sectors.app: {e}")
            return pd.DataFrame()
    
    def get_company_info(self, symbol: str) -> Dict[str, Any]:
        """Fetch company information"""
        cache_key = self._get_cache_key(symbol=symbol, info=True)
        
        # Try cache
        cached_data = self._read_cache(cache_key, max_age_seconds=86400)  # 24 hours
        if cached_data:
            return cached_data
        
        self._rate_limit()
        
        endpoint = f"{self.base_url}/company/{symbol}"
        
        try:
            response = requests.get(
                endpoint,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            # Cache the result
            self._write_cache(cache_key, data)
            
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching company info: {e}")
            return {}
    
    def search_stocks(self, query: str) -> List[Dict[str, Any]]:
        """Search for stocks"""
        cache_key = self._get_cache_key(query=query, search=True)
        
        # Try cache
        cached_data = self._read_cache(cache_key, max_age_seconds=86400)
        if cached_data:
            return cached_data
        
        self._rate_limit()
        
        endpoint = f"{self.base_url}/companies"
        
        try:
            response = requests.get(
                endpoint,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            # Filter by query
            query_lower = query.lower()
            results = [
                stock for stock in data
                if query_lower in stock.get('symbol', '').lower() or
                   query_lower in stock.get('name', '').lower()
            ]
            
            # Cache the result
            self._write_cache(cache_key, results)
            
            return results
            
        except requests.exceptions.RequestException as e:
            print(f"Error searching stocks: {e}")
            return []
    
    def get_all_stocks(self) -> List[Dict[str, Any]]:
        """Get list of all stocks in IDX"""
        cache_key = self._get_cache_key(all_stocks=True)
        
        # Try cache (cache for 24 hours)
        cached_data = self._read_cache(cache_key, max_age_seconds=86400)
        if cached_data:
            return cached_data
        
        self._rate_limit()
        
        endpoint = f"{self.base_url}/companies"
        
        try:
            response = requests.get(
                endpoint,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            # Cache the result
            self._write_cache(cache_key, data)
            
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching all stocks: {e}")
            return []
    
    def get_financials(self, symbol: str) -> Dict[str, Any]:
        """Get financial data for fundamental analysis"""
        cache_key = self._get_cache_key(symbol=symbol, financials=True)
        
        # Try cache (24 hours)
        cached_data = self._read_cache(cache_key, max_age_seconds=86400)
        if cached_data:
            return cached_data
        
        self._rate_limit()
        
        endpoint = f"{self.base_url}/financials/{symbol}"
        
        try:
            response = requests.get(
                endpoint,
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            
            # Cache the result
            self._write_cache(cache_key, data)
            
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"Error fetching financials: {e}")
            return {}
