# 📊 Stock Market Analyzer

A Python CLI tool that provides comprehensive stock analysis reports using real-time market data from Yahoo Finance.

## Features

- **Key Financial Metrics**: Current price, market cap, P/E ratio, dividend yield, beta
- **Technical Analysis**: SMA (20-day, 50-day), RSI, MACD indicators
- **Performance Tracking**: Year-over-year price performance
- **Shareholder Analysis**: Top institutional shareholders
- **Report Generation**: HTML and text reports
- **Quick Stock Picker**: Easy selection from commonly analyzed stocks
- **Interactive Menu**: Type a ticker or select from the menu

## Installation

### Requirements

- Python 3.8+
- pip (Python package manager)

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Verify Installation

```bash
python stock_analyser.py --help
```

## Usage

### Basic Usage

Analyze a single stock:

```bash
python stock_analyser.py AAPL
```

### Interactive Mode (No Arguments)

Run without arguments for an interactive menu:

```bash
python stock_analyser.py
```

Type your ticker symbol or select from the quick picker.

### Command Line Options

| Option | Description |
|--------|-------------|
| `-l` / `--list` | List commonly analyzed stocks and exit |
| `-o` / `--output` | Output format: html, text, or both |
| `-t` / `--text-file` | Save text report to file instead of printing |
| `-b` / `--basic` | Basic analysis mode (only essential metrics) |
| `-h` / `--html-file` | Save HTML report to file |

### Examples

```bash
# Analyze Apple with full report and open in browser
python stock_analyser.py AAPL

# Get HTML-only report for Microsoft
python stock_analyser.py MSFT --output-html

# Get text report for Tesla (no chart, save as file)
python stock_analyser.py TSLA -o text -t

# List commonly analyzed stocks
python stock_analyser.py -l

# Basic analysis of Google
python stock_analyser.py GOOGL --basic
```

### HTML Report Features

When you run the analyzer, it generates a beautiful HTML report that includes:

- 📈 Interactive charts (Plotly)
- 💰 Key metrics table
- 📊 Price performance with line charts
- 🔬 Technical indicators
- 👥 Institutional shareholders
- ℹ️ Company information

## Project Structure

```
market_analyser/
├── stock_analyser.py      # Main application
├── requirements.txt        # Python dependencies
├── utils/
│   ├── __init__.py
│   ├── data_fetcher.py    # Data fetching from Yahoo Finance
│   └── report_generator.py # Report generation (HTML/Text)
├── reports/                # Generated reports folder
└── README.md              # This file
```

## Technical Analysis Indicators

### Moving Averages
- **20-day SMA**: Short-term trend indicator
- **50-day SMA**: Medium-term trend indicator

### Relative Strength Index (RSI)
- Measures price momentum
- Overbought (>70) or oversold (<30) conditions

### MACD (Moving Average Convergence Divergence)
- Trend-following momentum indicator
- Shows relationship between EMA 12 and EMA 26

## Data Source

All market data is fetched from **Yahoo Finance** using the `yfinance` library. This provides:

- Real-time stock prices
- Historical price data (up to 1 year)
- Company fundamentals
- Institutional ownership information

## Output Files

Reports are saved in the `reports/` folder with filenames like:

```
YYYYMMDD_HHMMSS_AAPL_report.html   # HTML report
YYYYMMDD_HHMMSS_AAPL_report.txt    # Text report
```

## Keyboard Shortcuts

- `Ctrl+C`: Cancel analysis and exit
- Use arrow keys when selecting from the quick picker menu

## Tips

1. **First-time users**: Try running without arguments to see the interactive menu
2. **Quick reports**: Use `--basic` flag for essential metrics only
3. **Detailed analysis**: Run with no flags for full technical and financial analysis
4. **Save reports**: HTML reports open automatically in your browser

## Troubleshooting

### "Module not found" error
```bash
pip install -r requirements.txt
```

### Network errors
Ensure you have an internet connection. The app fetches data from Yahoo Finance.

### Invalid ticker symbol
Verify the ticker is correct (e.g., "AAPL" for Apple, "GOOGL" for Google/Alphabet)

## License

This project is open source and available for educational use.

## Contributing

Feel free to enhance this tool by:
- Adding more technical indicators
- Supporting additional data sources
- Creating new report formats

Enjoy analyzing stocks! 📈