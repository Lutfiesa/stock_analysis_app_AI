"""
Base Data Fetcher
Abstract base class for all data fetchers with caching support
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd


class BaseFetcher(ABC):
    """Abstract base class for data fetchers"""
    
    def __init__(self, api_key: str, cache_dir: Optional[Path] = None):
        self.api_key = api_key
        self.cache_dir = cache_dir or Path('data/cache')
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.rate_limit_delay = 1.0  # seconds between requests
        self.last_request_time = 0
    
    def _rate_limit(self):
        """Apply rate limiting between requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        
        self.last_request_time = time.time()
    
    def _get_cache_key(self, **kwargs) -> str:
        """Generate cache key from parameters"""
        params_str = json.dumps(kwargs, sort_keys=True)
        return f"{self.__class__.__name__}_{hash(params_str)}"
    
    def _read_cache(self, cache_key: str, max_age_seconds: int = 3600) -> Optional[Any]:
        """Read data from cache if it exists and is not expired"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if not cache_file.exists():
            return None
        
        # Check if cache is expired
        file_age = time.time() - cache_file.stat().st_mtime
        if file_age > max_age_seconds:
            cache_file.unlink()  # Delete expired cache
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None
    
    def _write_cache(self, cache_key: str, data: Any):
        """Write data to cache"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Failed to write cache: {e}")
    
    @abstractmethod
    def get_stock_data(
        self, 
        symbol: str, 
        interval: str = '1d',
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Fetch stock price data
        
        Args:
            symbol: Stock ticker symbol
            interval: Data interval (1m, 5m, 15m, 1h, 1d, 1w, 1M)
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
        
        Returns:
            DataFrame with columns: timestamp, open, high, low, close, volume
        """
        pass
    
    @abstractmethod
    def get_company_info(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch company information
        
        Args:
            symbol: Stock ticker symbol
        
        Returns:
            Dictionary with company details
        """
        pass
    
    @abstractmethod
    def search_stocks(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for stocks by name or symbol
        
        Args:
            query: Search query
        
        Returns:
            List of matching stocks
        """
        pass
    
    def _normalize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize DataFrame to standard format"""
        if df.empty:
            return df
        
        # Ensure standard column names (lowercase)
        column_mapping = {
            'Open': 'open',
            'High': 'high',
            'Low': 'low',
            'Close': 'close',
            'Volume': 'volume',
            'Timestamp': 'timestamp',
            'Date': 'timestamp',
            'Datetime': 'timestamp'
        }
        
        df = df.rename(columns=column_mapping)
        
        # Ensure timestamp is datetime
        if 'timestamp' in df.columns:
            if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
                df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # Sort by timestamp
        if 'timestamp' in df.columns:
            df = df.sort_values('timestamp')
        
        return df
