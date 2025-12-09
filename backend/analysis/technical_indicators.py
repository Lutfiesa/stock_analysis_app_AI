"""
Technical Indicators
Implementations of common technical analysis indicators
"""
import pandas as pd
import numpy as np
from typing import Optional, Tuple


class TechnicalIndicators:
    """Collection of technical analysis indicators"""
    
    @staticmethod
    def sma(data: pd.Series, period: int) -> pd.Series:
        """
        Simple Moving Average
        
        Args:
            data: Price data (usually close prices)
            period: Number of periods
        
        Returns:
            SMA values
        """
        return data.rolling(window=period).mean()
    
    @staticmethod
    def ema(data: pd.Series, period: int) -> pd.Series:
        """
        Exponential Moving Average
        
        Args:
            data: Price data
            period: Number of periods
        
        Returns:
            EMA values
        """
        return data.ewm(span=period, adjust=False).mean()
    
    @staticmethod
    def wma(data: pd.Series, period: int) -> pd.Series:
        """
        Weighted Moving Average
        
        Args:
            data: Price data
            period: Number of periods
        
        Returns:
            WMA values
        """
        weights = np.arange(1, period + 1)
        return data.rolling(period).apply(
            lambda x: np.dot(x, weights) / weights.sum(), raw=True
        )
    
    @staticmethod
    def rsi(data: pd.Series, period: int = 14) -> pd.Series:
        """
        Relative Strength Index
        
        Args:
            data: Price data
            period: RSI period (default: 14)
        
        Returns:
            RSI values (0-100)
        """
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def macd(
        data: pd.Series,
        fast_period: int = 12,
        slow_period: int = 26,
        signal_period: int = 9
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Moving Average Convergence Divergence
        
        Args:
            data: Price data
            fast_period: Fast EMA period
            slow_period: Slow EMA period
            signal_period: Signal line period
        
        Returns:
            Tuple of (MACD line, Signal line, Histogram)
        """
        fast_ema = TechnicalIndicators.ema(data, fast_period)
        slow_ema = TechnicalIndicators.ema(data, slow_period)
        
        macd_line = fast_ema - slow_ema
        signal_line = TechnicalIndicators.ema(macd_line, signal_period)
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    @staticmethod
    def bollinger_bands(
        data: pd.Series,
        period: int = 20,
        std_dev: float = 2.0
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Bollinger Bands
        
        Args:
            data: Price data
            period: SMA period
            std_dev: Number of standard deviations
        
        Returns:
            Tuple of (Upper band, Middle band/SMA, Lower band)
        """
        middle_band = TechnicalIndicators.sma(data, period)
        std = data.rolling(window=period).std()
        
        upper_band = middle_band + (std * std_dev)
        lower_band = middle_band - (std * std_dev)
        
        return upper_band, middle_band, lower_band
    
    @staticmethod
    def stochastic(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        k_period: int = 14,
        d_period: int = 3
    ) -> Tuple[pd.Series, pd.Series]:
        """
        Stochastic Oscillator
        
        Args:
            high: High prices
            low: Low prices
            close: Close prices
            k_period: %K period
            d_period: %D period (smoothing)
        
        Returns:
            Tuple of (%K, %D)
        """
        lowest_low = low.rolling(window=k_period).min()
        highest_high = high.rolling(window=k_period).max()
        
        k = 100 * (close - lowest_low) / (highest_high - lowest_low)
        d = k.rolling(window=d_period).mean()
        
        return k, d
    
    @staticmethod
    def atr(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 14
    ) -> pd.Series:
        """
        Average True Range
        
        Args:
            high: High prices
            low: Low prices
            close: Close prices
            period: ATR period
        
        Returns:
            ATR values
        """
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        
        return atr
    
    @staticmethod
    def adx(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        period: int = 14
    ) -> pd.Series:
        """
        Average Directional Index
        
        Args:
            high: High prices
            low: Low prices
            close: Close prices
            period: ADX period
        
        Returns:
            ADX values
        """
        # Calculate +DM and -DM
        up_move = high.diff()
        down_move = -low.diff()
        
        plus_dm = up_move.where((up_move > down_move) & (up_move > 0), 0)
        minus_dm = down_move.where((down_move > up_move) & (down_move > 0), 0)
        
        # Calculate ATR
        atr = TechnicalIndicators.atr(high, low, close, period)
        
        # Calculate +DI and -DI
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
        
        # Calculate DX and ADX
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()
        
        return adx
    
    @staticmethod
    def obv(close: pd.Series, volume: pd.Series) -> pd.Series:
        """
        On-Balance Volume
        
        Args:
            close: Close prices
            volume: Volume data
        
        Returns:
            OBV values
        """
        obv = (np.sign(close.diff()) * volume).fillna(0).cumsum()
        return obv
    
    @staticmethod
    def mfi(
        high: pd.Series,
        low: pd.Series,
        close: pd.Series,
        volume: pd.Series,
        period: int = 14
    ) -> pd.Series:
        """
        Money Flow Index
        
        Args:
            high: High prices
            low: Low prices
            close: Close prices
            volume: Volume data
            period: MFI period
        
        Returns:
            MFI values (0-100)
        """
        typical_price = (high + low + close) / 3
        money_flow = typical_price * volume
        
        positive_flow = money_flow.where(typical_price > typical_price.shift(), 0)
        negative_flow = money_flow.where(typical_price < typical_price.shift(), 0)
        
        positive_mf = positive_flow.rolling(window=period).sum()
        negative_mf = negative_flow.rolling(window=period).sum()
        
        mfi = 100 - (100 / (1 + positive_mf / negative_mf))
        
        return mfi
    
    @staticmethod
    def calculate_all(df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate all common indicators for a DataFrame
        
        Args:
            df: DataFrame with OHLCV data
        
        Returns:
            DataFrame with added indicator columns
        """
        result = df.copy()
        
        # Moving Averages
        for period in [7, 20, 50, 100, 200]:
            result[f'sma_{period}'] = TechnicalIndicators.sma(result['close'], period)
            result[f'ema_{period}'] = TechnicalIndicators.ema(result['close'], period)
        
        # EMA 12 and 26 for MACD and chart display
        result['ema_12'] = TechnicalIndicators.ema(result['close'], 12)
        result['ema_26'] = TechnicalIndicators.ema(result['close'], 26)
        
        # RSI
        result['rsi'] = TechnicalIndicators.rsi(result['close'])
        
        # MACD
        macd, signal, hist = TechnicalIndicators.macd(result['close'])
        result['macd'] = macd
        result['macd_signal'] = signal
        result['macd_histogram'] = hist
        
        # Bollinger Bands
        bb_upper, bb_middle, bb_lower = TechnicalIndicators.bollinger_bands(result['close'])
        result['bb_upper'] = bb_upper
        result['bb_middle'] = bb_middle
        result['bb_lower'] = bb_lower
        
        # Stochastic
        stoch_k, stoch_d = TechnicalIndicators.stochastic(
            result['high'], result['low'], result['close']
        )
        result['stoch_k'] = stoch_k
        result['stoch_d'] = stoch_d
        
        # ATR & ADX
        result['atr'] = TechnicalIndicators.atr(
            result['high'], result['low'], result['close']
        )
        result['adx'] = TechnicalIndicators.adx(
            result['high'], result['low'], result['close']
        )
        
        # Volume indicators
        result['obv'] = TechnicalIndicators.obv(result['close'], result['volume'])
        result['mfi'] = TechnicalIndicators.mfi(
            result['high'], result['low'], result['close'], result['volume']
        )
        
        return result
