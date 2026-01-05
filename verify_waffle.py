import sys
import os
import plotly.graph_objects as go

sys.path.append(os.getcwd())
try:
    from src import visuals
except ImportError:
    print("Could not import src.visuals")
    sys.exit(1)

def test_waffle():
    print("Testing Waffle Chart...")
    
    # Scenario: 10% benefit, 40% baseline risk
    fig = visuals.create_waffle_chart(10.0, 40.0)
    assert isinstance(fig, go.Figure)
    print("✓ Waffle Chart generated (10/40)")
    
    # Scenario: Low Risk (< 2.0 benefit, 10 baseline)
    fig2 = visuals.create_waffle_chart("< 2.0", 10.0)
    assert isinstance(fig2, go.Figure)
    print("✓ Waffle Chart generated (Low Risk)")

if __name__ == "__main__":
    test_waffle()
