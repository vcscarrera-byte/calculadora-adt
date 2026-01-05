
from datetime import date, timedelta
from src.logic import calculate_psadt

def test_psadt():
    print("Testing PSADT Calculation...")
    
    # Case 1: Perfect doubling in 1 month (approx)
    # 30.4375 days is a month in our logic
    d1 = date(2024, 1, 1)
    d2 = d1 + timedelta(days=30) # approx 1 month
    # v1 = 1, v2 = 2 => Doubling
    dt = calculate_psadt([d1, d2], [1.0, 2.0])
    print(f"Case 1 (1->2 in 30 days): {dt} months (Expected ~1.0)")
    assert 0.9 <= dt <= 1.1, f"Expected ~1.0, got {dt}"
    
    # Case 2: Doubling in 3 months
    d3 = d1 + timedelta(days=91) # ~3 months
    dt2 = calculate_psadt([d1, d3], [1.0, 2.0])
    print(f"Case 2 (1->2 in 91 days): {dt2} months (Expected ~3.0)")
    assert 2.9 <= dt2 <= 3.1, f"Expected ~3.0, got {dt2}"

    # Case 3: Stable PSA (No increase)
    dt3 = calculate_psadt([d1, d2], [1.0, 1.0])
    print(f"Case 3 (1->1 stable): {dt3} (Expected None)")
    assert dt3 is None
    
    # Case 4: Multiple points (Linear increasing but exponential doubling)
    # PSA: 1 -> 2 -> 4 over 2 months (1 month each step)
    d_mid = d1 + timedelta(days=30)
    d_end = d1 + timedelta(days=61)
    dt4 = calculate_psadt([d1, d_mid, d_end], [1.0, 2.0, 4.0])
    print(f"Case 4 (1->2->4 in 2 months): {dt4} months (Expected ~1.0)")
    assert 0.9 <= dt4 <= 1.1
    
    # Case 5: Insufficient data
    dt5 = calculate_psadt([d1], [1.0])
    print(f"Case 5 (One point): {dt5} (Expected None)")
    assert dt5 is None

    print("ALL TESTS PASSED")

if __name__ == "__main__":
    test_psadt()
