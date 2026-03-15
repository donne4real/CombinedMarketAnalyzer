import os
import json
import streamlit as st
from openai import OpenAI
from typing import Dict, Any

def get_openai_client() -> OpenAI | None:
    """Initialize the OpenAI client using the API key from Streamlit secrets or environment."""
    api_key = os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        try:
            api_key = st.secrets.get("OPENAI_API_KEY")
        except FileNotFoundError:
            pass
            
    if not api_key:
        return None
        
    return OpenAI(api_key=api_key)

def generate_stock_summary(asset_name: str, ticker: str, asset_type: str, strategies: Dict[str, Any]) -> str:
    """
    Generates a 2-3 sentence plain-English summary of the asset's strategy performance.
    
    Args:
        asset_name: Full name of the company/fund
        ticker: Ticker symbol
        asset_type: 'Stock', 'ETF', or 'Mutual Fund'
        strategies: The dictionary of strategy scores and reasons.
        
    Returns:
        A concise string summary.
    """
    client = get_openai_client()
    if not client:
        return "⚠️ OpenAI API key not found. Please set the `OPENAI_API_KEY` environment variable or Streamlit secret to enable AI Summaries."
        
    # Extract the total score and a few key strategy drivers
    total_score = strategies.get("total_score", 0)
    
    # We don't want to pass the entire massive dict, just a simplified version
    simplified_strategies = {}
    for k, v in strategies.items():
        if isinstance(v, dict) and "score" in v and "reason" in v:
            if v["score"] >= 8 or v["score"] <= 3: # Only send strong signals to save tokens
                simplified_strategies[k] = {"score": v["score"], "reason": v["reason"]}
                
    prompt = f"""
    You are an expert financial advisor for novice investors. 
    Analyze this {asset_type}: {asset_name} ({ticker}).
    The asset scored {total_score} points based on our algorithmic strategies.
    
    Key strategy signals:
    {json.dumps(simplified_strategies, indent=2)}
    
    Task: Write a highly concise, 2-3 sentence summary explaining what this means in plain English.
    Avoid jargon. Tell the investor if this looks like a strong fundamental asset, a risky play, or something in between based on the scores.
    DO NOT provide financial advice to buy or sell. Just summarize the algorithmic signals.
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful, jargon-free financial summarizer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ Failed to generate AI summary: {str(e)}"
