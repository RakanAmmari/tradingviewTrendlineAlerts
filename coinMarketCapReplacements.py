# Some coins have different symbols on TradingView than CoinMarketCap, which causes an error when retrieving prices.
# This is a dictionary to replace the symbol before retrieving prices. Key: TradingView symbol, Value: CoinMarketCap symbol.

correctCMCSymbol = {
    'GXS': 'GXC',
    'IOTA': 'MIOTA',
    'NANO': 'XNO'
}