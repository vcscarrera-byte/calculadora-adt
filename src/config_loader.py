import csv
import os
from .constants import RiskLevel, GleasonScore, TumorStage, PetFindings, MarginStatus

def load_rules(csv_path="config/risk_rules.csv"):
    """
    Loads rules from CSV.
    Returns a list of dicts: [{'risk': 'HIGH', 'var': 'gleason', 'op': 'IN', 'val': 'GG4;GG5'}, ...]
    """
    rules = []
    if not os.path.exists(csv_path):
        return []
        
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rules.append(row)
    return rules

def evaluate_risk_from_rules(inputs, rules):
    """
    Evaluates inputs against loaded rules.
    Priority: HIGH -> INTERMEDIATE -> LOW.
    """
    if not rules:
        return None # Fallback to hardcoded

    # Helper to parse value based on variable type
    def parse_val(var_name, val_str):
        if var_name == 'gleason':
            return [getattr(GleasonScore, v.strip()) for v in val_str.split(';')] if ';' in val_str else getattr(GleasonScore, val_str.strip())
        if var_name == 'stage':
             return getattr(TumorStage, val_str.strip())
        if var_name == 'pet_findings':
            return [getattr(PetFindings, v.strip()) for v in val_str.split(';')] if ';' in val_str else getattr(PetFindings, val_str.strip())
        if var_name in ['psadt_months', 'psa_pre_srt']:
             return float(val_str)
        if var_name == 'has_psa_persistence':
             return val_str.lower() == 'true'
        return val_str

    # Evaluate VERY HIGH rules first
    for r in rules:
        if r['risk_level'] == 'VERY_HIGH':
            if check_rule(inputs, r, parse_val):
                return RiskLevel.VERY_HIGH

    # Evaluate HIGH rules first
    for r in rules:
        if r['risk_level'] == 'HIGH':
            if check_rule(inputs, r, parse_val):
                return RiskLevel.HIGH
                
    # Evaluate INTERMEDIATE
    for r in rules:
        if r['risk_level'] == 'INTERMEDIATE':
            if check_rule(inputs, r, parse_val):
                return RiskLevel.INTERMEDIATE
                
    return None

def check_rule(inputs, rule, parser):
    var = rule['variable']
    op = rule['operator']
    val_raw = rule['value']
    
    # Get input value
    if var not in inputs or inputs[var] is None:
        return False
        
    input_val = inputs[var] # Enum or float
    
    try:
        if op == 'EQ':
            target = parser(var, val_raw)
            return input_val == target
        elif op == 'IN':
            targets = parser(var, val_raw) # Should be list
            if not isinstance(targets, list): targets = [targets]
            return input_val in targets
        elif op == 'LT':
            target = parser(var, val_raw)
            return input_val < target
        elif op == 'GT':
            target = parser(var, val_raw)
            return input_val > target
        elif op == 'BETWEEN':
            # Val format: "min;max"
            parts = val_raw.split(';')
            min_v = float(parts[0])
            max_v = float(parts[1])
            return min_v <= input_val < max_v
    except Exception as e:
        print(f"Rule check failed: {rule} -> {e}")
        return False
        
    return False
