import streamlit as st
from src import ui, logic

# Page Configuration
st.set_page_config(
    page_title="Calculadora ADT - Câncer de Próstata",
    page_icon="⚕️",
    layout="wide"
)

def main():
    st.title("Quando associar hormonioterapia à radioterapia de salvamento no câncer de próstata")
    st.markdown("""
    Esta ferramenta auxilia na decisão de adicionar Terapia de Privação Androgênica (ADT) 
    e definir o campo de radioterapia (sRT) em pacientes com câncer de próstata pós-prostatectomia.
    
    *Atenção: Uso exclusivo para profissionais de saúde. Não substitui julgamento clínico.*
    """)
    st.markdown("---")
    
    # 1. Get Inputs
    inputs = ui.render_inputs()
    
    # 2. Process Logic
    risk = logic.classify_risk(
        inputs['psa_pre_srt'],
        inputs['gleason'],
        inputs['stage'],
        inputs['psadt_months'],
        inputs['pet_findings'],
        inputs['margin'],
        inputs['n_stage'],
        inputs['has_psa_persistence']
    )
    
    rt_field = logic.suggest_rt_field(
        risk=risk,
        pet_findings=inputs['pet_findings']
    )
    
    adt_rec = logic.suggest_adt(
        risk=risk,
        life_expectancy=inputs['life_expectancy'],
        has_cardio_risk=inputs['has_cardio'],
        has_severe_metabolic=inputs['has_metabolic']
    )
    
    # 3. Render Outputs
    ui.render_results(risk, rt_field, adt_rec, inputs)

if __name__ == "__main__":
    main()
