from .constants import RiskLevel, RTField, ADTRecommendation, GleasonScore, TumorStage, PetFindings

def generate_summary_text(inputs, risk, rt_field, adt, benefits) -> str:
    """
    Generates a structured text summary for medical records.
    """
    
    # Format inputs for display
    def fmt_bool(val): return "Sim" if val else "Não"
    
    psadt_str = f"{inputs['psadt_months']} meses" if inputs['psadt_months'] else "Desconhecido"
    
    psa_display = inputs.get('psa_label', f"{inputs['psa_pre_srt']} ng/dL")
    
    text = f"""RESUMO CLÍNICO: Radioterapia de Salvamento e ADT

DATA: [Inserir Data]

___ DADOS CLÍNICOS ___
PSA Pré-sRT: {psa_display}
Gleason (Patológico): {inputs['gleason'].value}
Estadiamento (pT): {inputs['stage'].value}
Margem Cirúrgica: {inputs['margin'].value}
PSADT: {psadt_str}
PET-PSMA: {inputs['pet_findings'].value}

___ COMORBIDADES ___
Risco Cardiovascular Elevado: {fmt_bool(inputs['has_cardio'])}
Risco Metabólico Elevado: {fmt_bool(inputs['has_metabolic'])}
Saúde Óssea Comprometida: {fmt_bool(inputs['has_bone'])}
Expectativa de Vida: {inputs['life_expectancy'].value}

___ ANÁLISE DE DECISÃO ___
Classificação de Risco: {risk.value}
Indicação de Campo de RT: {rt_field.value}
Recomendação de ADT: {adt.value}

___ ESTIMATIVA DE BENEFÍCIO (5 ANOS) ___
Redução Absoluta de Risco (Recorrência/Metástase): {benefits['arr_5yr']}%
Número Necessário para Tratar (NNT): {benefits['nnt']}
(Obs: Estimativas baseadas em literatura, sujeitas a variação individual)

---------------------------------------------------
Gerado por Calculadora ADT (Ferramenta de Apoio)
Não substitui julgamento clínico.
"""
    return text

from fpdf import FPDF
import tempfile
import os

class PDFReport(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'Calculadora ADT - Ferramenta de Apoio à Decisão - Uso Exclusivo para Profissionais de Saúde', 0, 0, 'C')

def create_pdf(inputs, risk, rt_field, adt, benefits, visuals_map):
    """
    Generates a PDF report with charts.
    visuals_map: dict of {'key': bytes} for chart images.
    """
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    # Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Relatório de Decisão Clínica: sRT + ADT", ln=True, align='C')
    pdf.ln(5)
    
    # Disclaimer Header
    pdf.set_font("Arial", 'B', 10)
    pdf.set_text_color(200, 0, 0)
    pdf.multi_cell(0, 5, "AVISO LEGAL: Este relatório é gerado por um software de apoio à decisão e NÃO substitui o julgamento clínico. As estimativas baseiam-se em literatura agregada e podem não refletir o risco individual com precisão. O médico assistente é o único responsável pela conduta.")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(5)
    
    # Clinical Data
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "1. Dados Clínicos", ln=True)
    pdf.set_font("Arial", size=11)
    
    def safe_text(s):
        # Replace non-latin1 chars
        replacements = {
            "≤": "<=",
            "≥": ">=",
            "–": "-",
            "’": "'",
            "“": '"',
            "”": '"'
        }
        for k, v in replacements.items():
            s = s.replace(k, v)
        return s
    
    def add_line(label, val):
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(50, 7, safe_text(label), 0)
        pdf.set_font("Arial", size=11)
        pdf.cell(0, 7, safe_text(str(val)), 0, 1)

    psa_display = inputs.get('psa_label', f"{inputs['psa_pre_srt']} ng/dL")
    add_line("PSA Pré-sRT:", psa_display)
    add_line("Persistência PSA:", "Sim" if inputs.get('has_psa_persistence') else "Não")
    add_line("Gleason:", inputs['gleason'].value)
    add_line("Estadiamento:", inputs['stage'].value)
    add_line("PSADT:", f"{inputs['psadt_months']} meses" if inputs['psadt_months'] else "Desc.")
    add_line("PET-PSMA:", inputs['pet_findings'].value)
    pdf.ln(3)
    
    # Comorbidities
    comorbs = []
    if inputs['has_cardio']: comorbs.append("Risco Cardiovascular")
    if inputs['has_metabolic']: comorbs.append("Risco Metabólico")
    if inputs['has_bone']: comorbs.append("Saúde Óssea")
    if inputs['has_libido_concern']: comorbs.append("Não aceita efeitos na libido (Preferência)")
    if not comorbs: comorbs.append("Nenhuma maior relatada")
    
    add_line("Comorbidades:", ", ".join(comorbs))
    add_line("Exp. Vida:", inputs['life_expectancy'].value)
    pdf.ln(5)
    
    # Decision Analysis
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "2. Análise de Decisão", ln=True)
    
    add_line("Risco:", risk.value)
    add_line("Campo RT:", rt_field.value)
    add_line("Recomendação ADT:", adt.value)
    pdf.ln(5)
    
    # Benefits & Charts
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "3. Estimativa de Benefício (5 Anos)", ln=True)
    
    if benefits['arr_5yr'] != 0.0:
        pdf.set_font("Arial", size=11)
        pdf.cell(0, 10, f"Redução Absoluta de Risco: {benefits['arr_5yr']}% | NNT: {benefits['nnt']}", ln=True)
        
        # Embed Images
        # Save bytes to temp files because FPDF image() needs a path or specific handling
        # FPDF2 supports bytes stream? Standard FPDF often needs file.
        # Let's write to temp.
        
        y_start = pdf.get_y()
        
        # 1. ARR Gauge
        if 'arr_gauge' in visuals_map:
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                tmp.write(visuals_map['arr_gauge'])
                tmp_path = tmp.name
            
            # Place Gauge on left
            pdf.image(tmp_path, x=10, y=y_start, w=60)
            os.unlink(tmp_path)
            
        # 2. Waffle Chart
        if 'waffle' in visuals_map:
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                tmp.write(visuals_map['waffle'])
                tmp_path_w = tmp.name
                
            # Place Waffle below or right?
            # Gauge is ~60 wide. A4 is ~210 wide.
            pdf.image(tmp_path_w, x=80, y=y_start, w=100)
            os.unlink(tmp_path_w)
            
        pdf.ln(80) # Move cursor down past images
    else:
        pdf.cell(0, 10, "Benefício estimado da ADT é negligenciável para este perfil.", ln=True)
        
    return pdf.output(dest='S').encode('latin-1', errors='replace') # Return bytes

