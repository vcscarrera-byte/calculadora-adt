import streamlit as st
from .constants import (
    GleasonScore, TumorStage, MarginStatus, PetFindings, LifeExpectancy,
    RiskLevel, RTField, ADTRecommendation, NodalStage
)

def render_inputs():
    """
    Renders the inputs in the main body (Expander) for better mobile visibility.
    Returns a dictionary of values.
    """
    # Use an expander open by default so mobile users see it immediately
    with st.expander("📝 Preencher Dados Clínicos (Clique para expandir/recolher)", expanded=True):
        
        st.markdown("### Dados Principais")
        
        psa_option = st.selectbox(
            "PSA pré-sRT (ng/dL)", 
            options=[
                "<= 0,3 ng/mL",
                "> 0,3 a <= 0,7 ng/mL",
                "> 0,7 ng/mL"
            ]
        )
        
        # Map selection
        if psa_option == "<= 0,3 ng/mL":
            psa_pre_srt = 0.2
        elif psa_option == "> 0,3 a <= 0,7 ng/mL":
            psa_pre_srt = 0.5
        else:
            psa_pre_srt = 0.8
            
        psa_label = psa_option
    
        has_psa_persistence = st.checkbox(
            "Persistência do PSA (Nunca indetectável pós-PR)",
            help="Se o PSA nunca baixou para < 0.1 ng/mL após a cirurgia."
        )
        
        col_clin_1, col_clin_2 = st.columns(2)
        
        with col_clin_1:
            gleason = st.selectbox(
                "Escore de Gleason (Patológico)",
                options=[e for e in GleasonScore],
                format_func=lambda x: x.value
            )
            
            stage = st.selectbox(
                "Estadiamento Patológico (pT)",
                options=[e for e in TumorStage],
                format_func=lambda x: x.value
            )
            
        with col_clin_2:
            n_stage = st.selectbox(
                "Estadiamento Patológico (pN)",
                options=[e for e in NodalStage],
                format_func=lambda x: x.value
            )
            
            margin = st.selectbox(
                "Margem Cirúrgica",
                options=[e for e in MarginStatus],
                format_func=lambda x: x.value
            )
        
        st.markdown("---")
        
        col_pet_1, col_pet_2 = st.columns(2)
        
        with col_pet_1:
            pet_findings = st.selectbox(
                "Achados PET-PSMA",
                options=[e for e in PetFindings],
                format_func=lambda x: x.value
            )
            
        with col_pet_2:
             psadt_option = st.radio(
                "Tempo de Duplicação (PSADT)",
                options=["Conhecido", "Desconhecido"]
            )
             psadt_months = None
             if psadt_option == "Conhecido":
                psadt_months = st.number_input(
                    "PSADT (meses)", 
                    min_value=0.0, value=10.0, step=1.0
                )

        st.markdown("---")
        st.markdown("### Perfil do Paciente")
        
        life_expectancy = st.radio(
            "Expectativa de Vida",
            options=[e for e in LifeExpectancy],
            format_func=lambda x: x.value,
            horizontal=True
        )
        
        st.markdown("**Fatores contra hormonioterapia**")
        c1, c2 = st.columns(2)
        with c1:
            has_cardio = st.checkbox("Alto Risco Cardiovascular (IAM, AVC prévio)")
            has_metabolic = st.checkbox("Sindrome Metabólica Grave / Diabetes")
        with c2:
            has_bone = st.checkbox("Osteoporose grave / Fratura prévia")
            has_libido_concern = st.checkbox("Paciente não aceita perda de libido")
    
    return {
        "psa_pre_srt": psa_pre_srt,
        "psa_label": psa_label,
        "psadt_months": psadt_months,
        "gleason": gleason,
        "stage": stage,
        "n_stage": n_stage,
        "margin": margin,
        "pet_findings": pet_findings,
        "life_expectancy": life_expectancy,
        "has_cardio": has_cardio,
        "has_metabolic": has_metabolic,
        "has_bone": has_bone,
        "has_libido_concern": has_libido_concern,
        "has_psa_persistence": has_psa_persistence
    }

