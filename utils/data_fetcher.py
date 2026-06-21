# Stock Data Fetcher Module
# Fetches historical and fundamental data using yfinance

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta


def fetch_stock_data(ticker: str) -> dict:
    """
    Fetch comprehensive stock data from Yahoo Finance.
    
    Args:
        ticker: Stock ticker symbol (e.g., 'AAPL', 'MSFT')
    
    Returns:
        Dictionary containing all fetched data
    """
    stock = yf.Ticker(ticker)
    
    # Get basic info
    info = stock.info
    
    # Get historical prices
    period1mo = stock.history(period='1mo')
    period3mo = stock.history(period='3mo')
    period6mo = stock.history(period='6mo')
    period1y = stock.history(period='1y')
    
    # Get share holder info (optional, may fail if not available)
    try:
        shares_holders = stock.major_holders
    except Exception:
        shares_holders = None
    
    return {
        'ticker': ticker,
        'info': info,
        'history_1mo': period1mo if not period1mo.empty else None,
        'history_3mo': period3mo if not period3mo.empty else None,
        'history_6mo': period6mo if not period6mo.empty else None,
        'history_1y': period1y if not period1y.empty else None,
        'shares_holders': shares_holders
    }


def get_company_name(ticker: str) -> str:
    """Get company name from ticker."""
    stock = yf.Ticker(ticker)
    return stock.info.get('shortName', stock.info.get('longName', ticker.upper()))


def calculate_performance_metrics(history: pd.DataFrame) -> dict:
    """Calculate performance metrics from historical data."""
    if history.empty:
        return {'start': None, 'end': None}
    
    dates = history.index
    start_price = history['Close'].iloc[0]
    end_price = history['Close'].iloc[-1]
    low = history['Low'].min()
    high = history['High'].max()
    
    # Calculate percentage changes
    pct_change_1d = ((history['Close'].iloc[-1] / history['Close'].iloc[-2]) - 1) * 100 if len(history) > 1 else 0
    pct_change_5d = ((history['Close'].iloc[-1] / history['Close'].iloc[-6]) - 1) * 100 if len(history) >= 6 else 0
    pct_change_mtd = ((end_price / start_price) - 1) * 100
    
    # YTD calculation (from first trading day of current year)
    current_year = datetime.now().year
    try:
        ytd_data = history[history.index >= pd.Timestamp(f"{current_year}-01-01", tz=history.index.tz)]
    except (TypeError, AttributeError):
        ytd_data = history[history.index >= pd.Timestamp(f"{current_year}-01-01")]
    ytd_start = ytd_data['Close'].iloc[0] if not ytd_data.empty else None
    pct_ytd = ((end_price / ytd_start) - 1) * 100 if ytd_start else None
    
    return {
        'start_date': dates[0].strftime('%Y-%m-%d'),
        'end_date': dates[-1].strftime('%Y-%m-%d'),
        'start_price': start_price,
        'end_price': end_price,
        'low': low,
        'high': high,
        'change_absolute': end_price - start_price,
        'change_pct': pct_change_mtd,
        'ytd_change_pct': pct_ytd if ytd_start else None,
        'range_1m': high - low
    }


# Import pandas at module level to avoid circular import issues
