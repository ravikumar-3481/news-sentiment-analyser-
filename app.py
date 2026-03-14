import streamlit as st
import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- CONFIGURATION ---
st.set_page_config(
    page_title="NewsPulse AI | Sentiment Analyzer",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed" # Hide sidebar by default
)

# --- STYLING ---
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #007bff;
        color: white;
    }
    .nav-container {
        display: flex;
        justify-content: center;
        background-color: #ffffff;
        padding: 1rem;
        border-bottom: 1px solid #e0e0e0;
        margin-bottom: 2rem;
    }
    .reportview-container .main .block-container {
        padding-top: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIC FUNCTIONS ---
def get_sentiment(text):
    """Performs sentiment analysis using TextBlob."""
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    if polarity > 0.1:
        return "Positive", polarity
    elif polarity < -0.1:
        return "Negative", polarity
    else:
        return "Neutral", polarity

def scrape_news(url):
    """Scrapes headlines from common news structures."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for common headline tags
        found_headlines = []
        for tag in soup.find_all(['h1', 'h2', 'h3']):
            text = tag.get_text().strip()
            if len(text.split()) > 4: # Filter out short menu items
                found_headlines.append(text)
        
        return list(set(found_headlines)) # Return unique headlines
    except Exception as e:
        return f"Error: {str(e)}"

# --- NAVIGATION ---
# Using a horizontal radio button for navigation instead of a sidebar
st.markdown("<h1 style='text-align: center; color: #1E3A8A;'>NewsPulse AI 📈</h1>", unsafe_allow_html=True)
selected_page = st.segmented_control(
    label="Navigation",
    options=["🏠 Home", "📊 Dashboard", "ℹ️ About"],
    default="🏠 Home",
    label_visibility="collapsed"
)

st.divider()

# --- PAGE: HOME ---
if selected_page == "🏠 Home":
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("What is NewsPulse AI?")
        st.write("""
        **NewsPulse AI** is a real-time Natural Language Processing (NLP) tool designed to bridge 
        the gap between raw digital news and actionable sentiment data. In an era of information 
        overload, understanding the collective "mood" of the media regarding specific topics 
        (like *AI Ethics*, *Global Markets*, or *Climate Change*) is essential for decision-makers.
        """)
        
        st.subheader("How It Works")
        st.info("""
        1. **Scraping:** The engine sends a request to a specified news URL and extracts headlines using `BeautifulSoup`.
        2. **Processing:** Text is cleaned and tokenized to prepare for emotional evaluation.
        3. **Analysis:** Using the `TextBlob` library, each headline is assigned a **Polarity Score** ranging from -1.0 (Very Negative) to +1.0 (Very Positive).
        4. **Visualization:** Data is aggregated and presented through interactive charts to reveal the prevailing public sentiment.
        """)
    
    with col2:
        st.image("https://images.unsplash.com/photo-1504711434969-e33886168f5c?auto=format&fit=crop&q=80&w=600", caption="Global News Analysis")
        st.success("Target Industries: \n- Fintech & Trading \n- Public Relations \n- Policy Research")

# --- PAGE: DASHBOARD ---
elif selected_page == "📊 Dashboard":
    st.subheader("Real-Time Sentiment Analysis")
    
    # Pre-defined options for quick testing
    target_topic = st.selectbox(
        "Choose a Preset Source or Enter Custom URL below:",
        ["https://techcrunch.com/category/artificial-intelligence/", 
         "https://www.bbc.com/news/business", 
         "Custom URL"]
    )
    
    custom_url = ""
    if target_topic == "Custom URL":
        custom_url = st.text_input("Enter News Website URL:", "https://news.ycombinator.com/")
    
    url_to_use = custom_url if target_topic == "Custom URL" else target_topic

    if st.button("Run Analysis"):
        headlines = scrape_news(url_to_use)
        
        if isinstance(headlines, str) and headlines.startswith("Error"):
            st.error(headlines)
        elif not headlines:
            st.warning("No headlines detected. Try a different URL or check the site structure.")
        else:
            # Data Processing
            data = []
            for h in headlines:
                sentiment, score = get_sentiment(h)
                data.append({"Headline": h, "Sentiment": sentiment, "Score": score})
            
            df = pd.DataFrame(data)
            
            # Key Metrics
            m1, m2, m3 = st.columns(3)
            m1.metric("Total Headlines", len(df))
            m2.metric("Positive 🟢", len(df[df['Sentiment'] == 'Positive']))
            m3.metric("Negative 🔴", len(df[df['Sentiment'] == 'Negative']))
            
            # Visualization
            c1, c2 = st.columns([1, 1])
            
            with c1:
                fig_pie = px.pie(
                    df, names='Sentiment', 
                    title='Overall Sentiment Distribution',
                    color='Sentiment',
                    color_discrete_map={'Positive':'#2ecc71', 'Neutral':'#95a5a6', 'Negative':'#e74c3c'},
                    hole=0.4
                )
                st.plotly_chart(fig_pie, use_container_width=True)
                
            with c2:
                fig_hist = px.histogram(
                    df, x='Score', 
                    title='Sentiment Polarity Spread',
                    nbins=20,
                    color_discrete_sequence=['#1E3A8A']
                )
                st.plotly_chart(fig_hist, use_container_width=True)

            # Raw Data
            with st.expander("View Scraped Headlines & Individual Scores"):
                st.dataframe(df, use_container_width=True)

# --- PAGE: ABOUT ---
elif selected_page == "ℹ️ About":
    st.subheader("Project Architecture")
    st.markdown("""
    ### Technical Stack
    - **Frontend:** [Streamlit](https://streamlit.io/) for the interactive web interface.
    - **Scraping:** [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) for HTML parsing.
    - **NLP Engine:** [TextBlob](https://textblob.readthedocs.io/) for linguistic processing and polarity calculation.
    - **Visuals:** [Plotly Express](https://plotly.com/python/) for dynamic charting.

    ### Real-World Value
    Traders use these sentiment "spikes" to identify market volatility before technical indicators catch up. PR firms monitor these dashboards to track brand health during a product launch or crisis.

    ---
    *Developed as a demonstration of NLP & Web Scraping integration.*
    """)
    
    st.caption(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# --- FOOTER ---
st.markdown("---")
st.markdown("<p style='text-align: center; color: gray;'>NewsPulse AI - Data-Driven News Intelligence</p>", unsafe_allow_html=True)
