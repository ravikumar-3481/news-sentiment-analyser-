import streamlit as st
import requests
from bs4 import BeautifulSoup
from textblob import TextBlob
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from collections import Counter
import re

# --- CONFIGURATION ---
st.set_page_config(
    page_title="NewsPulse AI | Advanced Sentiment Engine",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- STYLING ---
st.markdown("""
    <style>
    .main {
        background-color: #f4f7f9;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3.5em;
        background-color: #1E3A8A;
        color: white;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #3b82f6;
        border: none;
    }
    .metric-card {
        background-color: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        text-align: center;
    }
    .dev-card {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        padding: 25px;
        border-radius: 15px;
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIC FUNCTIONS ---
def get_sentiment(text):
    """Performs sentiment analysis using TextBlob."""
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    subjectivity = analysis.sentiment.subjectivity
    
    if polarity > 0.1:
        label = "Positive"
    elif polarity < -0.1:
        label = "Negative"
    else:
        label = "Neutral"
    
    return label, round(polarity, 2), round(subjectivity, 2)

def extract_keywords(text_list):
    """Simple keyword extraction by frequency."""
    words = []
    stopwords = set(['the', 'and', 'for', 'that', 'with', 'from', 'this', 'news', 'says', 'how', 'why', 'what'])
    for text in text_list:
        clean = re.sub(r'[^\w\s]', '', text.lower())
        words.extend([w for w in clean.split() if w not in stopwords and len(w) > 3])
    return Counter(words).most_common(10)

def scrape_news(url):
    """Scrapes headlines from common news structures."""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        found_headlines = []
        # Targeting common headline wrappers
        for tag in soup.find_all(['h1', 'h2', 'h3', 'h4']):
            text = tag.get_text().strip()
            if len(text.split()) > 4 and len(text) < 200: 
                found_headlines.append(text)
        
        return list(dict.fromkeys(found_headlines)) # Preserve order while removing duplicates
    except Exception as e:
        return f"Error: {str(e)}"

# --- NAVIGATION ---
st.markdown("<h1 style='text-align: center; color: #1E3A8A; margin-bottom: 0;'>NewsPulse AI 📡</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b;'>Intelligence for the Modern Information Age</p>", unsafe_allow_html=True)

selected_page = st.segmented_control(
    label="Navigation",
    options=["🏠 Home", "📊 Dashboard", "ℹ️ About"],
    default="🏠 Home",
    label_visibility="collapsed"
)

st.divider()

# --- PAGE: HOME ---
if selected_page == "🏠 Home":
    col1, col2 = st.columns([1.5, 1])
    
    with col1:
        st.subheader("🚀 Project Overview")
        st.write("""
        **NewsPulse AI** is a sophisticated Sentiment Analysis engine that utilizes 
        web-scraping and Natural Language Processing to decode the emotional undertone 
        of current events. 
        
        In today's fast-paced world, market fluctuations and public opinion are often 
        driven by headlines before they are reflected in hard data. This tool allows users 
        to quantify that "vibe" instantly.
        """)
        
        st.subheader("🛠️ Core Features")
        features = {
            "Real-Time Scraping": "Extracts live headlines from any major news portal.",
            "Sentiment Grading": "Classifies text into Positive, Negative, or Neutral clusters.",
            "Bias Detection": "Measures 'Subjectivity' to distinguish facts from opinions.",
            "Keyword Analysis": "Identifies recurring themes across dozens of articles."
        }
        for f, d in features.items():
            st.markdown(f"**{f}:** {d}")

    with col2:
        # --- DEVELOPER PROFILE ---
        st.markdown("""
            <div class="dev-card">
                <h2 style='margin-top:0;'>Developer Profile</h2>
                <p><strong>Name:</strong> Gemini AI Developer</p>
                <p><strong>Role:</strong> Full-Stack NLP Engineer</p>
                <p><strong>Stack:</strong> Python, Streamlit, NLTK, BeautifulSoup</p>
                <hr style='border-color: rgba(255,255,255,0.2)'>
                <p style='font-size: 0.9em; font-style: italic;'>
                    "Passionate about turning unstructured web data into visual stories."
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        st.success("✨ **Pro Tip:** Use the Dashboard to track 'AI' sentiment shifts daily!")

# --- PAGE: DASHBOARD ---
elif selected_page == "📊 Dashboard":
    st.subheader("Data Extraction & Analysis")
    
    # URL Selection
    target_topic = st.selectbox(
        "Select News Source:",
        ["https://techcrunch.com/category/artificial-intelligence/", 
         "https://www.theverge.com/tech",
         "https://www.bbc.com/news/business",
         "Custom URL"]
    )
    
    url_to_use = target_topic
    if target_topic == "Custom URL":
        url_to_use = st.text_input("Enter Custom URL:", "https://news.ycombinator.com/")
    
    if st.button("🚀 Analyze Now"):
        headlines = scrape_news(url_to_use)
        
        if isinstance(headlines, str) and headlines.startswith("Error"):
            st.error(headlines)
        elif not headlines:
            st.warning("No headlines found. This site may have anti-scraping blocks.")
        else:
            # Processing
            data = []
            for h in headlines:
                label, pol, subj = get_sentiment(h)
                data.append({
                    "Headline": h, 
                    "Sentiment": label, 
                    "Polarity": pol, 
                    "Subjectivity": subj
                })
            
            df = pd.DataFrame(data)
            
            # HIGHLIGHTS SECTION
            st.markdown("### 📈 Sentiment Highlights")
            h1, h2, h3, h4 = st.columns(4)
            avg_pol = df['Polarity'].mean()
            h1.metric("Headlines Found", len(df))
            h2.metric("Avg Polarity", f"{avg_pol:.2f}")
            h3.metric("Positivity Rate", f"{(len(df[df['Sentiment']=='Positive'])/len(df)*100):.1f}%")
            h4.metric("Subjectivity", f"{df['Subjectivity'].mean():.2f}")

            # VISUALIZATION
            v1, v2 = st.columns([1, 1])
            with v1:
                fig_pie = px.pie(df, names='Sentiment', title='Market Mood Distribution',
                                 color='Sentiment', hole=0.5,
                                 color_discrete_map={'Positive':'#10b981', 'Neutral':'#94a3b8', 'Negative':'#ef4444'})
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with v2:
                # Keyword Bar Chart
                keywords = extract_keywords(headlines)
                k_df = pd.DataFrame(keywords, columns=['Word', 'Count'])
                fig_key = px.bar(k_df, x='Count', y='Word', orientation='h', title='Trending Topics',
                                 color_discrete_sequence=['#3b82f6'])
                st.plotly_chart(fig_key, use_container_width=True)

            # FULL TABLE - AS REQUESTED
            st.markdown("### 📋 Complete Scraped Data")
            # Style the table to be more readable
            def color_sentiment(val):
                color = '#10b981' if val == 'Positive' else '#ef4444' if val == 'Negative' else '#94a3b8'
                return f'color: {color}; font-weight: bold;'
            
            styled_df = df.style.applymap(color_sentiment, subset=['Sentiment'])
            st.table(df) # Using st.table for a fixed view, or st.dataframe for interactive

            # EXTREMES
            col_a, col_b = st.columns(2)
            with col_a:
                st.info("⭐ **Most Positive Headline**")
                best = df.loc[df['Polarity'].idxmax()]['Headline']
                st.write(f"*{best}*")
            with col_b:
                st.error("⚠️ **Most Negative Headline**")
                worst = df.loc[df['Polarity'].idxmin()]['Headline']
                st.write(f"*{worst}*")

# --- PAGE: ABOUT ---
elif selected_page == "ℹ️ About":
    st.subheader("Project Documentation")
    st.write("""
    ### Technical Specification
    This application is built using a **Modular Python Architecture**:
    
    1. **Data Layer:** `Requests` and `BeautifulSoup4` handle the DOM parsing.
    2. **Logic Layer:** `TextBlob` (built on NLTK) provides the pre-trained sentiment models.
    3. **Presentation Layer:** `Streamlit` provides the reactive UI, while `Plotly` handles the SVG-based charts.
    
    ### How to Interpret the Scores
    - **Polarity [-1 to 1]:** 1 is pure joy/success, -1 is pure anger/failure.
    - **Subjectivity [0 to 1]:** 0 is purely objective (just facts), 1 is purely subjective (opinionated).
    
    ### Limitations
    As a demo tool, this scraper may not work on sites with heavy JavaScript protection (like X/Twitter or Bloomberg). In professional environments, an API like NewsAPI is recommended.
    """)
    st.divider()
    st.caption(f"NewsPulse AI Engine v2.0 | System Time: {datetime.now().strftime('%H:%M:%S')}")

# --- FOOTER ---
st.markdown("<br><hr><p style='text-align: center; color: #94a3b8;'>Built for Insight • Driven by Data</p>", unsafe_allow_html=True)
