# Stock Market Analyzer - Main Application
# A Python CLI tool to analyze stocks with comprehensive reports

import argparse
import sys
import os
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, os.getcwd())

from utils.data_fetcher import fetch_stock_data, calculate_performance_metrics
from utils.report_generator import ReportGenerator


def format_currency(value):
    """Format number as currency."""
    if value is None:
        return "N/A"
    try:
        return f"${value:,.2f}"
    except (TypeError, ValueError):
        return str(value)


def format_percentage(value):
    """Format number as percentage."""
    if value is None or (isinstance(value, str) and str(value).upper() in ['N/A', 'NaN']):
        return "N/A"
    try:
        num = float(value)
        return f"{num:.2f}%"
    except (ValueError, TypeError):
        return str(value)


def format_number(value):
    """Format number with commas."""
    if value is None or (isinstance(value, str) and str(value).upper() in ['N/A', 'NaN']):
        return "N/A"
    try:
        num = float(value)
        return f"{num:,}"
    except (ValueError, TypeError):
        return str(value)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Stock Market Analyzer - Get comprehensive stock analysis reports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python stock_analyser.py AAPL
  python stock_analyser.py MSFT --output-html
  python stock_analyser.py TSLA --output-text --no-chart
  python stock_analyser.py GOOGL -l report.html
        
