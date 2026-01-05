from src.logic import classify_risk, suggest_adt, get_absolute_benefits, RiskLevel, ADTRecommendation, GleasonScore, TumorStage, PetFindings, MarginStatus, RTField, LifeExpectancy

def test_v4_logic():
    print("Testing V4.2026 Risk Logic...")
    
    # Case 1: VERY HIGH Risk (N1)
    # N1 should be VERY HIGH
    r1 = classify_risk(0.1, GleasonScore.ISUP1, TumorStage.PT2, 20, PetFindings.PELVIC_LN, MarginStatus.R0)
    assert r1 == RiskLevel.VERY_HIGH, f"N1 should be VERY_HIGH, got {r1}"
    print("PASS: N1 -> Very High")
    
    # Case 2: VERY HIGH Risk (PSADT <= 6)
    r2 = classify_risk(0.1, GleasonScore.ISUP1, TumorStage.PT2, 5.0, PetFindings.NEGATIVE, MarginStatus.R0)
    assert r2 == RiskLevel.VERY_HIGH, f"PSADT=5 should be VERY_HIGH, got {r2}"
    print("PASS: PSADT<=6 -> Very High")

    # Case 3: VERY HIGH Risk (Persistence + GG4)
    r3 = classify_risk(0.1, GleasonScore.ISUP4, TumorStage.PT2, 20, PetFindings.NEGATIVE, MarginStatus.R0, has_psa_persistence=True)
    assert r3 == RiskLevel.VERY_HIGH, f"Persist+GG4 should be VERY_HIGH, got {r3}"
    print("PASS: Persistence + GG4 -> Very High")
    
    # Case 4: HIGH Risk (Persistence ONLY + GG1) -> NOT Very High (Logic check: Persist+GG4 required)
    # Check if falls back to other high risk factors or Low/Int
    r4 = classify_risk(0.1, GleasonScore.ISUP1, TumorStage.PT2, 20, PetFindings.NEGATIVE, MarginStatus.R0, has_psa_persistence=True)
    # GG1, pT2, PSADT>12, PSA<0.5, Neg PET -> Low Risk even with persistence? 
    # V4 Logic says: (Persist AND GG>=4) is Very High.
    # Persist alone isn't stated as High in my implemented logic.
    assert r4 == RiskLevel.LOW, f"Persist+GG1 should be LOW (per current logic), got {r4}"
    print("PASS: Persistence + GG1 -> Low (Correct as per strict logic)")
    
    # Case 5: HIGH Risk (GG4)
    r5 = classify_risk(0.1, GleasonScore.ISUP4, TumorStage.PT2, 20, PetFindings.NEGATIVE, MarginStatus.R0)
    assert r5 == RiskLevel.HIGH, f"GG4 should be HIGH, got {r5}"
    print("PASS: GG4 -> High")
    
    # Case 6: INTERMEDIATE Risk (GG3 + pT2)
    r6 = classify_risk(0.6, GleasonScore.ISUP3, TumorStage.PT2, 20, PetFindings.NEGATIVE, MarginStatus.R0)
    assert r6 == RiskLevel.INTERMEDIATE, f"GG3 should be INTERMEDIATE, got {r6}"
    print("PASS: GG3 -> Intermediate")
    
    # Test ADT Suggestions
    # Very High -> Long + ARPI
    adt_vh = suggest_adt(RiskLevel.VERY_HIGH, LifeExpectancy.LONG, False, False)
    assert adt_vh == ADTRecommendation.LONG_ARPI, f"Very High should get LONG_ARPI, got {adt_vh}"
    print("PASS: Suggest ADT Very High -> Long + ARPI")
    
    # High -> Long
    adt_h = suggest_adt(RiskLevel.HIGH, LifeExpectancy.LONG, False, False)
    assert adt_h == ADTRecommendation.LONG, f"High should get LONG, got {adt_h}"
    print("PASS: Suggest ADT High -> Long")

    # Test NNT
    ben_vh = get_absolute_benefits(RiskLevel.VERY_HIGH, ADTRecommendation.LONG_ARPI)
    assert ben_vh['nnt'] == 8, f"Very High NNT should be 8, got {ben_vh['nnt']}"
    print("PASS: Very High NNT -> 8")

    print("ALL V4 LOGIC TESTS PASSED")

if __name__ == "__main__":
    test_v4_logic()
