import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Set page configuration for a premium look
st.set_page_config(
    page_title="Hands-On Persona Analyzer",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS to inject some of our styling
st.markdown("""
<style>
    .stApp {
        background-color: #0b0f19;
    }
    h1 {
        background: linear-gradient(90deg, #6366f1, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-family: 'Outfit', sans-serif;
        text-align: center;
        padding-bottom: 2rem;
    }
    .metric-card {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        padding: 1rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .persona-badge {
        display: inline-block;
        padding: 0.5rem 1.5rem;
        background: rgba(236, 72, 153, 0.2);
        color: #ec4899;
        border: 1px solid #ec4899;
        border-radius: 999px;
        font-weight: 600;
        font-size: 1.2rem;
        text-transform: uppercase;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("AI Hands-On Persona Analyzer")
st.markdown("<p style='text-align: center; color: #94a3b8; margin-bottom: 2rem;'>Enter a GitHub username to discover their engineering profile</p>", unsafe_allow_html=True)

# Define API endpoint. When deployed, make sure this Render URL is correct.
API_URL = "https://ai-based-hands-on-skill-analyzer-1.onrender.com/api/analyze"

with st.form("analysis_form"):
    st.markdown("### Provide Developer Data")
    github_username = st.text_input("GitHub Username *", placeholder="e.g. torvalds")
    extra_urls = st.text_input("Deployed Project URLs (Optional)", placeholder="https://app.com, https://demo.com")
    video_url = st.text_input("Demo Video URL (Optional)", placeholder="https://youtube.com/...")
    
    submitted = st.form_submit_button("Analyze Profile", use_container_width=True)

if submitted:
    if not github_username:
        st.error("Please provide a GitHub username.")
    else:
        with st.spinner("Analyzing GitHub data, extracting signals... This may take a few seconds."):
            payload = {"github_username": github_username}
            if extra_urls:
                payload["extra_urls"] = [url.strip() for url in extra_urls.split(",") if url.strip()]
            if video_url:
                payload["video_urls"] = [video_url.strip()]
                
            try:
                response = requests.post(API_URL, json=payload, timeout=30)
                if response.status_code == 200:
                    data = response.json()
                    
                    if "raw_data" in data and "github_data" in data["raw_data"] and data["raw_data"]["github_data"].get("error"):
                        st.error(f"GitHub Error: {data['raw_data']['github_data']['error']}")
                        st.stop()
                        
                    analysis = data["analysis"]
                    metrics = analysis["metrics"]
                    top_langs = data["raw_data"]["github_data"].get("top_languages", {})
                    
                    st.markdown("---")
                    
                    # --- Header Section ---
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"<h2>@{github_username}</h2>", unsafe_allow_html=True)
                        st.markdown(f"<div class='persona-badge'>{analysis['persona']}</div>", unsafe_allow_html=True)
                    with col2:
                        st.metric(label="HANDS-ON SCORE", value=f"{analysis['hands_on_score']}/100")
                        
                    # --- Metrics Row ---
                    st.markdown("<br>", unsafe_allow_html=True)
                    m1, m2, m3, m4 = st.columns(4)
                    m1.metric("Original Repos", metrics["original_repos"])
                    m2.metric("Total Stars", metrics["total_stars"])
                    m3.metric("Languages Used", metrics["unique_languages"])
                    m4.metric("Deployed Apps", metrics["active_links"])
                    
                    st.markdown("---")
                    
                    # --- Charts Row ---
                    c1, c2 = st.columns(2)
                    
                    with c1:
                        st.markdown("### Score Breakdown")
                        breakdown_data = analysis["breakdown"]
                        
                        # Data prep for Plotly Radar
                        categories = ['Project Evidence', 'GitHub Activity', 'Engineering Practice', 'Collaboration']
                        valores = [
                            (breakdown_data['project_evidence'] / 30) * 100,
                            (breakdown_data['github_activity'] / 30) * 100,
                            (breakdown_data['engineering_practice'] / 20) * 100,
                            (breakdown_data['collaboration'] / 20) * 100
                        ]
                        
                        df_radar = pd.DataFrame(dict(r=valores, theta=categories))
                        
                        fig_radar = px.line_polar(df_radar, r='r', theta='theta', line_close=True,
                                                 template="plotly_dark")
                        fig_radar.update_traces(fill='toself', line_color='#6366f1', fillcolor='rgba(99, 102, 241, 0.4)')
                        fig_radar.update_layout(
                            polar=dict(radialaxis=dict(visible=False, range=[0, 100])),
                            showlegend=False,
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)'
                        )
                        st.plotly_chart(fig_radar, use_container_width=True)
                        
                    with c2:
                        st.markdown("### Top Languages")
                        if top_langs:
                            # Take top 5
                            langs = list(top_langs.keys())[:5]
                            counts = list(top_langs.values())[:5]
                            
                            fig_donut = px.pie(names=langs, values=counts, hole=0.7, 
                                             template="plotly_dark",
                                             color_discrete_sequence=['#6366f1', '#ec4899', '#10b981', '#f59e0b', '#8b5cf6'])
                            fig_donut.update_layout(
                                paper_bgcolor='rgba(0,0,0,0)',
                                plot_bgcolor='rgba(0,0,0,0)',
                                legend=dict(orientation="v", yanchor="top", y=1, xanchor="left", x=1.0)
                            )
                            st.plotly_chart(fig_donut, use_container_width=True)
                        else:
                            st.info("No language data available for this user.")
                            
                    st.markdown("---")
                    st.markdown("### Key Insights")
                    for insight in analysis["insights"]:
                        st.success(insight, icon="✅")
                    
                else:
                    st.error(f"Error communicating with backend API (Status {response.status_code})")
            except requests.exceptions.ConnectionError:
                st.error("Failed to connect to the backend server. Is the Render link correct?")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
