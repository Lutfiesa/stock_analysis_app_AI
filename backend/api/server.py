"""
FastAPI Server for Stock Analysis App
Provides REST API endpoints for frontend
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional, List
import sys
from pathlib import Path
import pandas as pd

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.config.config import config
from backend.data_fetcher.twelve_data_fetcher import TwelveDataFetcher
from backend.analysis.technical_indicators import TechnicalIndicators
from backend.analysis.fundamental_analysis import FundamentalAnalysis

# Initialize FastAPI app
app = FastAPI(
    title="Stock Analysis API",
    description="API for Indonesia Stock Market Analysis",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize data fetchers
# Using Twelve Data as primary (free tier: 800 calls/day)
# Sectors.app removed due to paid requirement
twelve_data_fetcher = None

if config.TWELVEDATA_API_KEY:
    twelve_data_fetcher = TwelveDataFetcher(config.TWELVEDATA_API_KEY)

# Primary fetcher is now Twelve Data
primary_fetcher = twelve_data_fetcher


@app.on_event("startup")
async def startup_event():
    """Initialize on startup"""
    print("🚀 Stock Analysis API Starting...")
    print(f"📊 Environment: {config.APP_ENV}")
    print(f"🔑 Twelve Data API: {'✓ Configured' if twelve_data_fetcher else '✗ Not configured'}")
    if not twelve_data_fetcher:
        print("⚠️  Warning: No API key configured! Please set TWELVEDATA_API_KEY in .env")


@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "Stock Analysis API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "twelve_data_api": twelve_data_fetcher is not None
        }
    }


@app.get("/api/stocks/search")
async def search_stocks(q: str = Query(..., min_length=1)):
    """
    Search for stocks by symbol or name
    
    Args:
        q: Search query
    
    Returns:
        List of matching stocks
    """
    if not primary_fetcher:
        raise HTTPException(status_code=503, detail="No API configured. Please set TWELVEDATA_API_KEY in .env")
    
    try:
        results = primary_fetcher.search_stocks(q)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stocks/all")
async def get_all_stocks():
    """Get list of all available stocks"""
    if not primary_fetcher:
        raise HTTPException(status_code=503, detail="No API configured. Please set TWELVEDATA_API_KEY in .env")
    
    try:
        stocks = primary_fetcher.get_all_stocks()
        return {"stocks": stocks}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stock/{symbol}")
async def get_stock_data(
    symbol: str,
    interval: str = "1d",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """
    Get stock price data
    
    Args:
        symbol: Stock symbol
        interval: Data interval (1d, 1h, etc.)
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
    
    Returns:
        Stock price data
    """
    fetcher = primary_fetcher
    
    if not fetcher:
        raise HTTPException(status_code=503, detail="No data source configured")
    
    try:
        df = fetcher.get_stock_data(
            symbol=symbol.upper(),
            interval=interval,
            start_date=start_date,
            end_date=end_date
        )
        
        if df.empty:
            raise HTTPException(status_code=404, detail="No data found for symbol")
        
        # Convert to list of dicts
        data = df.to_dict('records')
        
        # Convert timestamps to strings
        for record in data:
            if 'timestamp' in record:
                record['timestamp'] = record['timestamp'].isoformat()
        
        return {
            "symbol": symbol.upper(),
            "interval": interval,
            "data": data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stock/{symbol}/info")
async def get_company_info(symbol: str):
    """
    Get company information
    
    Args:
        symbol: Stock symbol
    
    Returns:
        Company details
    """
    fetcher = primary_fetcher
    
    if not fetcher:
        raise HTTPException(status_code=503, detail="No data source configured")
    
    try:
        info = fetcher.get_company_info(symbol.upper())
        
        if not info:
            raise HTTPException(status_code=404, detail="Company info not found")
        
        return info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analysis/technical/{symbol}")
async def get_technical_analysis(
    symbol: str,
    interval: str = "1d",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """
    Get technical analysis with indicators
    
    Args:
        symbol: Stock symbol
        interval: Data interval
        start_date: Start date
        end_date: End date
    
    Returns:
        Price data with technical indicators
    """
    fetcher = primary_fetcher
    
    if not fetcher:
        raise HTTPException(status_code=503, detail="No data source configured")
    
    try:
        df = fetcher.get_stock_data(
            symbol=symbol.upper(),
            interval=interval,
            start_date=start_date,
            end_date=end_date
        )
        
        if df.empty:
            raise HTTPException(status_code=404, detail="No data found")
        
        # Calculate indicators
        df_with_indicators = TechnicalIndicators.calculate_all(df)
        
        # Replace NaN/Inf with None for JSON compatibility
        df_with_indicators = df_with_indicators.replace([float('inf'), float('-inf')], None)
        df_with_indicators = df_with_indicators.where(pd.notnull(df_with_indicators), None)
        
        # Convert to records
        data = df_with_indicators.to_dict('records')
        
        # Convert timestamps and clean NaN values
        for record in data:
            if 'timestamp' in record:
                try:
                    record['timestamp'] = record['timestamp'].isoformat()
                except:
                    record['timestamp'] = str(record['timestamp'])
            # Clean any remaining NaN values
            for key, value in record.items():
                if isinstance(value, float) and (pd.isna(value) or value != value):
                    record[key] = None
        
        # Get latest values for summary
        latest = df_with_indicators.iloc[-1]
        
        def safe_float(val):
            """Convert to float safely, return None for NaN/Inf"""
            if val is None or pd.isna(val):
                return None
            try:
                f = float(val)
                if f != f or f == float('inf') or f == float('-inf'):
                    return None
                return f
            except:
                return None
        
        summary = {
            'price': safe_float(latest.get('close')),
            'rsi': safe_float(latest.get('rsi')),
            'macd': safe_float(latest.get('macd')),
            'macd_signal': safe_float(latest.get('macd_signal')),
            'sma_20': safe_float(latest.get('sma_20')),
            'sma_50': safe_float(latest.get('sma_50')),
        }
        
        return {
            "symbol": symbol.upper(),
            "summary": summary,
            "data": data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/analysis/fundamental/{symbol}")
async def get_fundamental_analysis(symbol: str):
    """
    Get fundamental analysis
    
    Args:
        symbol: Stock symbol
    
    Returns:
        Fundamental ratios and analysis
    """
    if not primary_fetcher:
        raise HTTPException(status_code=503, detail="No API configured")
    
    try:
        # Get financials (limited in free tier)
        financials = primary_fetcher.get_financials(symbol.upper())
        
        if not financials:
            raise HTTPException(status_code=404, detail="Financial data not found")
        
        # Perform analysis (will be limited with free tier data)
        analysis = FundamentalAnalysis.analyze_company(financials)
        
        return {
            "symbol": symbol.upper(),
            "analysis": analysis,
            "raw_data": financials,
            "note": "Full fundamental data requires premium API subscription"
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    
    print(f"""
    ╔══════════════════════════════════════╗
    ║   Stock Analysis API Server          ║
    ║   Indonesia Market (IDX)             ║
    ╚══════════════════════════════════════╝
    
    🌐 Server: http://{config.BACKEND_HOST}:{config.BACKEND_PORT}
    📚 API Docs: http://{config.BACKEND_HOST}:{config.BACKEND_PORT}/docs
    """)
    
    uvicorn.run(
        "server:app",
        host=config.BACKEND_HOST,
        port=config.BACKEND_PORT,
        reload=config.DEBUG
    )
