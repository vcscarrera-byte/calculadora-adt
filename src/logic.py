from .constants import (
    RiskLevel, RTField, ADTRecommendation,
    GleasonScore, TumorStage, PetFindings, LifeExpectancy, MarginStatus, NodalStage
)

def classify_risk(
    psa_pre_srt: float,
    gleason: GleasonScore,
    stage: TumorStage,
    psadt_months: float, # can be None if unknown
    pet_findings: PetFindings,
    margin: MarginStatus,
    n_stage: NodalStage = NodalStage.NX,
    has_psa_persistence: bool = False
) -> RiskLevel:
    """
    Classifies risk based on V4.2026 Top-Down Hierarchy.
    
    1. VERY HIGH: N1 OR PSADT<=6 OR (Persist + GG>=4)
    2. HIGH: GG>=4 OR pT3b OR PSADT<=12 OR PSA>1.0
    3. INTERMEDIATE: GG2-3 OR pT3a OR R1 OR PSA>=0.5
    4. LOW: (Implied else / GG1+pT2+R0+PSADT>12+PSA<0.5)
    """

    # 0. Try External Rules
    from . import config_loader
    rules = config_loader.load_rules()
    
    inputs_dict = {
        'psa_pre_srt': psa_pre_srt,
        'gleason': gleason,
        'stage': stage,
        'psadt_months': psadt_months,
        'pet_findings': pet_findings,
        'margin': margin,
        'has_psa_persistence': has_psa_persistence,
        'n_stage': n_stage
    }
    
    # Get risk from rules (can be None)
    risk_from_config = config_loader.evaluate_risk_from_rules(inputs_dict, rules)

    # Calculate Risk from Python Logic (V4.2026 Codebase)
    risk_from_code = RiskLevel.LOW # Default
    
    # Helper booleans
    # Grade
    is_gg4_5 = gleason in [GleasonScore.GG4, GleasonScore.GG5]
    is_gg2_3 = gleason in [GleasonScore.GG2, GleasonScore.GG3]
    
    # Stage
    is_pt3b = stage == TumorStage.PT3B
    is_pt3a = stage == TumorStage.PT3A
    
    # Margin
    is_r1 = margin == MarginStatus.R1
    
    # Nodal / PET (Clinical or Pathological)
    is_n1 = (pet_findings in [PetFindings.PELVIC_LN, PetFindings.EXTRA_PELVIC]) or (n_stage == NodalStage.N1)
    
    # Kinetic
    is_psadt_le_6 = psadt_months is not None and psadt_months <= 6.0
    is_psadt_le_12 = psadt_months is not None and psadt_months <= 12.0
    
    # PSA Levels (New Logic: >0.7 High, >0.3 Intermediate)
    is_psa_high = psa_pre_srt > 0.7
    is_psa_int = psa_pre_srt > 0.3 # Covers 0.31 to 0.7 (if high is false)
    
    # --- 1. VERY HIGH RISK ---
    if (is_n1 or is_psadt_le_6 or (has_psa_persistence and is_gg4_5)):
        risk_from_code = RiskLevel.VERY_HIGH
    
    # --- 2. HIGH RISK (If not Very High) ---
    elif (is_gg4_5 or is_pt3b or is_psadt_le_12 or is_psa_high):
        risk_from_code = RiskLevel.HIGH
        
    # --- 3. INTERMEDIATE RISK (If not High/VH) ---
    elif (is_gg2_3 or is_pt3a or is_r1 or is_psa_int):
        risk_from_code = RiskLevel.INTERMEDIATE
        
    # --- 4. COMBINE AND RETURN MAX ---
    # Define weight for comparison
    def risk_weight(r):
        if r == RiskLevel.VERY_HIGH: return 4
        if r == RiskLevel.HIGH: return 3
        if r == RiskLevel.INTERMEDIATE: return 2
        return 1
        
    if risk_from_config:
        # Return whichever is higher (Conservative approach for safety)
        if risk_weight(risk_from_config) > risk_weight(risk_from_code):
            return risk_from_config
            
    return risk_from_code

