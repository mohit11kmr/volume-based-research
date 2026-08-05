import sys
import os
sys.path.append(os.path.dirname(__file__))

from main import get_stock_analysis, run_screener

try:
    print("Testing get_stock_analysis('RELIANCE.NS')...")
    res = get_stock_analysis('RELIANCE.NS')
    print("SUCCESS: Symbol:", res['symbol'], "Candles count:", len(res['candles']))
    print("Latest:", res['latest'])
except Exception as e:
    import traceback
    print("ERROR:")
    traceback.print_exc()
