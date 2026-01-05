import sys
import os

# Ensure we can import from src
sys.path.append(os.getcwd())

from src.constants import RiskLevel, RTField, ADTRecommendation, GleasonScore, TumorStage, MarginStatus, PetFindings, LifeExpectancy
from src import utils

def test_summary_generation():
    print("Testing Summary Generation...")
    
    # Mock Inputs
    inputs = {
        'psa_pre_srt': 0.5,
        'gleason': GleasonScore.ISUP3,
        'stage': TumorStage.PT2,
        'margin': MarginStatus.R0,
        'psadt_months': 10.0,
        'pet_findings': PetFindings.NEGATIVE,
        'has_cardio': False,
        'has_metabolic': True,
        'has_bone': False,
        'life_expectancy': LifeExpectancy.LONG
    }
    
    risk = RiskLevel.INTERMEDIATE
    rt = RTField.BED_ONLY
    adt = ADTRecommendation.SHORT
    benefits = {'arr_5yr': 5.0, 'nnt': 20}
    
    text = utils.generate_summary_text(inputs, risk, rt, adt, benefits)
    
    print("--- Generated Text ---")
    print(text)
    print("----------------------")
    
    assert "RESUMO CLÍNICO" in text
    assert "ISUP 3" in text
    assert "Risco Metabólico Elevado: Sim" in text
    assert "(NNT): 20" in text
    
    print("✓ Summary text generated correctly.")

if __name__ == "__main__":
    test_summary_generation()
