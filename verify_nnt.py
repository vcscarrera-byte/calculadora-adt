import sys
import os

sys.path.append(os.getcwd())
from src import visuals
import plotly.graph_objects as go

def test_nnt_gauge():
    print("Testing NNT Gauge...")
    
    # 1. Good NNT (10)
    fig = visuals.create_nnt_gauge(10)
    assert isinstance(fig, go.Figure)
    print("✓ NNT 10 handled")
    
    # 2. String NNT ("> 50")
    fig2 = visuals.create_nnt_gauge("> 50")
    assert isinstance(fig2, go.Figure)
    print("✓ NNT '> 50' handled")
    
    # 3. None/"-"
    fig3 = visuals.create_nnt_gauge("-")
    assert isinstance(fig3, go.Figure)
    print("✓ NNT '-' handled")

if __name__ == "__main__":
    test_nnt_gauge()
