**TradedeskCLI** is a lightweight command-line tool for quickly searching stocks by ticker or company name and retrieving their current market price.

🔹 **Key Features**

Search by Ticker

tradedesk search --ticker AAPL


→ Prints the current price of Apple Inc.

Search by Company Name

tradedesk search --name "Tesla"


→ Finds the ticker (TSLA) and shows the latest price.

Formatted Output
Results are displayed in a clear format:

🔎 Stock: Apple Inc. (AAPL)
💰 Current Price: $212.45
⏰ Last Updated: 2025-08-20 13:35 UTC

🔹 **Why It’s Useful**

Super fast stock lookups from the terminal.

Great for developers, traders, and data engineers.

Forms the foundation for an extensible financial ETL pipeline (future versions will support indicators, historical data, automation).
