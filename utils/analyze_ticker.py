from utils.data_fetcher import fetch_stock_data, get_company_name, calculate_performance_metrics

def analyze_ticker(ticker: str, args, basic=False):
    """
    Analyzes a stock ticker and returns performance metrics.
    
    Args:
        ticker: Stock ticker symbol
        args: Command-line arguments
        basic: Whether to return basic metrics only
    
    Returns:
        Dictionary of analysis results
    """
    # Fetch stock data
    data = fetch_stock_data(ticker)
    
    # Get company name
    company_name = get_company_name(ticker)
    
    # Calculate metrics
    metrics = calculate_performance_metrics(data['history_1mo'])
    
    return {
        'ticker': ticker,
        'company': company_name,
        'metrics': metrics
    }