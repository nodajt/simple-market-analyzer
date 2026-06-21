# Report Generator Module
# Generates HTML reports with charts and formatted text reports

import os
import pandas as pd
from datetime import datetime
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg
from yfinance import Ticker


class ReportGenerator:
    """Generates text and HTML reports for stock analysis."""
    
    def __init__(self, report_dir: str = 'reports'):
        self.report_dir = report_dir
        os.makedirs(report_dir, exist_ok=True)
        
    def generate_text_report(self, data: dict) -> str:
        """Generate a formatted text report."""
        ticker = data['ticker']
        info = data.get('info', {})
        history_1y = data.get('history_1y')
        from utils.data_fetcher import calculate_performance_metrics
        perf_metrics = calculate_performance_metrics(history_1y) if history_1y is not None and not history_1y.empty else None
        
        # Get key metrics
        market_cap = info.get('marketCap', 'N/A')
        pe_ratio = info.get('trailingPE', info.get('forwardPE', 'N/A'))
        dividend_yield = info.get('dividendYield', 'N/A')
        beta = info.get('beta', 'N/A')
        
        # Price data
        current_price = info.get('currentPrice', 'N/A')
        day_range = info.get('dayRange', ['N/A', 'N/A'])
        year_high = info.get('fiftyTwoWeekHigh', 'N/A')
        year_low = info.get('fiftyTwoWeekLow', 'N/A')
        
        # Build report
        lines = [
            "=" * 60,
            f"STOCK ANALYSIS REPORT - {ticker}",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} UTC",
            "=" * 60,
            "",
            "COMPANY INFORMATION:",
            "-" * 40,
            f"Company Name: {info.get('longName', info.get('shortName', ticker.upper()))}",
            f"Sector: {info.get('sector', 'N/A') or info.get('industry', 'N/A')}",
            f"Industry: {info.get('industry', 'N/A')}",
            "",
            "KEY METRICS:",
            "-" * 40,
            f"Current Price: ${current_price if current_price else 'N/A' if not isinstance(current_price, str) else current_price}",
            f"Market Cap: ${market_cap if market_cap else 'N/A'}",
            f"P/E Ratio (Trailing): {pe_ratio if pe_ratio and isinstance(pe_ratio, (int, float)) else pe_ratio or 'N/A'}",
            f"P/E Ratio (Forward): {info.get('forwardPE', 'N/A')}",
            f"Dividend Yield: {dividend_yield}%",
            f"Beta: {beta}",
            "",
            "PRICE DATA:",
            "-" * 40,
            f"52-Week High: ${year_high if year_high and isinstance(year_high, (int, float)) else year_high or 'N/A'}",
            f"52-Week Low: ${year_low if year_low and isinstance(year_low, (int, float)) else year_low or 'N/A'}",
            f"Day Range: {day_range[0] if day_range and len(day_range) > 1 else 'N/A'} - {day_range[1] if day_range and len(day_range) > 2 else day_range[2] if len(day_range) > 2 else 'N/A' or 'N/A'}",
            "",
        ]
        
        # Add performance summary if available
        if perf_metrics:
            lines.extend([
                "PERFORMANCE SUMMARY (Last Year):",
                "-" * 40,
                f"Start Price: ${perf_metrics.get('start_price', 'N/A') or info.get('previousClose', 'N/A')}",
                f"End Price: ${perf_metrics.get('end_price', current_price)}",
                f"Change: {perf_metrics.get('change_pct', 0):+.2f}%",
                "",
            ])
        
        # Technical indicators (if available)
        if history_1y is not None and not history_1y.empty:
            lines.append("TECHNICAL ANALYSIS:")
            lines.append("-" * 40)
            
            close_prices = history_1y['Close']
            sma20 = self._calculate_sma(close_prices, 20)
            sma50 = self._calculate_sma(close_prices, 50)
            
            if not pd.isna(sma20):
                lines.extend([
                    f"20-day SMA: ${sma20:.2f}",
                    f"50-day SMA: ${sma50:.2f}" if sma50 is not None else "",
                ])
            
            rsi = self._calculate_rsi(close_prices, 14)
            if rsi is not None:
                lines.append(f"RSI (14): {rsi:.2f}")
            
            macd, signal, hist = self._calculate_macd(close_prices)
            if macd is not None:
                lines.extend([
                    f"MACD: {macd:.3f}",
                    f"Signal Line: {signal:.3f}",
                    f"Histogram: {hist:.3f}",
                ])
            
            lines.append("")
        
        return "\n".join(lines)
    
    def generate_html_report(self, data: dict) -> str:
        """Generate an HTML report with charts."""
        ticker = data['ticker']
        info = data.get('info', {})
        history_1y = data.get('history_1y')
        
        # Prepare chart data
        close_prices = history_1y['Close'].values if history_1y is not None and not history_1y.empty else []
        dates = history_1y.index.strftime('%Y-%m-%d').values if history_1y is not None and not history_1y.empty else []
        
        # Generate HTML
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stock Analysis Report - {ticker}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #1a1a2e; color: #eee; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        h1 {{ text-align: center; color: #4fc3f7; margin-bottom: 20px; font-size: 2.5em; }}
        h2 {{ border-bottom: 2px solid #4fc3f7; padding-bottom: 10px; margin: 30px 0 15px; color: #81d4fa; }}
        .info-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; padding: 20px; }}
        .info-card {{ background: #16213e; border-radius: 10px; padding: 20px; border: 1px solid #0f3460; }}
        .info-label {{ color: #81d4fa; font-size: 0.9em; text-transform: uppercase; }}
        .info-value {{ color: #fff; font-size: 1.2em; margin-top: 5px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; background: #16213e; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #0f3460; }}
        th {{ background: #0f3460; color: #81d4fa; font-weight: bold; }}
        .chart-container {{ max-width: 900px; margin: 20px auto; padding: 20px; background: #16213e; border-radius: 10px; }}
        button {{ background: #4fc3f7; color: #1a1a2e; border: none; padding: 15px 30px; font-size: 1em; border-radius: 8px; cursor: pointer; margin-top: 20px; }}
        button:hover {{ background: #29b6f6; }}
        .positive {{ color: #4caf50; }}
        .negative {{ color: #f44336; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📈 Stock Analysis Report - {ticker}</h1>
        <p style="text-align: center; color: #81d4fa;">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')} UTC</p>
"""
        
        # Add info grid
        current_price = info.get('currentPrice', 'N/A')
        market_cap = info.get('marketCap', 'N/A')
        pe_ratio = info.get('trailingPE', info.get('forwardPE', 'N/A'))
        dividend_yield = info.get('dividendYield', '0')
        beta = info.get('beta', 'N/A')
        
        html += f"""
        <div class="info-grid">
            <div class="info-card">
                <div class="info-label">Current Price</div>
                <div class="info-value">${current_price if current_price else 'N/A'}</div>
            </div>
            <div class="info-card">
                <div class="info-label">Market Cap</div>
                <div class="info-value">${market_cap if market_cap and not isinstance(market_cap, str) else market_cap or 'N/A'}</div>
            </div>
            <div class="info-card">
                <div class="info-label">P/E Ratio</div>
                <div class="info-value">{pe_ratio if pe_ratio and isinstance(pe_ratio, (int, float)) else pe_ratio or 'N/A'}</div>
            </div>
            <div class="info-card">
                <div class="info-label">Dividend Yield</div>
                <div class="info-value">{dividend_yield}%</div>
            </div>
            <div class="info-card">
                <div class="info-label">Beta</div>
                <div class="info-value">{beta}</div>
            </div>
        </div>
"""
        
        # Add technical indicators
        if history_1y is not None and not history_1y.empty:
            html += """
        <h2>Technical Indicators</h2>
        """
            
            sma20 = self._calculate_sma(history_1y['Close'], 20)
            sma50 = self._calculate_sma(history_1y['Close'], 50)
            
            sma20_str = f"${sma20:.2f}" if not pd.isna(sma20) else "N/A"
            sma50_str = f"${sma50:.2f}" if sma50 is not None and not pd.isna(sma50) else "N/A"
            html += f"""
        <div class="info-grid">
            <div class="info-card"><div class="info-label">SMA (20)</div><div class="info-value">{sma20_str}</div></div>
            <div class="info-card"><div class="info-label">SMA (50)</div><div class="info-value">{sma50_str}</div></div>
        </div>
"""
            
            rsi = self._calculate_rsi(history_1y['Close'], 14)
            if rsi is not None:
                rsi_class = "positive" if rsi < 50 else "negative" if rsi > 50 else ""
                html += f"""
        <div class="info-grid">
            <div class="info-card"><div class="info-label">RSI (14)</div><div class="info-value {rsi_class}">{rsi:.2f}</div></div>
        </div>
"""
            
            macd, signal, hist = self._calculate_macd(history_1y['Close'])
            if macd is not None:
                html += f"""
        <div class="info-grid">
            <div class="info-card"><div class="info-label">MACD</div><div class="info-value">{macd:.3f}</div></div>
            <div class="info-card"><div class="info-label">Signal</div><div class="info-value">{signal:.3f}</div></div>
            <div class="info-card"><div class="info-label">Histogram</div><div class="info-value">{hist:.3f}</div></div>
        </div>
"""
        
        # Add price chart (PNG embedded)
        html += """
        <h2>Price History (1 Year)</h2>
        <div class="chart-container">
            <img src="data:image/png;base64,{}" alt="Stock Price Chart">
        </div>
"""
        
        # Add summary section
        history_1y = data.get('history_1y')
        if history_1y is not None and not history_1y.empty:
            dates_list = history_1y.index.strftime('%Y-%m-%d').tolist()
            html += f'<table><tr><th>Date</th><th>Open</th><th>High</th><th>Low</th><th>Close</th></tr>'
            for date, open_p, high, low, close in zip(dates_list, history_1y['Open'], history_1y['High'], history_1y['Low'], history_1y['Close']):
                change = (close - open_p) / open_p * 100 if open_p else 0
                color_class = "positive" if change >= 0 else "negative"
                html += f'<tr><td>{date}</td><td>${open_p:.2f}</td><td>${high:.2f}</td><td>${low:.2f}</td><td class="{color_class}">${close:.2f}</td></tr>'
            html += '</table>'
        
        html += f"""
    </div>
</body>
</html>
"""
        
        return html
    
    def _calculate_sma(self, prices: pd.Series, period: int) -> float:
        """Calculate Simple Moving Average."""
        if len(prices) < period:
            return None
        return prices[-period:].mean()
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> float:
        """Calculate Relative Strength Index."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period, min_periods=1).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period, min_periods=1).mean()
        loss_last = loss.iloc[-1]
        rs = gain.iloc[-1] / loss_last if loss_last != 0 else float('inf')
        return 100 - (100 / (1 + rs))
    
    def _calculate_macd(self, prices: pd.Series, fast: int = 12, slow: int = 26) -> tuple:
        """Calculate MACD."""
        ema_fast = prices.ewm(span=fast, adjust=False).mean()
        ema_slow = prices.ewm(span=slow, adjust=False).mean()
        macd = ema_fast - ema_slow
        signal = macd.ewm(span=9, adjust=False).mean()
        hist = macd - signal
        
        return (macd.iloc[-1], signal.iloc[-1], hist.iloc[-1])


# Generate chart and save to file
def generate_and_save_chart(history_1y: pd.DataFrame, filename: str) -> str:
    """Generate price chart and save to PNG."""
    if history_1y.empty:
        return None
    
    fig = Figure(figsize=(9, 5))
    canvas = FigureCanvasAgg(fig)
    
    ax = fig.add_subplot(111)
    ax.plot(history_1y.index, history_1y['Close'], label='Close', linewidth=2, color='#4fc3f7')
    ax.fill_between(history_1y.index, history_1y['Low'], history_1y['High'], alpha=0.1)
    
    ax.set_title('Stock Price History (1 Year)', fontsize=14, fontweight='bold')
    ax.set_ylabel('Price ($)')
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    canvas.print_png(filename)
    return filename