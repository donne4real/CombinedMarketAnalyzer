"""
Shared UI helpers for Streamlit pages.

This module contains:
- Common CSS styles
- Page headers
- Reusable UI components
"""

import streamlit as st


def get_common_css():
    """Get common CSS styles for all pages."""
    return """
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E3A8A;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .strategy-card {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    .score-display {
        font-size: 2rem;
        font-weight: bold;
        color: #1E3A8A;
    }
    .positive-score {
        color: #10b981;
    }
    .negative-score {
        color: #ef4444;
    }
    .neutral-score {
        color: #f59e0b;
    }
    </style>
    """


def render_page_header(title: str, icon: str = "📈", description: str = ""):
    """Render a consistent page header.
    
    Args:
        title: Page title
        icon: Emoji icon for the title
        description: Optional description text
    """
    st.markdown(get_common_css(), unsafe_allow_html=True)
    st.markdown(f"<h1 class='main-header'>{icon} {title}</h1>", unsafe_allow_html=True)
    if description:
        st.markdown(f"<p style='color: #6b7280; font-size: 1.1rem;'>{description}</p>", unsafe_allow_html=True)
    st.divider()


def render_strategy_card(strategy_name: str, score: float, reason: str, max_score: float = 10.0):
    """Render a strategy card with score and reason.
    
    Args:
        strategy_name: Name of the strategy
        score: Score (0-10)
        reason: Explanation/reason for the score
        max_score: Maximum possible score (default 10)
    """
    # Determine color based on score
    if score >= max_score * 0.8:
        score_color = "positive-score"
        score_emoji = "🟢"
    elif score >= max_score * 0.6:
        score_color = "neutral-score"
        score_emoji = "🟡"
    elif score >= max_score * 0.4:
        score_color = "neutral-score"
        score_emoji = "🟠"
    else:
        score_color = "negative-score"
        score_emoji = "🔴"
    
    with st.container():
        st.markdown(f"""
        <div class="strategy-card">
            <h3 style="margin-top: 0;">{strategy_name} {score_emoji}</h3>
            <div class="score-display {score_color}">
                Score: {score:.1f}/{max_score:.1f}
            </div>
            <p style="margin-bottom: 0; opacity: 0.9;">{reason}</p>
        </div>
        """, unsafe_allow_html=True)


def render_total_score(total_score: float, max_score: float = 100.0, label: str = "Total Score"):
    """Render a total score display.
    
    Args:
        total_score: The total score to display
        max_score: Maximum possible score (default 100)
        label: Label for the score
    """
    percentage = (total_score / max_score) * 100
    
    # Determine color
    if percentage >= 80:
        color = "#10b981"  # Green
        emoji = "🌟"
    elif percentage >= 60:
        color = "#f59e0b"  # Amber
        emoji = "✨"
    elif percentage >= 40:
        color = "#f97316"  # Orange
        emoji = "⚠️"
    else:
        color = "#ef4444"  # Red
        emoji = "❌"
    
    st.markdown(f"""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, {color}22, {color}11); border-radius: 15px; margin: 2rem 0;">
        <h2 style="color: {color}; margin-bottom: 0.5rem;">{emoji} {label}</h2>
        <div style="font-size: 4rem; font-weight: bold; color: {color};">
            {total_score:.1f}/{max_score:.1f}
        </div>
        <div style="font-size: 1.2rem; color: #6b7280;">
            {percentage:.1f}%
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_metric_card(label: str, value: str, delta: str = None, delta_color: str = "normal"):
    """Render a metric card with optional delta.
    
    Args:
        label: Label for the metric
        value: Value to display
        delta: Optional delta/change value
        delta_color: Color for delta ("normal", "inverse", "off")
    """
    if delta:
        st.metric(label=label, value=value, delta=delta, delta_color=delta_color)
    else:
        st.metric(label=label, value=value)


def render_progress_bar(progress: float, label: str = "Progress"):
    """Render a styled progress bar.
    
    Args:
        progress: Progress value (0.0 to 1.0)
        label: Label for the progress bar
    """
    st.progress(progress, text=f"{label}: {progress*100:.1f}%")


def render_info_box(message: str, type: str = "info"):
    """Render an info box with appropriate styling.
    
    Args:
        message: Message to display
        type: Type of box ("info", "success", "warning", "error")
    """
    colors = {
        "info": "#3b82f6",
        "success": "#10b981",
        "warning": "#f59e0b",
        "error": "#ef4444"
    }
    emojis = {
        "info": "ℹ️",
        "success": "✅",
        "warning": "⚠️",
        "error": "❌"
    }
    
    color = colors.get(type, "#3b82f6")
    emoji = emojis.get(type, "ℹ️")
    
    st.markdown(f"""
    <div style="padding: 1rem; background: {color}22; border-left: 4px solid {color}; border-radius: 5px; margin: 1rem 0;">
        <span style="font-size: 1.5rem;">{emoji}</span> <span style="margin-left: 0.5rem;">{message}</span>
    </div>
    """, unsafe_allow_html=True)