To get help on a specific command, run: python stock_analyser.py -h
        """
    )
    
    parser.add_argument(
        'ticker',
        nargs='?',
        help='Stock ticker symbol (e.g., AAPL, MSFT, TSLA). Can also be provided via -l flag.'
    )
    
    parser.add_argument(
        '-l', '--list',
        action='store_true',
        help='List available tickers and exit'
    )
    
    parser.add_argument(
        '-o', '--output',
        choices=['html', 'text', 'both'],
        default='both',
        help='Output format: html, text, or both (default: both)'
    )
    
    parser.add_argument(
        '-t', '--text-file',
        action='store_true',
        help='Save text report to file instead of printing'
    )
    
    parser.add_argument(
        '-c', '--chart',
        action='store_true',
        default=True,
        help='Generate chart (default: enabled)'
    )
    
    parser.add_argument(
        '-b', '--basic',
        action='store_true',
        help='Basic analysis mode - shows only essential metrics'
    )
    
    parser.add_argument(
        '-H', '--html-file',      # was '-h' — reserved by argparse for help
        action='store_true',
        default=True,
        help='Save HTML report to file (default: enabled)'
    )
    
    return parser.parse_args()


def analyze_ticker(ticker: str, args, basic: bool = False) -> None:
    """
    Analyze a stock ticker and display/report the results.
    
    Args:
        ticker: Stock ticker symbol
        basic: If True, show only basic metrics
    """
    print("\n" + "=" * 60)
    print(f" 📊 STOCK ANALYZER - {ticker.upper()}")
    print("=" * 60)
    
    # Fetch data
    print("\n🔄 Fetching data from Yahoo Finance...")
    try:
        data = fetch_stock_data(ticker)
    except Exception as e:
        print(f"\n❌ Error fetching data: {e}")
        print("Please check the ticker symbol is valid and try again.")
        sys.exit(1)
    
    # Company info header
    company_name = data['info'].get('longName', data['info'].get('shortName', f"{ticker} Inc."))
    sector = data['info'].get('sector', 'N/A')
    industry = data['info'].get('industry', 'N/A')
    
    print(f"\n🏢 {company_name}")
    print(f"   Sector: {sector or 'N/A'} | Industry: {industry or 'N/A'}")
    
    # Key Metrics (always show these)
    current_price = data['info'].get('currentPrice')
    market_cap = data['info'].get('marketCap')
    pe_trailing = data['info'].get('trailingPE', data['info'].get('forwardPE'))
    forward_pe = data['info'].get('forwardPE')
    dividend_yield = data['info'].get('dividendYield')
    beta = data['info'].get('beta')
    
    print("\n💰 KEY METRICS")
    print("-" * 40)
    print(f"   Current Price     : {format_currency(current_price)}")
    print(f"   Market Cap        : {format_currency(market_cap)}")
    print(f"   P/E Ratio (Trailing): {format_number(pe_trailing)}")
    if forward_pe and not str(forward_pe).upper() == str(pe_trailing):
        print(f"   P/E Ratio (Forward)  : {format_number(forward_pe)}")
    print(f"   Dividend Yield     : {format_percentage(dividend_yield)}")
    print(f"   Beta               : {format_number(beta)}")
    
    # Price Data
    fiftyTwoWeekHigh = data['info'].get('fiftyTwoWeekHigh')
    fiftyTwoWeekLow = data['info'].get('fiftyTwoWeekLow')
    previousClose = data['info'].get('previousClose')
    
    if current_price and (fiftyTwoWeekHigh or previousClose):
        if previousClose:
            change_abs = current_price - previousClose
            change_pct = ((current_price - previousClose) / previousClose) * 100
            change_class = "🟢" if change_abs >= 0 else "🔴"
            print(f"\n   Previous Close     : ${format_currency(previousClose)}")
            print(f"   Change Today       : {change_class} {format_currency(abs(change_abs))} ({format_percentage(abs(change_pct))})")
        if fiftyTwoWeekHigh or fiftyTwoWeekLow:
            print("\n   52-Week Range:")
            print(f"      High             : ${format_currency(fiftyTwoWeekHigh)}")
            print(f"      Low              : ${format_currency(fiftyTwoWeekLow)}")
    
    # Technical Analysis
    history_1y = data.get('history_1y')
    if history_1y is not None and not history_1y.empty:
        close_prices = history_1y['Close']
        
        # SMA calculations
        sma20 = history_1y['Close'].rolling(window=20, min_periods=1).mean()
        sma50 = history_1y['Close'].rolling(window=50, min_periods=1).mean()
        
        print("\n📈 TECHNICAL ANALYSIS")
        print("-" * 40)
        if len(close_prices) >= 20:
            print(f"   20-day SMA         : ${sma20.iloc[-1]:.2f}")
            current_vs_sma20 = ((close_prices.iloc[-1] - sma20.iloc[-1]) / sma20.iloc[-1]) * 100
            sma_trend = "📈 Bullish" if close_prices.iloc[-1] > sma20.iloc[-1] else "📉 Bearish"
            print(f"   Current vs SMA20   : {current_vs_sma20:+.2f}% ({sma_trend})")
        
        if len(close_prices) >= 50:
            print(f"   50-day SMA         : ${sma50.iloc[-1]:.2f}")
            current_vs_sma50 = ((close_prices.iloc[-1] - sma50.iloc[-1]) / sma50.iloc[-1]) * 100
            sma_trend50 = "📈 Bullish" if close_prices.iloc[-1] > sma50.iloc[-1] else "📉 Bearish"
            print(f"   Current vs SMA50   : {current_vs_sma50:+.2f}% ({sma_trend50})")
        
        # RSI
        delta = close_prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14, min_periods=1).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14, min_periods=1).mean()
        loss_last = loss.iloc[-1]
        rs = gain.iloc[-1] / loss_last if loss_last != 0 else float('inf')
        rsi = 100 - (100 / (1 + rs))
        print(f"   RSI (14)           : {rsi:.2f}")
        rsi_status = "Neutral" if 45 <= rsi <= 55 else ("Overtold" if rsi < 30 or rsi > 70 else "")
        print(f"                       Status: {rsi_status}")
        
        # MACD
        ema_fast = close_prices.ewm(span=12, adjust=False).mean()
        ema_slow = close_prices.ewm(span=26, adjust=False).mean()
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=9, adjust=False).mean()
        histogram = macd_line - signal_line
        
        print(f"   MACD               : {histogram.iloc[-1]:.3f}")
        print(f"   Signal Line        : {signal_line.iloc[-1]:.3f}")
        
        if macd_line.iloc[-1] > signal_line.iloc[-1]:
            print(f"                       Status: 📈 Bullish")
        else:
            print(f"                       Status: 📉 Bearish")
        
        # Price Performance
        perf_metrics = calculate_performance_metrics(history_1y)
        if perf_metrics:
            print("\n📊 PERFORMANCE SUMMARY (Last Year)")
            print("-" * 40)
            start_price = perf_metrics.get('start_price') or previousClose
            end_price = perf_metrics.get('end_price') or current_price
            
            if start_price and end_price:
                pct_change = ((end_price - start_price) / start_price) * 100
                print(f"   Start Price        : ${format_currency(start_price)}")
                print(f"   End Price          : ${format_currency(end_price)}")
                change_dir = "🟢" if pct_change >= 0 else "🔴"
                print(f"   Change             : {change_dir} {format_currency(abs(end_price - start_price))} ({pct_change:+.2f}%)")
    
    # Shareholders (if available)
    shares_holders = data.get('shares_holders')
    if shares_holders is not None and not shares_holders.empty:
        print("\n👥 TOP SHAREHOLDERS")
        print("-" * 40)
        for idx, (label, row) in enumerate(shares_holders.head(5).iterrows(), 1):
            value = row.iloc[0]
            label_str = str(label).replace('PercentHeld', '% Held').replace('Count', ' Count')
            formatted_val = f"{value:.2f}%" if 'Percent' in str(label) else f"{value:,.2f}"
            print(f"   {idx}. {label_str}: {formatted_val}")
    
    # Print report if output format includes text or HTML
    generator = ReportGenerator()
    text_report = generator.generate_text_report(data)
    html_report = generator.generate_html_report(data)
    
    # Output to file or print
    output_format = 'html' if args.output == 'html' else ('text' if args.output == 'text' else 'both')
    
    if output_format in ['html', 'both']:
        # Save HTML report
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        html_filename = f"{timestamp}_{ticker.upper()}_report.html"
        html_path = os.path.join('reports', html_filename)
        
        with open(html_path, 'w') as f:
            f.write(html_report)
        
        if args.output == 'html':
            print("\n📄 HTML Report generated (opening in browser)...")
        else:
            print(f"\n💾 HTML report saved to: {html_path}")
    
    if output_format in ['text', 'both']:
        if args.text_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            text_filename = f"{timestamp}_{ticker.upper()}_report.txt"
            text_path = os.path.join('reports', text_filename)
            
            with open(text_path, 'w') as f:
                f.write(text_report)
            
            print(f"\n📄 Text report saved to: {text_path}")
        else:
            if not basic:
                print("\n" + "-" * 60)
                print("DETAILED REPORT:")
                print("-" * 60)
                print(text_report)
    
    # Open HTML in browser if requested and on non-headless system
    if args.html_file and output_format == 'html':
        from webbrowser import open as web_open
        try:
            web_open(f"file://{os.path.abspath(html_path)}", new=2)
            print("\n🌐 Opening HTML report in your default browser...")
        except Exception:
            pass
    
    # Separator
    print("\n" + "=" * 60)
    print("Analysis complete!")
    print("=" * 60 + "\n")


def list_tickers():
    """List commonly analyzed tickers."""
    print("\n" + "=" * 60)
    print("📋 COMMONLY ANALYZED STOCKS")
    print("=" * 60 + "\n")
    
    tickers = [
        ("AAPL", "Apple Inc."),
        ("MSFT", "Microsoft Corporation"),
        ("GOOGL", "Alphabet Inc."),
        ("AMZN", "Amazon.com Inc."),
        ("META", "Meta Platforms Inc."),
        ("TSLA", "Tesla Inc."),
        ("NVDA", "NVIDIA Corporation"),
        ("BRK.B", "Berkshire Hathaway Inc."),
        ("JPM", "JPMorgan Chase & Co."),
        ("V", "Visa Inc."),
        ("WMT", "Walmart Inc."),
        ("JNJ", "Johnson & Johnson"),
        ("PG", "Procter & Gamble Co."),
        ("MA", "Mastercard Inc."),
        ("UNH", "UnitedHealth Group Inc."),
    ]
    
    print(f"{'Ticker':<10} {'Company Name':<35}")
    print("-" * 45)
    for ticker, name in tickers:
        print(f"{ticker:<10} {name:<35}")
    print("=" * 60 + "\n")


def main():
    """Main entry point."""
    args = parse_args()
    
    # Handle list mode
    if args.list:
        list_tickers()
        sys.exit(0)
    
    # Handle ticker input
    if not args.ticker:
        print("\n📊 Stock Market Analyzer")
        print("=" * 60)
        print("\nTo analyze a stock, provide a ticker symbol:\n")
        print("   python stock_analyser.py AAPL\n")
        print("Or use the -l flag to list commonly analyzed stocks:")
        print("   python stock_analyser.py -l\n")
        
        # Quick picker menu
        print("=" * 60)
        print("📋 QUICK STOCK PICKER")
        print("=" * 60 + "\n")
        
        tickers = [
            ("AAPL", "Apple"),
            ("MSFT", "Microsoft"),
            ("GOOGL", "Alphabet/Google"),
            ("AMZN", "Amazon"),
            ("META", "Meta/Facebook"),
            ("TSLA", "Tesla"),
            ("NVDA", "NVIDIA"),
        ]
        
        for i, (ticker, name) in enumerate(tickers, 1):
            print(f"   {i}. {ticker:<8} - {name}")
        print("   0. Cancel")
        print()
        
        try:
            choice = input("Select a stock number (or type your own ticker): ").strip()
            
            if choice == '0':
                sys.exit(0)
            
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(tickers):
                    args.ticker = tickers[idx][0]
                else:
                    print("Invalid selection. Using manual input mode.\n")
            
            if not args.ticker:
                args.ticker = input("Enter ticker symbol (e.g., AAPL): ").strip().upper()
                
                # Validate ticker
                try:
                    import yfinance as yf
                    stock = yf.Ticker(args.ticker)
                    info = stock.info
                    if not info or len(info) < 3:
                        print(f"\n❌ Invalid ticker: {args.ticker}")
                        sys.exit(1)
                except Exception as e:
                    print(f"\n❌ Error fetching data for {args.ticker}: {e}")
                    sys.exit(1)
        except KeyboardInterrupt:
            print("\n\nCancelled.")
            sys.exit(0)
    
    # Check if ticker is provided
    if not args.ticker:
        print("Error: No ticker symbol provided.")
        sys.exit(1)
    
    # Validate ticker before analysis
    try:
        import yfinance as yf
        stock = yf.Ticker(args.ticker)
        info = stock.info
        if not info or len(info) < 3:
            print(f"\n❌ Invalid ticker symbol: {args.ticker}")
            print("Please verify the ticker and try again.\n")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error fetching data for {args.ticker}: {e}")
        sys.exit(1)
    
    # Call the analysis function
    analyze_ticker(args.ticker, args, basic=args.basic)


if __name__ == "__main__":
    main()