def render_results(risk, rt_field, adt, inputs):
    """
    Renders the decision support output blocks.
    """
    st.header("Análise de Decisão Compartilhada")
    
    # Block 1: Patient Profile & Risk
    st.subheader("1. Perfil de Risco")
    
    col1, col2, col3 = st.columns([1, 1, 1]) # Adjusted columns
    
    # Dynamic styling for risk
    risk_color = "green"
    if risk == RiskLevel.INTERMEDIATE:
        risk_color = "orange"
    elif risk == RiskLevel.HIGH:
        risk_color = "red"
    elif risk == RiskLevel.VERY_HIGH:
        risk_color = "red" # Or maybe purple/darkred? Let's use red for consistency or specific styling.
        # Streamlit standard colors: blue, green, orange, red, violet.
        # Let's try violet for Very High to distinguish? Or just Red.
        # User prompt didn't specify color, but RED implies high alert.
        risk_color = "red"
        
    with col1:
        st.markdown(f"**Classificação**")
        st.markdown(f":{risk_color}[**{risk.value}**]")
        
    with col2:
        from . import visuals
        # We need benefit data here. It was calculated later in the original code.
        # Let's fetch it now.,
        from . import logic
        local_benefit = logic.get_absolute_benefits(risk, adt)
        baseline_risk = logic.get_baseline_recurrence_risk(risk)
        
        # User Request: Change first gauge to Metastasis Risk Gauge
        fig = visuals.create_risk_gauge(baseline_risk)
        st.plotly_chart(fig, use_container_width=True)

    with col3:
        st.markdown("**Fatores de Risco**")
        factors = []
        if inputs['gleason'] in [GleasonScore.GG4, GleasonScore.GG5]:
            factors.append(f"- Alto Grau ({inputs['gleason'].value})")
        if inputs['stage'] == TumorStage.PT3B:
            factors.append("- Invasão de Vesícula Seminal")
        if inputs['psadt_months'] and inputs['psadt_months'] < 6:
            factors.append(f"- PSADT Rápido ({inputs['psadt_months']} meses)")
        if inputs['pet_findings'] != PetFindings.NEGATIVE:
            factors.append(f"- PET: {inputs['pet_findings'].value}")
        
        if not factors:
            st.info("Nenhum fator de alto risco maior identificado.")
        else:
            for f in factors:
                st.write(f)
            
    # Block 2: Pros vs Cons (Trade-offs)
    st.markdown("---")
    st.subheader("2. Balança da Decisão (Trade-offs)")
    
    c_favor, c_against = st.columns(2)
    
    with c_favor:
        st.markdown("#### Favorece Intensificação")
        if risk == RiskLevel.HIGH:
            st.success("Alto Risco de Metástase a Distância: Benefício claro de ADT Longa + Tratamento de Pelve.")
        elif risk == RiskLevel.INTERMEDIATE:
            st.warning("Benefício potencial de ADT Curta para reduzir recorrência bioquímica.")
        else:
            st.info("Perfil favorável: Baixo benefício de intensificação.")
            
    with c_against:
        st.markdown("#### Pesa Contra Intensificação")
        contra_factors = []
        if inputs['has_cardio']:
            contra_factors.append("Risco Cardiovascular: Alerta para ADT.")
        if inputs['has_metabolic']:
            contra_factors.append("Risco Metabólico: Piora com ADT.")
        if inputs['has_bone']:
            contra_factors.append("Saúde Óssea: Risco de fratura com ADT.")
        if inputs['life_expectancy'] == LifeExpectancy.SHORT:
            contra_factors.append("Expectativa de Vida Limitada: Toxicidade pode superar benefício.")
        if inputs['has_libido_concern']:
            contra_factors.append("Preferência do Paciente: Forte aversão aos efeitos na libido.")
            
        if contra_factors:
            for c in contra_factors:
                st.error(c)
        else:
            st.write("Sem comorbidades maiores proibitivas selecionadas.")

    # Block 3: Final Recommendation
    st.markdown("---")
    st.subheader("3. Sugestão Terapêutica (Baseada em Diretrizes)")
    
    # Logic to frame the recommendation text nicely
    # Note: The 'adt' input is the "ideal" clinical recommendation from logic.py
    # We clarify it based on comorbidities.
    
    import textwrap
    
    st.markdown(f"**Campo de Radioterapia:** **{rt_field.value}**")
    
    rec_text = adt.value
    
    # Adjust display text if comorbidities exist but clinical risk suggests ADT
    is_contraindicated = (inputs['has_cardio'] or inputs['has_metabolic']) and adt != ADTRecommendation.NONE
    
    st.markdown("### Estratégia Preferida")
    if is_contraindicated:
        st.warning(f"Indicação Clínica: **{rec_text}**")
        st.markdown("*Nota: Devido às comorbidades, considerar redução de duração ou monitoramento estrito.*")
    else:
        st.success(f"**{rec_text}**")
        
    # Absolute Benefits Section
    benefit_data = settings_benefits(risk, adt)
    if benefit_data['arr_5yr'] != 0.0:
        st.markdown("---")
        st.subheader("Benefício Absoluto Estimado (5 anos)")
        st.markdown("*Comparado à radioterapia isolada (Estimativa baseada em ensaios clínicos)*")
        
        # 3 Columns: Gauge ARR | Metric ARR | Metric NNT
        b_col0, b_col1, b_col2 = st.columns([1, 1, 1])
        
        with b_col0:
             from . import visuals
             fig_arr = visuals.create_arr_gauge(benefit_data['arr_5yr'])
             st.plotly_chart(fig_arr, use_container_width=True)

        with b_col1:
             st.markdown("### ")  # Spacer to align with gauge
             st.markdown("### ")
             st.metric(
                label="Redução Absoluta de Risco", 
                value=f"{benefit_data['arr_5yr']}%"
            )
            
        with b_col2:
             st.markdown("### ") # Spacer
             st.markdown("### ")
             st.metric(
                label="Número Necessário para Tratar (NNT)", 
                value=f"{benefit_data['nnt']}",
                help="Número de pacientes que precisam receber ADT para evitar 1 evento de recorrência/metástase."
            )
            
        # Icon Array (Waffle)
        st.markdown("---")
        st.markdown("### Visualização de Impacto (100 Pacientes)")
        
        w_col1, w_col2 = st.columns([1, 1])
        
        baseline_risk = logic.get_baseline_recurrence_risk(risk)
        waffle_fig = visuals.create_waffle_chart(benefit_data['arr_5yr'], baseline_risk)
        
        with w_col1:
            st.plotly_chart(waffle_fig, use_container_width=True)
            
        with w_col2:
            st.markdown("#### Legenda")
            st.markdown(f"🔴 **Recorrência ({int(max(baseline_risk - (benefit_data['arr_5yr'] if isinstance(benefit_data['arr_5yr'], (int, float)) else 0), 0))}):** Pacientes que recidivam mesmo com o tratamento.")
            st.markdown(f"🟢 **Benefício ({int(benefit_data['arr_5yr'] if isinstance(benefit_data['arr_5yr'], (int, float)) else 0)}):** Pacientes salvos da recorrência pela ADT.")
            st.markdown(f"🔵 **Sem Recorrência ({100 - int(baseline_risk)}):** Pacientes que ficariam bem mesmo sem ADT (sRT sozinha já curou ou doença lenta).")

    st.markdown("#### Alternativa Razoável")
    if risk == RiskLevel.HIGH:
        if is_contraindicated:
            st.write("sRT + ADT Curta (Descalonamento por toxicidade)")
        else:
            st.write("sRT + ADT Curta (Se preocupação com qualidade de vida)")
    elif risk == RiskLevel.INTERMEDIATE:
        st.write("sRT Isolada (Discussão sobre benefício marginal da ADT)")
    else:
        st.write("Observação vigilante (em casos selecionados) ou sRT precoce sem ADT.")

    # Disclaimer (on screen)
    with st.expander("Aviso Legal (Disclaimer)", expanded=False):
        st.markdown("""
        **AVISO LEGAL**: Esta ferramenta é destinada exclusivamente ao uso por profissionais de saúde qualificados. 
        As estimativas de risco e benefício são baseadas em dados da literatura médica agregada e podem não refletir o resultado individual de cada paciente.
        Esta calculadora **NÃO** fornece aconselhamento médico direto, diagnóstico ou prescrição. 
        A decisão final sobre o tratamento deve ser tomada pelo médico assistente, em conjunto com o paciente, considerando todas as variáveis clínicas.
        O desenvolvedor não se responsabiliza por decisões tomadas com base nestas informações.
        """)

    # References
    with st.expander("Referências Bibliográficas", expanded=False):
        st.markdown("""
        1. Zaurito P, Cosenza A, Quarta L, Scilipoti S, Longoni M, Santangelo A, et al. A Narrative Review of Treatment Options for Patients with Node-Positive Disease After Radical Prostatectomy: Current Evidence and Controversies. Cancers. 2025;17(17):2792.
        2. Shimabukuro T, Tokunaga T, Shimizu K, Fujii N, Kobayashi K, Hiroyoshi T, et al. Time to Prostate-Specific Antigen Failure as a Unique Prognosticator of Overall Survival in Biochemically Recurrent Prostate Cancer Patients Undergoing Radical Prostatectomy. Adv Urol. 2025;2025:2961319.
        3. Challis B, Kneebone A, Eade T, Guo L, Atyeo J, Brown C, et al. Avoiding prostate bed radiation for the PSMA-PET detected nodal recurrence patient post prostatectomy. Clin Transl Radiat Oncol. 2025;50:100896.
        4. Cornford P, Tilki D, van den Bergh RCN, Eberli D, De Meerleer G, De Santis M, et al. EAU-EANM-ESTRO-ESUR-ISUP-SIOG Guidelines on Prostate Cancer. Arnhem (NL): EAU Guidelines Office; 2025.
        5. Di Giorgio A, Siepe G, Serani F, Di Franco M, Malizia C, Castellucci P, et al. Long-term outcomes of PSMA PET/CT-guided radiotherapy in biochemical failure patients post-radical prostatectomy: a 5-year follow-up analysis. Eur J Nucl Med Mol Imaging. 2025;52(13):3720–3729.
        6. Yang YJ, Min K, Tae JH, Lee CU, Choi J, Kim JH, et al. Oncologic outcomes of salvage radiotherapy and lymphadenectomy for positron emission tomography-positive lymph nodes in biochemical recurrence: A systematic review to inform treatment decisions. Prostate Int. 2025; (In Press).
        7. Vorbach SM, Rittmayer H, Seppi T, Nilica B, Kafka M, Ganswindt U. PSMA-PET/CT-based salvage elective nodal radiotherapy for lymph node recurrence following radical prostatectomy. World J Urol. 2025;43(1):571.
        8. Belliveau C, Saad F, Duplan D, Petit C, Delouya G, Taussky D, et al. Prostate-Specific Membrane Antigen PET-Guided Intensification of Salvage Radiotherapy After Radical Prostatectomy: A Phase 2 Randomized Clinical Trial (PSMAiSRT). JAMA Oncol. 2025. doi:10.1001/jamaoncol.2025.3746.
        9. Le QC, Siech C, Hoeh B, Saad F, Preisser F, Tilki D, et al. Influence of Concomitant Androgen Deprivation Therapy and Its Duration for Salvage Radiation After Radical Prostatectomy: A Systematic Review and Network Meta-analysis According to Published Data. Eur Urol Oncol. 2025;8(2):1406–1415.
        10. Gillessen S, Turco F, Davis ID, Efstathiou JA, Fizazi K, James ND, et al. Consensus Questions APCCC 2024. Advanced Prostate Cancer Consensus Conference; 2024 Apr 25-27; Lugano, Switzerland.
        11. Advanced Prostate Cancer Consensus Conference (APCCC). Resumo das Perguntas, Alternativas e Status de Votação: Persistência de PSA e Recidiva Bioquímica pós-Prostatectomia Radical. Lugano: APCCC; 2024.
        12. Morgan TM, Boorjian SA, Buyyounouski MK, Chapin BF, Chen DYT, Cheng HH, et al. Salvage Therapy for Prostate Cancer: AUA/ASTRO/SUO Guideline 2024. Linthicum (MD): American Urological Association; 2024.
        13. Gillessen S, Turco F, Davis ID, Efstathiou JA, Fizazi K, James ND, et al. Management of Patients with Advanced Prostate Cancer. Report from the 2024 Advanced Prostate Cancer Consensus Conference (APCCC). Eur Urol. 2024. doi:10.1016/j.eururo.2024.09.017.
        14. Instituto D’Or de Oncologia (IDO). Projeto de Pesquisa: Manejo do Paciente com Recidiva Bioquímica Pós-Prostatectomia Radical e Recorrência Nodal Regional Detectada por PSMA PET/CT. Rio de Janeiro: IDO; 2023.
        15. Tamihardja J, Zehner L, Hartrampf P, Lisowski D, Kneitz S, Cirsi S, et al. Salvage Nodal Radiotherapy as Metastasis-Directed Therapy for Oligorecurrent Prostate Cancer Detected by Positron Emission Tomography Shows Favorable Outcome in Long-Term Follow-Up. Cancers. 2022;14(15):3766.
        16. Attard G, Murphy L, Clarke NW, Cross W, Jones RJ, Parker CC, et al. Abiraterone acetate and prednisolone with or without enzalutamide for high-risk non-metastatic prostate cancer: a meta-analysis of primary results from two randomised controlled phase 3 trials of the STAMPEDE platform protocol. Lancet. 2022;399(10323):447–460
        """)

    # Export Section
    st.markdown("---")
    st.markdown("### Exportar Relatório")
    
    col_pdf, col_txt = st.columns(2)
    
    from . import utils, visuals
    
    # Text Export
    summary_text = utils.generate_summary_text(inputs, risk, rt_field, adt, benefit_data)
    col_txt.download_button(
        label="📄 Baixar Resumo (.txt)",
        data=summary_text,
        file_name="resumo_clinico_adt.txt",
        mime="text/plain"
    )
    
    # PDF Export
    # We generate charts on the fly for the PDF
    if col_pdf.button("🖨️ Gerar PDF com Gráficos"):
        with st.spinner("Gerando gráficos e compilando PDF..."):
            visuals_map = {}
            if benefit_data['arr_5yr'] != 0.0:
                 # Reconstruct specific figures for export (or reuse cached if stored)
                 # We need to call functions from visuals
                 # 1. ARR Gauge
                 fig_arr = visuals.create_arr_gauge(benefit_data['arr_5yr'])
                 visuals_map['arr_gauge'] = visuals.get_chart_image(fig_arr)
                 
                 # 2. Waffle
                 local_baseline = logic.get_baseline_recurrence_risk(risk)
                 fig_waffle = visuals.create_waffle_chart(benefit_data['arr_5yr'], local_baseline)
                 visuals_map['waffle'] = visuals.get_chart_image(fig_waffle)
            
            pdf_bytes = utils.create_pdf(inputs, risk, rt_field, adt, benefit_data, visuals_map)
            
            st.download_button(
                label="📥 Baixar PDF Pronto",
                data=pdf_bytes,
                file_name="relatorio_clinico_adt.pdf",
                mime="application/pdf"
            )

def settings_benefits(risk, adt):
    # This helper isolates the logic call to avoid circular imports? 
    # Actually logic is imported in main app. 
    # But ui.py doesn't import logic by default in the plan structure (app.py does).
    # Wait, ui.py handles rendering. It should assume the data is passed OR import logic.
    # In app.py we pass risk, rt_field, adt, inputs.
    # We should probably call logic.get_absolute_benefits inside ui.py or pass it from app.py
    # For simplicity, I'll update render_results to accept benefit_stats or call logic.
    # Let's import logic inside the function to avoid top-level circular dependency if any.
    from . import logic
    return logic.get_absolute_benefits(risk, adt)
