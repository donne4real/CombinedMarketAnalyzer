import plotly.graph_objects as go

def create_speedometer(score: float, max_score: int, title: str = "Total Score") -> go.Figure:
    """
    Creates a Plotly gauge chart (speedometer) from 0 to max_score.
    Color gradient goes from Red (Avoid) to Yellow (Neutral) to Green (Strong Buy).
    """
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 24}},
        gauge={
            'axis': {'range': [0, max_score], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "rgba(0,0,0,0)"},  # Hide the default bar
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, max_score * 0.33], 'color': "rgba(220, 38, 38, 0.7)"},      # Red
                {'range': [max_score * 0.33, max_score * 0.66], 'color': "rgba(217, 119, 6, 0.7)"}, # Yellow/Orange
                {'range': [max_score * 0.66, max_score], 'color': "rgba(5, 150, 105, 0.7)"}       # Green
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': score
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        font={'color': "var(--text-color)"}
    )
    
    return fig

def create_radar_chart(strategies: dict, category_mapping: dict, title: str = "Strategy Analysis") -> go.Figure:
    """
    Creates a Plotly radar (spider) chart categorizing individual strategy scores
    into broader buckets (e.g., Value, Growth, Safety, Momentum).
    """
    categories = list(category_mapping.keys())
    values = []
    
    # Calculate average score for each broad category
    for cat in categories:
        cat_scores = []
        for strat_key in category_mapping[cat]:
            if strat_key in strategies:
                cat_scores.append(strategies[strat_key].get("score", 0))
        
        avg_score = sum(cat_scores) / len(cat_scores) if cat_scores else 0
        values.append(avg_score)
        
    # Close the radar loop
    categories.append(categories[0])
    values.append(values[0])
        
    fig = go.Figure(data=go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        fillcolor='rgba(102, 126, 234, 0.5)',
        line=dict(color='#1E3A8A'),
        marker=dict(size=8)
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 10]
            )
        ),
        showlegend=False,
        title=dict(text=title, x=0.5),
        height=350,
        margin=dict(l=40, r=40, t=60, b=40),
        paper_bgcolor="rgba(0,0,0,0)"
    )
    
    return fig
