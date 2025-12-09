"""
Fundamental Analysis
Tools for analyzing company fundamentals and financial ratios
"""
from typing import Dict, Any, Optional
import pandas as pd


class FundamentalAnalysis:
    """Fundamental analysis calculations"""
    
    @staticmethod
    def pe_ratio(price: float, eps: float) -> Optional[float]:
        """
        Price-to-Earnings Ratio
        
        Args:
            price: Current stock price
            eps: Earnings Per Share
        
        Returns:
            P/E ratio or None if EPS is zero
        """
        if eps == 0:
            return None
        return price / eps
    
    @staticmethod
    def pb_ratio(price: float, book_value_per_share: float) -> Optional[float]:
        """
        Price-to-Book Ratio
        
        Args:
            price: Current stock price
            book_value_per_share: Book value per share
        
        Returns:
            P/B ratio
        """
        if book_value_per_share == 0:
            return None
        return price / book_value_per_share
    
    @staticmethod
    def peg_ratio(pe_ratio: float, earnings_growth_rate: float) -> Optional[float]:
        """
        Price/Earnings to Growth Ratio
        
        Args:
            pe_ratio: P/E ratio
            earnings_growth_rate: Annual earnings growth rate (%)
        
        Returns:
            PEG ratio
        """
        if earnings_growth_rate == 0:
            return None
        return pe_ratio / earnings_growth_rate
    
    @staticmethod
    def roe(net_income: float, shareholders_equity: float) -> Optional[float]:
        """
        Return on Equity
        
        Args:
            net_income: Net income
            shareholders_equity: Total shareholders' equity
        
        Returns:
            ROE as percentage
        """
        if shareholders_equity == 0:
            return None
        return (net_income / shareholders_equity) * 100
    
    @staticmethod
    def roa(net_income: float, total_assets: float) -> Optional[float]:
        """
        Return on Assets
        
        Args:
            net_income: Net income
            total_assets: Total assets
        
        Returns:
            ROA as percentage
        """
        if total_assets == 0:
            return None
        return (net_income / total_assets) * 100
    
    @staticmethod
    def debt_to_equity(total_debt: float, shareholders_equity: float) -> Optional[float]:
        """
        Debt-to-Equity Ratio
        
        Args:
            total_debt: Total debt
            shareholders_equity: Total shareholders' equity
        
        Returns:
            D/E ratio
        """
        if shareholders_equity == 0:
            return None
        return total_debt / shareholders_equity
    
    @staticmethod
    def current_ratio(current_assets: float, current_liabilities: float) -> Optional[float]:
        """
        Current Ratio (Liquidity measure)
        
        Args:
            current_assets: Current assets
            current_liabilities: Current liabilities
        
        Returns:
            Current ratio
        """
        if current_liabilities == 0:
            return None
        return current_assets / current_liabilities
    
    @staticmethod
    def dividend_yield(annual_dividend: float, price: float) -> Optional[float]:
        """
        Dividend Yield
        
        Args:
            annual_dividend: Annual dividend per share
            price: Current stock price
        
        Returns:
            Dividend yield as percentage
        """
        if price == 0:
            return None
        return (annual_dividend / price) * 100
    
    @staticmethod
    def eps_growth(current_eps: float, previous_eps: float) -> Optional[float]:
        """
        EPS Growth Rate
        
        Args:
            current_eps: Current period EPS
            previous_eps: Previous period EPS
        
        Returns:
            Growth rate as percentage
        """
        if previous_eps == 0:
            return None
        return ((current_eps - previous_eps) / abs(previous_eps)) * 100
    
    @staticmethod
    def analyze_company(financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform comprehensive fundamental analysis
        
        Args:
            financial_data: Dictionary containing financial metrics
        
        Returns:
            Dictionary with calculated ratios and analysis
        """
        result = {
            'ratios': {},
            'scores': {},
            'signals': []
        }
        
        # Extract data
        price = financial_data.get('price', 0)
        eps = financial_data.get('eps', 0)
        book_value_per_share = financial_data.get('book_value_per_share', 0)
        net_income = financial_data.get('net_income', 0)
        total_assets = financial_data.get('total_assets', 0)
        shareholders_equity = financial_data.get('shareholders_equity', 0)
        total_debt = financial_data.get('total_debt', 0)
        current_assets = financial_data.get('current_assets', 0)
        current_liabilities = financial_data.get('current_liabilities', 0)
        annual_dividend = financial_data.get('annual_dividend', 0)
        earnings_growth = financial_data.get('earnings_growth_rate', 0)
        
        # Calculate ratios
        pe = FundamentalAnalysis.pe_ratio(price, eps)
        if pe:
            result['ratios']['pe_ratio'] = round(pe, 2)
        
        pb = FundamentalAnalysis.pb_ratio(price, book_value_per_share)
        if pb:
            result['ratios']['pb_ratio'] = round(pb, 2)
        
        if pe and earnings_growth:
            peg = FundamentalAnalysis.peg_ratio(pe, earnings_growth)
            if peg:
                result['ratios']['peg_ratio'] = round(peg, 2)
        
        roe_val = FundamentalAnalysis.roe(net_income, shareholders_equity)
        if roe_val:
            result['ratios']['roe'] = round(roe_val, 2)
        
        roa_val = FundamentalAnalysis.roa(net_income, total_assets)
        if roa_val:
            result['ratios']['roa'] = round(roa_val, 2)
        
        de = FundamentalAnalysis.debt_to_equity(total_debt, shareholders_equity)
        if de:
            result['ratios']['debt_to_equity'] = round(de, 2)
        
        cr = FundamentalAnalysis.current_ratio(current_assets, current_liabilities)
        if cr:
            result['ratios']['current_ratio'] = round(cr, 2)
        
        dy = FundamentalAnalysis.dividend_yield(annual_dividend, price)
        if dy:
            result['ratios']['dividend_yield'] = round(dy, 2)
        
        # Generate signals
        if pe and pe < 15:
            result['signals'].append('Low P/E ratio (potentially undervalued)')
        elif pe and pe > 30:
            result['signals'].append('High P/E ratio (potentially overvalued)')
        
        if roe_val and roe_val > 15:
            result['signals'].append('Good ROE (>15%)')
        
        if de and de < 0.5:
            result['signals'].append('Low debt-to-equity (financially stable)')
        elif de and de > 2:
            result['signals'].append('High debt-to-equity (high leverage)')
        
        if cr and cr > 1.5:
            result['signals'].append('Good liquidity (CR > 1.5)')
        elif cr and cr < 1:
            result['signals'].append('Low liquidity (CR < 1)')
        
        return result
