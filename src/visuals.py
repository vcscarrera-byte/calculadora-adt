import plotly.graph_objects as go

def create_nnt_gauge(nnt_value) -> go.Figure:
    """
    Creates a Gauge Chart representing the NNT (Number Needed to Treat).
    
    Logic:
    - Green (High Benefit): NNT 1-15
    - Yellow (Intermediate): NNT 15-30
    - Red (Low Benefit): NNT > 30 (or No Benefit)
    """
    
    # Parse NNT value to a numeric scale for the gauge (0-50)
    # NNT 1 (Best) -> Pointer at 1
    # NNT 50 (Worst) -> Pointer at 50
    
    try:
        if isinstance(nnt_value, int) or isinstance(nnt_value, float):
            value = float(nnt_value)
            display_text = str(nnt_value)
        elif ">" in str(nnt_value):
            value = 45 # High but visible
            display_text = "> 50"
        elif nnt_value == "-" or nnt_value is None:
            value = 50 # Max (Worst)
            display_text = "∞"
        else:
            value = float(nnt_value)
            display_text = str(nnt_value)
    except:
        value = 50
        display_text = "?"

    # Cap value for visualization
    viz_value = min(value, 50)

    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = viz_value,
        title = {'text': "NNT (Benefício)"},
        number = {'suffix': "", 'font': {'size': 20}},
        domain = {'x': [0, 1], 'y': [0, 1]},
        gauge = {
            'axis': {'range': [None, 50], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': "darkblue"}, 
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 15], 'color': 'rgba(0, 255, 0, 0.3)'},   # Green: Good NNT (1-15)
                {'range': [15, 30], 'color': 'rgba(255, 165, 0, 0.3)'}, # Yellow: Intermediate
                {'range': [30, 50], 'color': 'rgba(255, 0, 0, 0.3)'}   # Red: Poor NNT (>30)
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': viz_value
            }
        }
    ))
    
    # Custom annotation for display if needed, but 'number' handles it usually.
    # If it's infinity, we might want to override the valid number display?
    # Plotly 'number' takes the input 'value'. 
    # Let's simple rely on the viz_value for the bar, but we can't easily override the central number text to be string "∞" if mode is gauge+number.
    # Actually we can use 'delta' or just overlay text?
    # For MVP simplicity: Just show the numeric equivalent or user reads the metric card below.

    fig.update_layout(
        height=200, 
        margin=dict(l=20, r=20, t=30, b=20),
        font=dict(family="Arial")
    )
    
    return fig

def create_risk_gauge(risk_value: float) -> go.Figure:
    """
    Creates a Gauge Chart representing the 5-Year Metastasis Probability.
    
    Logic:
    - Red (High Risk): > 40%
    - Orange (Int Risk): 20-40% 
    - Green (Low Risk): < 20%
    """
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = risk_value,
        # title = {'text': "Risco de Metástase (5 anos)"}, # Moving to bottom annotation
        number = {'suffix': "%", 'font': {'size': 40}}, # Also making number noticeable? User just said increase title font 400%.
        domain = {'x': [0, 1], 'y': [0, 1]},
        gauge = {
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': "darkred"}, 
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 20], 'color': 'rgba(0, 255, 0, 0.3)'},   # Green: Low
                {'range': [20, 40], 'color': 'rgba(255, 165, 0, 0.3)'}, # Orange: Med
                {'range': [40, 100], 'color': 'rgba(255, 0, 0, 0.3)'}   # Red: High
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': risk_value
            }
        }
    ))

    fig.update_layout(
        height=300, # Increased height to fit text
        margin=dict(l=20, r=20, t=20, b=80), # High bottom margin for text
        font=dict(family="Arial"),
        annotations=[
            dict(
                text="Risco de Metástase (5 anos)",
                x=0.5,
                y=-0.2, # Below the chart area
                xref="paper",
                yref="paper",
                showarrow=False,
                font=dict(size=25) # Approx 2-3x standard. 400% of 12 is 48, but 48 might be too aggressive for the width. Let's try 30-35.
                                   # User said "400%". standard is usually small. 
                                   # Let's try 35px. It's bold.
            )
        ]
    )
    
    return fig

