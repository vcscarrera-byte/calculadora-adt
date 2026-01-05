import sys
import os

# Ensure we can import from src
sys.path.append(os.getcwd())

from src.constants import RiskLevel, ADTRecommendation
from src import logic

def test_benefits():
    print("Testing Absolute Benefits Logic...")
    
    # 1. High Risk -> Significant Benefit
    res_high = logic.get_absolute_benefits(RiskLevel.HIGH, ADTRecommendation.LONG)
    print(f"High Risk Benefit: {res_high}")
    assert res_high['arr_5yr'] >= 5.0, "High risk should have >5% ARR"
    assert res_high['nnt'] != "-", "High risk should have valid NNT"
    
    # 2. No ADT -> No Benefit
    res_none = logic.get_absolute_benefits(RiskLevel.LOW, ADTRecommendation.NONE)
    print(f"No ADT Benefit: {res_none}")
    assert res_none['arr_5yr'] == 0.0, "No ADT should have 0 ARR"
    assert res_none['nnt'] == "-", "No ADT should have placeholder NNT"

    print("✓ Benefits logic verified.")

if __name__ == "__main__":
    test_benefits()
