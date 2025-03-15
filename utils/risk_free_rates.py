import yfinance as yf
class RiskFreeRate:

    def united_states():
        # Fetch bond yields
        bond_data = yf.Ticker("^TNX").history(period="1d")
        if not bond_data.empty:
            return bond_data['Close'].iloc[-1]
        else:
            return None
        
    def united_kingdom():
        return 4.6
        
    def vietnam():
        # FIXME: no API so far
        return 3.054
    
    def australia():
        return 4.35
    
    def hong_kong():
        return 3.71
    
    def japan():
        return 1.284
    
    mapper = {
        'united_states' : united_states,
        'united_kingdom' : united_kingdom,
        'vietnam' : vietnam,
        'australia' : australia,
        'hong_kong' : hong_kong,
        'japan' : japan
    }
    
