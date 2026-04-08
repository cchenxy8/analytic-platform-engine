# Analytic Platform

A small Python backtesting project for comparing simple long-only trading strategies on daily price data.

## Included strategies

- `buy_and_hold`
- `moving_average`
- `mean_reversion`

## Run with a local CSV

```bash
python3 main.py --csv data/sample_prices.csv --strategy buy_and_hold
python3 main.py --csv data/sample_prices.csv --strategy moving_average
python3 main.py --csv data/mean_reversion_sample.csv --strategy mean_reversion
```

The CSV should contain:

- `date` or `timestamp`
- `close`

If `--symbol` is not provided, the app loads price data from `--csv`.

## Run with live market data

This project can also fetch daily data from Alpha Vantage.

Add your key to a local `.env` file:

```bash
ALPHAVANTAGE_API_KEY=your_key_here
```

Each user should use their own Alpha Vantage key. This avoids shared rate limits and keeps your personal key private.

The app reads the API key from:

- `--api-key`
- `ALPHAVANTAGE_API_KEY`
- a local `.env` file

Useful API options:

- `--symbol AAPL`
- `--api-outputsize compact`
- `--api-outputsize full`

Then run:

```bash
python3 main.py --symbol AAPL --strategy buy_and_hold
python3 main.py --symbol AAPL --strategy moving_average
python3 main.py --symbol AAPL --strategy mean_reversion
```

## Useful options

```bash
--short-window
--long-window
--lookback-window
--entry-threshold
--exit-threshold
--plot
```

By default, the equity curve is written to `outputs/equity_curve.svg`.

Debug options:

```bash
--debug-moving-average
--debug-mean-reversion
--debug-limit
```

## Project structure

- `main.py`: CLI entry point
- `data/loader.py`: CSV and API data loading
- `requirements.txt`: dependency note
- `engine/backtester.py`: backtest orchestration
- `engine/portfolio.py`: trade execution and equity tracking
- `strategies/`: strategy implementations
- `reporting/`: console output and SVG chart rendering
- `outputs/`: generated SVG charts
