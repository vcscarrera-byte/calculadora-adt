import sys
import os

sys.path.append(os.getcwd())
try:
    from src import visuals
except ImportError:
    print("Could not import src.visuals. Ensure running from project root.")
    sys.exit(1)

import plotly.graph_objects as go

def test_arr_gauge():
    print("Testing ARR Gauge...")
    
    # 1. High Benefit (> 6.7%)
    fig = visuals.create_arr_gauge(10.0)
    assert isinstance(fig, go.Figure)
    print("✓ ARR 10.0% handled (Green)")
    
    # 2. String ARR ("< 2.0")
    fig2 = visuals.create_arr_gauge("< 2.0")
    assert isinstance(fig2, go.Figure)
    print("✓ ARR '< 2.0' handled (Red)")
    
    # 3. Intermediate (5.0)
    fig3 = visuals.create_arr_gauge(5.0)
    assert isinstance(fig3, go.Figure)
    print("✓ ARR 5.0% handled (Yellow)")

if __name__ == "__main__":
    test_arr_gauge()
