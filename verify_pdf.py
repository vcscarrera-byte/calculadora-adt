import sys
import os

sys.path.append(os.getcwd())
from src import utils, logic
from src.constants import RiskLevel, RTField, ADTRecommendation, GleasonScore, TumorStage, MarginStatus, PetFindings, LifeExpectancy

def test_pdf_generation():
    print("Testing PDF creation...")
    
    # Mock inputs
    inputs = {
        'psa_pre_srt': 0.5,
        'gleason': GleasonScore.GG3,
        'stage': TumorStage.PT2,
        'margin': MarginStatus.R0,
        'psadt_months': 10.0,
        'pet_findings': PetFindings.NEGATIVE,
        'has_cardio': False,
        'has_metabolic': False,
        'has_bone': False,
        'has_libido_concern': True, # Test new input
        'life_expectancy': LifeExpectancy.SHORT # Should trigger "≤ 10 anos"
    }
    
    risk = RiskLevel.INTERMEDIATE
    rt = RTField.BED_ONLY
    adt = ADTRecommendation.SHORT
    benefits = {'arr_5yr': 5.0, 'nnt': 20}
    
    # Empty visuals map for simpler test (mock images require real bytes)
    # We can skip images or pass dummy bytes if kaleido is missing/failed in test env
    # But kaleido IS installed now.
    visuals_map = {} 
    
    pdf_bytes = utils.create_pdf(inputs, risk, rt, adt, benefits, visuals_map)
    
    assert len(pdf_bytes) > 0, "PDF bytes should not be empty"
    assert b"%PDF" in pdf_bytes[:10], "Header should indicate PDF"
    
    # Save to disk to manually check if needed
    with open("test_output.pdf", "wb") as f:
        f.write(pdf_bytes)
        
    print("✓ PDF generated successfully (test_output.pdf)")

if __name__ == "__main__":
    test_pdf_generation()
