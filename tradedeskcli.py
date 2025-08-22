#!/usr/bin/env python
from __future__ import annotations

import json
from typing import Optional

import requests
import typer
from rich.console import Console
from rich.table import Table
import yfinance as yf
import pyfiglet

# TradeDeskCLI: A simple command-line tool to search for stock tickers and print their current prices.
app = typer.Typer(add_completion=False, help="TradedeskCLI: search tickers and print current prices.")
console = Console()

YAHOO_SEARCH_URL = "https://query1.finance.yahoo.com/v1/finance/search"



def print_banner():
    banner = pyfiglet.figlet_format("TradeDeskCLI")
    console.print(banner, style="bold green")


def lookup_ticker_by_name(name: str) -> Optional[dict]:
    """
    Use Yahoo Finance public search to find the best matching quote for a company name.
    Returns a dict like {"symbol": "AAPL", "shortname": "Apple Inc."} or None.
    """
    try:
        resp = requests.get(
            YAHOO_SEARCH_URL,
            params={"q": name, "quotesCount": 1, "newsCount": 0, "listsCount": 0},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        quotes = data.get("quotes") or []
        if not quotes:
            return None
        q = quotes[0]
        return {
            "symbol": q.get("symbol"),
            "name": q.get("shortname") or q.get("longname") or q.get("symbol"),
            "type": q.get("quoteType"),
            "exchange": q.get("exchange"),
            "score": q.get("score"),
        }
    except Exception:
        return None


def get_current_price(ticker: str) -> Optional[float]:
    """
    Get a current/last price using yfinance.
    Tries fast_info first, falls back to last close from recent history.
    """
    try:
        t = yf.Ticker(ticker)
        # Prefer fast_info if available
        try:
            fi = t.fast_info
            if fi and "last_price" in fi and fi["last_price"]:
                return float(fi["last_price"])
        except Exception:
            pass

        # Fallback: recent 1d/1m history
        hist = t.history(period="1d", interval="1m")
        if not hist.empty:
            return float(hist["Close"].dropna().iloc[-1])

        # Secondary fallback: regular 1d/1d
        hist = t.history(period="1d")
        if not hist.empty:
            return float(hist["Close"].dropna().iloc[-1])
    except Exception:
        pass
    return None


@app.command("search")
def search_command(
    ticker: Optional[str] = typer.Option(
        None, "--ticker", "-t", help="Ticker symbol, e.g. AAPL, TSLA, BTC-USD"
    ),
    name: Optional[str] = typer.Option(
        None, "--name", "-n", help='Company/asset name, e.g. "Apple", "Tesla"'
    ),
    json_out: bool = typer.Option(False, "--json", help="Output JSON instead of a table."),
):
    """
    Search by ticker OR company name and print the current price.
    """
    if not ticker and not name:
        typer.echo("Provide --ticker or --name (see --help).")
        raise typer.Exit(code=2)

    resolved = None
    if name and not ticker:
        resolved = lookup_ticker_by_name(name)
        if not resolved or not resolved.get("symbol"):
            typer.echo(f'No results for name: "{name}".')
            raise typer.Exit(code=1)
        ticker = resolved["symbol"]

    price = get_current_price(ticker)
    asset_name = (
        resolved["name"] if resolved and resolved.get("name") else (ticker if not name else name)
    )

    if json_out:
        payload = {
            "ticker": ticker,
            "name": asset_name,
            "price": price,
            "success": price is not None,
        }
        typer.echo(json.dumps(payload, indent=2))
        raise typer.Exit()

    table = Table(title="TradedeskCLI – Price Lookup")
    table.add_column("Name", style="bold")
    table.add_column("Ticker")
    table.add_column("Current Price", justify="right")

    if price is None:
        table.add_row(asset_name, ticker or "-", "[red]N/A[/red]")
    else:
        table.add_row(asset_name, ticker or "-", f"{price:,.4f}")

    console.print(table)


if __name__ == "__main__":
    print_banner()
    app()