def create_arr_gauge(arr_value) -> go.Figure:
    """
    Creates a Gauge Chart representing the ARR (%).
    
    Logic (Inverse of NNT):
    - Green (High Benefit): ARR > 6.7% (NNT < 15)
    - Yellow (Intermediate): ARR 3.3% - 6.7%
    - Red (Low Benefit): ARR < 3.3% (NNT > 30)
    """
    
    try:
        if isinstance(arr_value, (int, float)):
            value = float(arr_value)
            # display_text = f"{value}%"
        elif isinstance(arr_value, str) and "<" in arr_value:
             # handle "< 2.0"
             value = 1.0 
        else:
             value = float(arr_value)
    except:
        value = 0

    viz_value = min(value, 20) # Cap at 20% for visualization scale

    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = viz_value,
        title = {'text': "RRA (Redução de Risco)"},
        number = {'suffix': "%", 'font': {'size': 20}},
        domain = {'x': [0, 1], 'y': [0, 1]},
        gauge = {
            'axis': {'range': [None, 20], 'tickwidth': 1, 'tickcolor': "white"},
            'bar': {'color': "darkblue"}, 
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 3.3], 'color': 'rgba(255, 0, 0, 0.3)'},   # Red: Low
                {'range': [3.3, 6.7], 'color': 'rgba(255, 165, 0, 0.3)'}, # Yellow
                {'range': [6.7, 20], 'color': 'rgba(0, 255, 0, 0.3)'}   # Green: High
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': viz_value
            }
        }
    ))

    fig.update_layout(
        height=200, 
        margin=dict(l=20, r=20, t=30, b=20),
        font=dict(family="Arial")
    )
    
    return fig

def get_chart_image(fig: go.Figure) -> bytes:
    """
    Converts a Plotly figure to a PNG image in bytes.
    Requires kaleido.
    """
    # Use 2x scale for better resolution in PDF
    return fig.to_image(format="png", scale=2)

def create_waffle_chart(arr_val, baseline_risk) -> go.Figure:
    """
    Creates a 10x10 Icon Array (Waffle Chart) representing 100 patients.
    
    Categories:
    1. Survived/No Recurrence (Gray/Blue) = 100 - baseline_risk
    2. Benefit/Recurrence Prevented (Green) = ARR
    3. Recurrence/Metastasis (Red) = baseline_risk - ARR
    """
    
    # Parse ARR
    try:
        if isinstance(arr_val, (int, float)):
            arr = float(arr_val)
        elif isinstance(arr_val, str) and "<" in arr_val:
            arr = 1.0
        else:
            arr = float(arr_val)
    except:
        arr = 0.0

    # Ensure logical consistency
    # prevented cannot exceed baseline
    baseline = max(baseline_risk, arr)
    
    n_prevented = int(round(arr))
    n_recurrence = int(round(baseline - arr))
    n_healthy = 100 - n_prevented - n_recurrence
    
    x_vals = []
    y_vals = []
    colors = []
    hover_texts = []
    
    c_healthy = "#1f77b4" # Blue
    c_prevented = "#2ca02c" # Green
    c_recurrence = "#d62728" # Red
    
    statuses = []
    for _ in range(n_recurrence):
        statuses.append({'color': c_recurrence, 'desc': "Recorrência (Sem Resposta à ADT)"})
    for _ in range(n_prevented):
        statuses.append({'color': c_prevented, 'desc': "Benefício (Recorrência Prevenida pela ADT)"})
    for _ in range(n_healthy):
        statuses.append({'color': c_healthy, 'desc': "Sem Recorrência (Cura pela sRT ou Indolente)"})
        
    # Ensure exactly 100
    while len(statuses) < 100:
        statuses.append({'color': c_healthy, 'desc': "Sem Recorrência"})
    while len(statuses) > 100:
        statuses.pop()
        
    # Assign to grid (10 rows of 10)
    for i in range(100):
        row = i // 10
        col = i % 10
        
        x_vals.append(col)
        y_vals.append(row)
        colors.append(statuses[i]['color'])
        hover_texts.append(statuses[i]['desc'])

    fig = go.Figure(data=go.Scatter(
        x=x_vals,
        y=y_vals,
        mode='markers',
        marker=dict(
            symbol='circle',
            size=20,
            color=colors,
            line=dict(width=1, color='DarkSlateGrey')
        ),
        text=hover_texts,
        hoverinfo='text'
    ))

    fig.update_layout(
        title="O que acontece com 100 pacientes?",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.5, 9.5]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.5, 9.5]),
        height=400,
        width=400,
        margin=dict(l=20, r=20, t=40, b=20),
        plot_bgcolor="white"
    )
    
    return fig
