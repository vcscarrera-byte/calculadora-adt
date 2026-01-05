from enum import Enum, auto

class RiskLevel(Enum):
    LOW = "Baixo Risco"
    INTERMEDIATE = "Risco Intermediário"
    HIGH = "Alto Risco"
    VERY_HIGH = "Muito Alto Risco"

class RTField(Enum):
    BED_ONLY = "Fossa Prostática (Leito)"
    BED_PELVIS = "Leito + Linfonodos Pélvicos"

class ADTRecommendation(Enum):
    NONE = "sRT Isolada (Sem ADT)"
    SHORT = "sRT + ADT Curta (4-6 meses)"
    LONG = "sRT + ADT Longa (18-24 meses)"
    LONG_ARPI = "sRT + ADT Longa + ARPI (24 meses)"

class GleasonScore(Enum):
    ISUP1 = "ISUP 1 (≤ 6)"
    ISUP2 = "ISUP 2 (3+4=7)"
    ISUP3 = "ISUP 3 (4+3=7)"
    ISUP4 = "ISUP 4 (4+4=8, 3+5=8, 5+3=8)"
    ISUP5 = "ISUP 5 (9-10)"

class TumorStage(Enum):
    PT2 = "pT2 (Confinado à próstata)"
    PT3A = "pT3a (Extensão extra-prostática)"
    PT3B = "pT3b (Invasão de vesícula seminal)"

class NodalStage(Enum):
    NX = "pNx (Não avaliado)"
    N0 = "pN0 (Linfonodos negativos)"
    N1 = "pN1 (Linfonodos positivos)"

class MarginStatus(Enum):
    R0 = "R0 (Margens Negativas)"
    R1 = "R1 (Margens Positivas)"

class PetFindings(Enum):
    NOT_PERFORMED = "Não realizado"
    NEGATIVE = "Negativo"
    BED = "Recidiva no Leito"
    PELVIC_LN = "Linfonodo Pélvico"
    EXTRA_PELVIC = "Doença Extra-pélvica (M1)"

class LifeExpectancy(Enum):
    LONG = "> 10 anos"
    SHORT = "≤ 10 anos"
