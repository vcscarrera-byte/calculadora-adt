from src.logic import classify_risk, RiskLevel, GleasonScore, TumorStage, PetFindings, MarginStatus, NodalStage
from src.visuals import create_risk_gauge
import plotly.graph_objects as go

def test_pn1_logic():
    print("Testing pN1 Logic...")
    # Base case: Low Risk features but pN1
    r = classify_risk(
        psa_pre_srt=0.1,
        gleason=GleasonScore.ISUP1,
        stage=TumorStage.PT2,
        psadt_months=20,
        pet_findings=PetFindings.NEGATIVE,
        margin=MarginStatus.R0,
        n_stage=NodalStage.N1, # Should trigger VERY HIGH
        has_psa_persistence=False
    )
    assert r == RiskLevel.VERY_HIGH, f"pN1 should be VERY HIGH, got {r}"
    print("PASS: pN1 -> Very High")

def test_risk_gauge():
    print("Testing Risk Gauge...")
    fig = create_risk_gauge(50.0)
    assert isinstance(fig, go.Figure), "Should return a Plotly Figure"
    print("PASS: create_risk_gauge returns Figure")

if __name__ == "__main__":
    test_pn1_logic()
    test_risk_gauge()
