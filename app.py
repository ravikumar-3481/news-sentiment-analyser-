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
from urllib.parse import urljoin

# --- CONFIGURATION ---
st.set_page_config(
    page_title="NewsPulse AI | Advanced Sentiment Engine",
    page_icon="📡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- STATE MANAGEMENT ---
if 'current_page' not in st.session_state:
    st.session_state.current_page = "🏠 Home"
if 'selected_article' not in st.session_state:
    st.session_state.selected_article = None
if 'scraped_data' not in st.session_state:
    st.session_state.scraped_data = None

# --- STYLING ---
st.markdown("""
    <style>
    .main { background-color: #f8fafc; }
    h1, h2, h3 { color: #0f172a; }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3em;
        background-color: #1E3A8A;
        color: white;
        font-weight: 600;
        transition: 0.3s ease-in-out;
        border: none;
    }
    .stButton>button:hover { background-color: #3b82f6; transform: translateY(-2px); }
    .metric-card {
        background-color: white; padding: 20px;
        border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);
        text-align: center; border-top: 4px solid #3b82f6;
    }
    .dev-card {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%);
        color: white; padding: 30px; border-radius: 16px;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
    }
    .dev-card h2 { color: #38bdf8; margin-top: 0; }
    .headline-card {
        background: white; padding: 15px; border-radius: 8px;
        border-left: 5px solid #1e3a8a; margin-bottom: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .article-text {
        font-size: 1.1em; line-height: 1.8; color: #334155;
        background: white; padding: 30px; border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIC FUNCTIONS ---
def get_sentiment(text):
    """Performs sentiment analysis using TextBlob."""
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    subjectivity = analysis.sentiment.subjectivity
    
    if polarity > 0.1: label, emoji = "Positive", "🟢"
    elif polarity < -0.1: label, emoji = "Negative", "🔴"
    else: label, emoji = "Neutral", "⚪"
    
    return label, emoji, round(polarity, 2), round(subjectivity, 2)

def extract_keywords(text_list):
    """Simple keyword extraction by frequency."""
    words = []
    stopwords = set(['the', 'and', 'for', 'that', 'with', 'from', 'this', 'news', 'says', 'how', 'why', 'what', 'will', 'over', 'into', 'after', 'about'])
    for text in text_list:
        clean = re.sub(r'[^\w\s]', '', text.lower())
        words.extend([w for w in clean.split() if w not in stopwords and len(w) > 3])
    return Counter(words).most_common(12)

@st.cache_data(ttl=300)
def scrape_news(url):
    """Scrapes headlines and links from common news structures."""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        found_data = []
        seen_headlines = set()
        
        for tag in soup.find_all(['h1', 'h2', 'h3', 'h4']):
            a_tag = tag.find('a')
            if a_tag and a_tag.get('href'):
                text = tag.get_text().strip()
                link = urljoin(url, a_tag.get('href')) # Resolve relative URLs
                
                if len(text.split()) > 4 and len(text) < 200 and text not in seen_headlines:
                    seen_headlines.add(text)
                    found_data.append({"Headline": text, "URL": link})
        
        return found_data
    except Exception as e:
        return f"Error: {str(e)}"

@st.cache_data(ttl=300)
def scrape_article_content(url):
    """Attempts to extract the main image and text from an article URL."""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Try to find OG Image
        img_tag = soup.find('meta', property='og:image')
        img_url = img_tag['content'] if img_tag else None
        
        # Try to extract paragraphs
        paragraphs = soup.find_all('p')
        content = "\n\n".join([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 50])
        
        if not content:
            content = "Could not extract full article text automatically due to website paywalls or javascript rendering."
            
        return img_url, content
    except Exception as e:
        return None, f"Could not load article content. Error: {str(e)}"

# --- NAVIGATION ---
st.markdown("<h1 style='text-align: center; color: #1E3A8A; margin-bottom: 0;'>NewsPulse AI 📡</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #64748b; font-size: 1.2em;'>Intelligence for the Modern Information Age</p>", unsafe_allow_html=True)

# Top navigation buttons
def nav_to(page):
    st.session_state.current_page = page

nav1, nav2, nav3 = st.columns(3)
with nav1:
    st.button("🏠 Home", use_container_width=True, on_click=nav_to, args=("🏠 Home",))
with nav2:
    st.button("📊 Dashboard", use_container_width=True, on_click=nav_to, args=("📊 Dashboard",))
with nav3:
    st.button("ℹ️ About", use_container_width=True, on_click=nav_to, args=("ℹ️ About",))

st.divider()

# --- PAGE: HOME ---
if st.session_state.current_page == "🏠 Home":
    st.session_state.selected_article = None # Reset article view
    
    col1, col2 = st.columns([1.6, 1])
    
    with col1:
        st.header("🚀 Project Overview")
        st.write("""
        **NewsPulse AI** is an advanced NLP (Natural Language Processing) and web-scraping engine designed to decode the emotional undertone and bias of current events across the globe in real-time.
        """)
        
        st.subheader("⚠️ Problem Statement")
        st.write("""
        In the modern digital age, we suffer from **Information Overload**. Thousands of news articles are published every minute, often loaded with clickbait, emotional manipulation, and inherent biases. It has become nearly impossible for an individual or investor to manually gauge the true, objective "mood" of the market or public opinion without being influenced by sensationalism.
        """)
        
        st.subheader("💡 The Solution")
        st.write("""
        NewsPulse AI solves this by deploying automated scrapers that instantly aggregate headlines from any given news portal. It passes these headlines through a linguistic model to strip away the noise and quantify two critical metrics:
        1. **Polarity (Sentiment):** Is the news driving fear or optimism?
        2. **Subjectivity (Bias):** Is the news reporting hard facts, or pushing an opinion?
        """)
        
        st.subheader("⚙️ Technologies Used")
        st.markdown("""
        * **Python:** Core backend programming language.
        * **Streamlit:** For building the interactive, reactive web application interface.
        * **BeautifulSoup4 & Requests:** For DOM parsing, HTML extraction, and web scraping.
        * **TextBlob & NLTK:** For Natural Language Processing and sentiment classification.
        * **Plotly:** For rendering advanced, interactive SVG-based charts.
        * **Pandas:** For structuring, cleaning, and managing the scraped datasets.
        """)
        
        st.subheader("🎯 Why is this Unique?")
        st.write("""
        Unlike static sentiment reports, NewsPulse AI allows users to input **Custom URLs** and get an on-the-fly analysis. It dynamically adjusts to any news site structure, generates instant interactive data visualizations, and acts as a transparent, bias-detection shield for the reader.
        """)
        
        st.subheader("📖 How to Use")
        st.info("""
        1. Navigate to the **📊 Dashboard** from the sidebar.
        2. Select a pre-configured news category or enter a Custom URL.
        3. Click **Analyze Now**.
        4. Explore the charts, or click on any headline to open the **Article Reader** and view the full content.
        """)

    with col2:
        # --- DEVELOPER PROFILE ---
        st.markdown("""
            <div class="dev-card">
                <h2>👨‍💻 Developer Profile</h2>
                <h3 style='color: white; margin-bottom: 5px;'>Ravi Kumar Vishwakarma</h3>
                <p style='color: #94a3b8; font-size: 1.1em; margin-top: 0;'>Full-Stack NLP Engineer</p>
                <p>Passionate about turning unstructured web data into visual stories and building AI tools that empower users.</p>
                <hr style='border-color: rgba(255,255,255,0.2); margin: 20px 0;'>
                <p style='margin-bottom: 10px;'><strong>Connect with me:</strong></p>
            </div>
        """, unsafe_allow_html=True)
        
        # Buttons outside HTML for Streamlit click handling
        st.link_button("📂 View My GitHub", "https://github.com/", use_container_width=True)
        st.link_button("💼 Connect on LinkedIn", "https://linkedin.com/", use_container_width=True)
        st.link_button("🌐 Visit Portfolio Website", "https://yourportfolio.com/", use_container_width=True)

# --- PAGE: DASHBOARD ---
elif st.session_state.current_page == "📊 Dashboard":
    
    # If an article is selected, show the Article Reader view
    if st.session_state.selected_article:
        st.button("← Back to Dashboard", on_click=lambda: st.session_state.update({'selected_article': None}))
        st.divider()
        
        article_url = st.session_state.selected_article['URL']
        headline = st.session_state.selected_article['Headline']
        sentiment = st.session_state.selected_article['Sentiment']
        
        st.markdown(f"<h2>{headline}</h2>", unsafe_allow_html=True)
        st.markdown(f"**Source URL:** [{article_url}]({article_url}) | **Sentiment:** {sentiment}")
        
        with st.spinner("Extracting article content..."):
            img_url, content = scrape_article_content(article_url)
            
            if img_url:
                st.image(img_url, use_container_width=True)
            
            st.markdown(f"<div class='article-text'>{content}</div>", unsafe_allow_html=True)
            
        st.divider()
        st.link_button("Open Original Article in New Tab ↗", article_url)

    # Otherwise, show the main dashboard
    else:
        st.subheader("Data Extraction & Analysis Engine")
        
        col_url, col_btn = st.columns([3, 1])
        with col_url:
            target_topic = st.selectbox(
                "Select a News Source or choose 'Custom URL':",
                ["https://techcrunch.com/category/artificial-intelligence/", 
                 "https://www.theverge.com/tech",
                 "https://www.bbc.com/news/business",
                 "Custom URL"]
            )
            
            url_to_use = target_topic
            if target_topic == "Custom URL":
                url_to_use = st.text_input("Enter Custom News URL:", placeholder="e.g., https://news.ycombinator.com/")
        
        with col_btn:
            st.markdown("<br>", unsafe_allow_html=True)
            analyze_clicked = st.button("🚀 Analyze Now")

        if analyze_clicked:
            with st.spinner("Initializing web scrapers & NLP models..."):
                raw_data = scrape_news(url_to_use)
                
                if isinstance(raw_data, str) and raw_data.startswith("Error"):
                    st.error(f"Scraping Failed: {raw_data}")
                elif not raw_data:
                    st.warning("No headlines found. This website might have heavy Javascript rendering or anti-scraping protections.")
                else:
                    processed_data = []
                    for item in raw_data:
                        label, emoji, pol, subj = get_sentiment(item["Headline"])
                        processed_data.append({
                            "Headline": item["Headline"],
                            "URL": item["URL"],
                            "Sentiment": label,
                            "Emoji": emoji,
                            "Polarity": pol,
                            "Subjectivity": subj
                        })
                    
                    st.session_state.scraped_data = pd.DataFrame(processed_data)

        # Display Dashboard if data exists
        if st.session_state.scraped_data is not None:
            df = st.session_state.scraped_data
            
            st.markdown("### 📈 Real-Time Intelligence")
            
            # --- METRICS ROW ---
            m1, m2, m3, m4 = st.columns(4)
            avg_pol = df['Polarity'].mean()
            pos_rate = (len(df[df['Sentiment']=='Positive'])/len(df)*100) if len(df) > 0 else 0
            
            with m1: st.markdown(f"<div class='metric-card'><h3>{len(df)}</h3><p>Headlines Scraped</p></div>", unsafe_allow_html=True)
            with m2: st.markdown(f"<div class='metric-card'><h3>{avg_pol:.2f}</h3><p>Net Mood Score</p></div>", unsafe_allow_html=True)
            with m3: st.markdown(f"<div class='metric-card'><h3>{pos_rate:.1f}%</h3><p>Positivity Rate</p></div>", unsafe_allow_html=True)
            with m4: st.markdown(f"<div class='metric-card'><h3>{df['Subjectivity'].mean():.2f}</h3><p>Avg Bias/Subjectivity</p></div>", unsafe_allow_html=True)
            
            st.markdown("<br>", unsafe_allow_html=True)

            # --- VISUALIZATION ROW 1 ---
            v1, v2 = st.columns(2)
            with v1:
                fig_pie = px.pie(df, names='Sentiment', title='Sentiment Distribution',
                                 color='Sentiment', hole=0.4,
                                 color_discrete_map={'Positive':'#10b981', 'Neutral':'#94a3b8', 'Negative':'#ef4444'})
                fig_pie.update_layout(margin=dict(t=40, b=0, l=0, r=0))
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with v2:
                fig_gauge = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = avg_pol,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "Overall Market Mood (-1 to 1)"},
                    gauge = {
                        'axis': {'range': [-1, 1]},
                        'bar': {'color': "#1e3a8a"},
                        'steps': [
                            {'range': [-1, -0.1], 'color': "#fca5a5"},
                            {'range': [-0.1, 0.1], 'color': "#f1f5f9"},
                            {'range': [0.1, 1], 'color': "#6ee7b7"}]
                    }))
                fig_gauge.update_layout(margin=dict(t=40, b=0, l=0, r=0))
                st.plotly_chart(fig_gauge, use_container_width=True)

            # --- VISUALIZATION ROW 2 ---
            v3, v4 = st.columns(2)
            with v3:
                fig_scatter = px.scatter(df, x='Polarity', y='Subjectivity', color='Sentiment',
                                         hover_data=['Headline'], title='Bias vs. Sentiment Analysis',
                                         color_discrete_map={'Positive':'#10b981', 'Neutral':'#94a3b8', 'Negative':'#ef4444'})
                st.plotly_chart(fig_scatter, use_container_width=True)

            with v4:
                keywords = extract_keywords(df['Headline'].tolist())
                k_df = pd.DataFrame(keywords, columns=['Word', 'Count'])
                fig_key = px.bar(k_df, x='Count', y='Word', orientation='h', title='Trending Keywords',
                                 color_discrete_sequence=['#3b82f6'])
                fig_key.update_layout(yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_key, use_container_width=True)

            # --- INTERACTIVE NEWS FEED ---
            st.markdown("### 📰 Interactive News Feed")
            st.write("Click on any article to analyze its content or view the source.")
            
            for idx, row in df.iterrows():
                with st.expander(f"{row['Emoji']} {row['Headline']}"):
                    st.write(f"**Sentiment Analysis:** Score {row['Polarity']} | **Subjectivity/Bias:** {row['Subjectivity']}")
                    
                    c1, c2 = st.columns([1, 4])
                    with c1:
                        if st.button("📖 Read Article", key=f"read_{idx}"):
                            st.session_state.selected_article = row.to_dict()
                            st.rerun()

# --- PAGE: ABOUT ---
elif st.session_state.current_page == "ℹ️ About":
    st.session_state.selected_article = None # Reset article view
    
    st.header("Project Documentation & Architecture")
    
    st.write("""
    ### 🧠 How It Works
    NewsPulse AI is built to replicate the workflow of a data journalist. It performs three critical operations in a matter of seconds:
    
    1. **Data Acquisition (Scraping):** When a user inputs a URL, the app sends a secure HTTP request pretending to be a web browser. It uses `BeautifulSoup` to parse the website's HTML Document Object Model (DOM), hunting specifically for Headline tags (`<h1>` to `<h4>`) and their associated hyperlinks (`<a>`).
    
    2. **Natural Language Processing (NLP):**
       The extracted text is passed through `TextBlob`, an NLP library built on top of the famous NLTK framework. The model evaluates the lexicon (words) within the headline against a vast dataset of pre-scored words to calculate:
       * **Polarity [-1.0 to 1.0]:** Evaluates the emotional direction. Words like "crash", "loss", and "terrible" drag the score down, while "innovative", "surge", and "win" push it up.
       * **Subjectivity [0.0 to 1.0]:** Evaluates the amount of personal opinion or factual information. High subjectivity means the headline is highly opinionated.
       
    3. **Data Visualization:**
       The numerical data is mapped into a Pandas DataFrame, which acts as the data foundation for `Plotly`. Plotly renders interactive, mathematically precise graphs that allow the user to visualize the overarching themes of the news portal at a glance.
       
    ### 🚧 Current Limitations & Future Scope
    * **Dynamic Content Loading:** Many modern websites (like Twitter/X, Bloomberg, or heavily React-based apps) use Client-Side Rendering (CSR). Standard `Requests` cannot read this content because it requires a Javascript engine to run first. 
    * **Paywalls:** The Article Reader feature relies on standard HTML paragraphs. If a site has a hard paywall, only the introductory text will be extracted.
    * **Future Upgrades:** Future versions of this tool will implement Selenium for rendering JS, and utilize Large Language Models (LLMs) like OpenAI's GPT for deeper contextual summary rather than simple lexicon-based sentiment analysis.
    """)
    
    st.divider()
    st.caption(f"NewsPulse AI Engine v2.5 | System Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Developed by Ravi Kumar Vishwakarma")

# --- FOOTER ---
st.markdown("<br><hr><p style='text-align: center; color: #94a3b8; font-size: 0.9em;'>Built for Insight • Driven by Data • Empowered by AI</p>", unsafe_allow_html=True)
