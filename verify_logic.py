import sys
import os

# Ensure we can import from src
sys.path.append(os.getcwd())

from src.constants import RiskLevel, GleasonScore, TumorStage, MarginStatus, PetFindings, RTField, ADTRecommendation, LifeExpectancy
from src import logic

def test_high_risk():
    print("Testing High Risk Logic...")
    # Scenario: pT3b -> High Risk
    risk = logic.classify_risk(
        psa_pre_srt=0.2,
        gleason=GleasonScore.ISUP2,
        stage=TumorStage.PT3B,
        psadt_months=20,
        pet_findings=PetFindings.NEGATIVE,
        margin=MarginStatus.R0
    )
    assert risk == RiskLevel.HIGH, f"Expected HIGH for pT3b, got {risk}"
    print("✓ pT3b correctly classified as High Risk")

def test_rt_field():
    print("Testing RT Field Logic...")
    # Scenario: Pelvic LN -> Bed + Pelvis
    field = logic.suggest_rt_field(RiskLevel.HIGH, PetFindings.PELVIC_LN)
    assert field == RTField.BED_PELVIS, f"Expected BED_PELVIS for LN+, got {field}"
    print("✓ Pelvic LN correctly triggers Pelvic Field")

def test_adt_logic():
    print("Testing ADT Logic...")
    # Scenario: Low Risk, Long expectancy -> None
    adt = logic.suggest_adt(RiskLevel.LOW, LifeExpectancy.LONG, False, False)
    assert adt == ADTRecommendation.NONE, f"Expected NONE for Low Risk, got {adt}"
    print("✓ Low Risk correctly suggests No ADT")

if __name__ == "__main__":
    try:
        test_high_risk()
        test_rt_field()
        test_adt_logic()
        print("\nAll logic checks passed successfully!")
    except AssertionError as e:
        print(f"\n❌ Logic Verification Failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Runtime Error: {e}")
        sys.exit(1)
