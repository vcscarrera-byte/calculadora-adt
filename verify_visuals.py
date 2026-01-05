import sys
import os

# Ensure we can import from src
sys.path.append(os.getcwd())

from src.constants import RiskLevel
from src import visuals
import plotly.graph_objects as go

def test_gauge():
    print("Testing Visuals Logic...")
    fig = visuals.create_risk_gauge(RiskLevel.HIGH)
    assert isinstance(fig, go.Figure), "Expected Plotly Figure"
    print("✓ create_risk_gauge returned a Figure")
    print("Visuals module importable and functional.")

if __name__ == "__main__":
    test_gauge()
