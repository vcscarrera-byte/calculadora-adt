from src.logic import classify_risk, RiskLevel, GleasonScore, TumorStage, PetFindings, MarginStatus, NodalStage

def test_psa_ranges():
    print("Testing PSA Ranges...")
    
    # 1. Low Risk (<= 0.3)
    r_low = classify_risk(0.2, GleasonScore.ISUP1, TumorStage.PT2, 20, PetFindings.NEGATIVE, MarginStatus.R0)
    assert r_low == RiskLevel.LOW, f"PSA 0.2 should be LOW, got {r_low}"
    print("PASS: PSA 0.2 -> Low")
    
    r_low_edge = classify_risk(0.3, GleasonScore.ISUP1, TumorStage.PT2, 20, PetFindings.NEGATIVE, MarginStatus.R0)
    assert r_low_edge == RiskLevel.LOW, f"PSA 0.3 should be LOW, got {r_low_edge}"
    print("PASS: PSA 0.3 -> Low")

    # 2. Intermediate Risk (0.3 < PSA <= 0.7)
    r_int = classify_risk(0.4, GleasonScore.ISUP1, TumorStage.PT2, 20, PetFindings.NEGATIVE, MarginStatus.R0)
    assert r_int == RiskLevel.INTERMEDIATE, f"PSA 0.4 should be INT, got {r_int}"
    print("PASS: PSA 0.4 -> Intermediate")

    r_int_edge = classify_risk(0.7, GleasonScore.ISUP1, TumorStage.PT2, 20, PetFindings.NEGATIVE, MarginStatus.R0)
    assert r_int_edge == RiskLevel.INTERMEDIATE, f"PSA 0.7 should be INT, got {r_int_edge}"
    print("PASS: PSA 0.7 -> Intermediate")
    
    # 3. High Risk (> 0.7)
    r_high = classify_risk(0.8, GleasonScore.ISUP1, TumorStage.PT2, 20, PetFindings.NEGATIVE, MarginStatus.R0)
    assert r_high == RiskLevel.HIGH, f"PSA 0.8 should be HIGH, got {r_high}"
    print("PASS: PSA 0.8 -> High")

def test_pet_not_performed():
    print("Testing PET Not Performed...")
    # Should behave like Negative (not trigger Very High)
    r_np = classify_risk(0.2, GleasonScore.ISUP1, TumorStage.PT2, 20, PetFindings.NOT_PERFORMED, MarginStatus.R0)
    assert r_np == RiskLevel.LOW, f"PET Not Performed should not escalate risk, got {r_np}"
    print("PASS: PET Not Performed -> Neutral")

if __name__ == "__main__":
    test_psa_ranges()
    test_pet_not_performed()