def suggest_rt_field(
    risk: RiskLevel,
    pet_findings: PetFindings
) -> RTField:
    """
    Suggests RT Field (Bed vs Bed+Pelvis).
    
    Logic:
    - If Pelvic LN positive (PET) -> Bed + Pelvis
    - If High Risk (often implies occult nodal risk) -> Bed + Pelvis (Clinical trade-off, but often suggested)
      *Refinement for MVP*: Let's stick to explicitly PET positive OR High Risk driven by biology (GS 8-10, pT3b).
    - Else -> Bed Only
    """
    if pet_findings in [PetFindings.PELVIC_LN, PetFindings.EXTRA_PELVIC]:
        return RTField.BED_PELVIS
        
    # If PET Not Performed or Negative, rely on clinical risk
    # High risk strictly by locally advanced/aggressive biology also often merits pelvic RT
    if risk == RiskLevel.VERY_HIGH:
        # Conduta A: RT (Leito + Pelve Total)
        return RTField.BED_PELVIS
        
    if risk == RiskLevel.HIGH:
        # Conduta B: RT (Leito + Pelve)
        return RTField.BED_PELVIS
        
    return RTField.BED_ONLY

def suggest_adt(
    risk: RiskLevel,
    life_expectancy: LifeExpectancy,
    has_cardio_risk: bool,
    has_severe_metabolic: bool
) -> ADTRecommendation:
    """
    Suggests ADT duration/addition.
    """
    # 1. Life Expectancy Check
    if life_expectancy == LifeExpectancy.SHORT:
        # Toxicidade x Benefício
        if risk in [RiskLevel.VERY_HIGH, RiskLevel.HIGH]:
            return ADTRecommendation.SHORT # De-escalate from Long/ARPI
        return ADTRecommendation.NONE
        
    # 2. Evaluation by Risk (LE > 10)
    if risk == RiskLevel.VERY_HIGH:
        return ADTRecommendation.LONG_ARPI
        
    if risk == RiskLevel.HIGH:
        return ADTRecommendation.LONG
        
    if risk == RiskLevel.INTERMEDIATE:
        return ADTRecommendation.SHORT
        
    return ADTRecommendation.NONE

def get_absolute_benefits(risk: RiskLevel, adt: ADTRecommendation) -> dict:
    """
    Returns estimated Absolute Risk Reduction (ARR) and Number Needed to Treat (NNT)
    for Metastasis-Free Survival (10-year horizon per requested data).
    
    Ref updated:
    - Very High: NNT ~8-9
    - High: NNT ~9-11
    - Intermediate: NNT ~17
    - Low: NNT >33 (Poor benefit)
    """
    
    if adt == ADTRecommendation.NONE:
         return {'arr_5yr': 0.0, 'nnt': "-"}

    if risk == RiskLevel.VERY_HIGH:
        # NNT ~8 -> ARR ~ 12.5%
        nnt = 8
        arr = 12.5
        return {'arr_5yr': arr, 'nnt': nnt}
        
    if risk == RiskLevel.HIGH:
        # NNT ~10 -> ARR ~ 10%
        nnt = 10
        arr = 10.0
        return {'arr_5yr': arr, 'nnt': nnt}
        
    if risk == RiskLevel.INTERMEDIATE:
        # NNT ~17 -> ARR ~ 5.9%
        nnt = 17
        arr = 5.9
        return {'arr_5yr': arr, 'nnt': nnt}
        
    # Low Risk (if ADT selected manually or overrides)
    return {'arr_5yr': "< 3.0", 'nnt': "> 33"}

def get_baseline_recurrence_risk(risk: RiskLevel) -> float:
    """
    Returns estimated 5-year baseline recurrence/metastasis risk WITHOUT ADT (sRT alone).
    Used for visualization (Icon Array).
    illustrative values.
    """
    if risk == RiskLevel.VERY_HIGH:
        return 60.0 # Aggressive recurrence risk
    elif risk == RiskLevel.HIGH:
        return 40.0 # High risk of failure with sRT alone
    elif risk == RiskLevel.INTERMEDIATE:
        return 20.0 # Moderate risk
    else:
        return 10.0 # Low risk
