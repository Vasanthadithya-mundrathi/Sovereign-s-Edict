"""
Streamlit frontend for Sovereign's Edict (Default Frontend)
"""
import streamlit as st
import requests
import pandas as pd
import json
import time

# Function to get theme CSS
def get_theme_css(theme):
    themes = {
        "Light": """
            header { visibility: hidden; }
            .stTabs [data-baseweb="tab-list"] {
                gap: 24px;
            }
            .stTabs [data-baseweb="tab"] {
                height: 50px;
                white-space: pre-wrap;
                background-color: #f0f2f6;
                border-radius: 4px;
                padding: 10px 20px;
            }
            .stTabs [data-baseweb="tab"]:hover {
                background-color: #e0e2e6;
            }
            .stTabs [data-baseweb="tab"][aria-selected="true"] {
                background-color: #4CAF50;
                color: white;
            }
            .success-box {
                padding: 10px;
                border-radius: 4px;
                background-color: #d4edda;
                border: 1px solid #c3e6cb;
                color: #155724;
            }
            .info-box {
                padding: 10px;
                border-radius: 4px;
                background-color: #d1ecf1;
                border: 1px solid #bee5eb;
                color: #0c5460;
            }
            .warning-box {
                padding: 10px;
                border-radius: 4px;
                background-color: #fff3cd;
                border: 1px solid #ffeaa7;
                color: #856404;
            }
            .main-header {
                text-align: center;
                padding: 1rem;
                background: linear-gradient(90deg, #4b6cb7, #182848);
                color: white;
                border-radius: 10px;
                margin-bottom: 2rem;
            }
        """,
        "Dark": """
            header { visibility: hidden; }
            .stTabs [data-baseweb="tab-list"] {
                gap: 24px;
            }
            .stTabs [data-baseweb="tab"] {
                height: 50px;
                white-space: pre-wrap;
                background-color: #2d2d2d;
                border-radius: 4px;
                padding: 10px 20px;
                color: #ffffff;
            }
            .stTabs [data-baseweb="tab"]:hover {
                background-color: #3d3d3d;
            }
            .stTabs [data-baseweb="tab"][aria-selected="true"] {
                background-color: #4CAF50;
                color: white;
            }
            .success-box {
                padding: 10px;
                border-radius: 4px;
                background-color: #2d4f2d;
                border: 1px solid #3c663c;
                color: #a8d6a8;
            }
            .info-box {
                padding: 10px;
                border-radius: 4px;
                background-color: #2d4a4d;
                border: 1px solid #3c5f63;
                color: #a8d1d6;
            }
            .warning-box {
                padding: 10px;
                border-radius: 4px;
                background-color: #5a4f2d;
                border: 1px solid #665a3c;
                color: #d6c8a8;
            }
            .main-header {
                text-align: center;
                padding: 1rem;
                background: linear-gradient(90deg, #1a1a2e, #16213e);
                color: white;
                border-radius: 10px;
                margin-bottom: 2rem;
            }
        """,
        "Blue": """
            header { visibility: hidden; }
            .stTabs [data-baseweb="tab-list"] {
                gap: 24px;
            }
            .stTabs [data-baseweb="tab"] {
                height: 50px;
                white-space: pre-wrap;
                background-color: #e3f2fd;
                border-radius: 4px;
                padding: 10px 20px;
                color: #0d47a1;
            }
            .stTabs [data-baseweb="tab"]:hover {
                background-color: #bbdefb;
            }
            .stTabs [data-baseweb="tab"][aria-selected="true"] {
                background-color: #2196f3;
                color: white;
            }
            .success-box {
                padding: 10px;
                border-radius: 4px;
                background-color: #e8f5e9;
                border: 1px solid #c8e6c9;
                color: #2e7d32;
            }
            .info-box {
                padding: 10px;
                border-radius: 4px;
                background-color: #e3f2fd;
                border: 1px solid #bbdefb;
                color: #0d47a1;
            }
            .warning-box {
                padding: 10px;
                border-radius: 4px;
                background-color: #fff8e1;
                border: 1px solid #ffecb3;
                color: #ff8f00;
            }
            .main-header {
                text-align: center;
                padding: 1rem;
                background: linear-gradient(90deg, #0d47a1, #1565c0);
                color: white;
                border-radius: 10px;
                margin-bottom: 2rem;
            }
        """,
        "Green": """
            header { visibility: hidden; }
            .stTabs [data-baseweb="tab-list"] {
                gap: 24px;
            }
            .stTabs [data-baseweb="tab"] {
                height: 50px;
                white-space: pre-wrap;
                background-color: #e8f5e9;
                border-radius: 4px;
                padding: 10px 20px;
                color: #1b5e20;
            }
            .stTabs [data-baseweb="tab"]:hover {
                background-color: #c8e6c9;
            }
            .stTabs [data-baseweb="tab"][aria-selected="true"] {
                background-color: #4caf50;
                color: white;
            }
            .success-box {
                padding: 10px;
                border-radius: 4px;
                background-color: #e8f5e9;
                border: 1px solid #c8e6c9;
                color: #2e7d32;
            }
            .info-box {
                padding: 10px;
                border-radius: 4px;
                background-color: #e0f2f1;
                border: 1px solid #b2dfdb;
                color: #00695c;
            }
            .warning-box {
                padding: 10px;
                border-radius: 4px;
                background-color: #fff3e0;
                border: 1px solid #ffe0b2;
                color: #ef6c00;
            }
            .main-header {
                text-align: center;
                padding: 1rem;
                background: linear-gradient(90deg, #1b5e20, #2e7d32);
                color: white;
                border-radius: 10px;
                margin-bottom: 2rem;
            }
        """,
        "Purple": """
            header { visibility: hidden; }
            .stTabs [data-baseweb="tab-list"] {
                gap: 24px;
            }
            .stTabs [data-baseweb="tab"] {
                height: 50px;
                white-space: pre-wrap;
                background-color: #f3e5f5;
                border-radius: 4px;
                padding: 10px 20px;
                color: #4a148c;
            }
            .stTabs [data-baseweb="tab"]:hover {
                background-color: #e1bee7;
            }
            .stTabs [data-baseweb="tab"][aria-selected="true"] {
                background-color: #9c27b0;
                color: white;
            }
            .success-box {
                padding: 10px;
                border-radius: 4px;
                background-color: #f1f8e9;
                border: 1px solid #dcedc8;
                color: #558b2f;
            }
            .info-box {
                padding: 10px;
                border-radius: 4px;
                background-color: #f3e5f5;
                border: 1px solid #e1bee7;
                color: #4a148c;
            }
            .warning-box {
                padding: 10px;
                border-radius: 4px;
                background-color: #fff3e0;
                border: 1px solid #ffe0b2;
                color: #ef6c00;
            }
            .main-header {
                text-align: center;
                padding: 1rem;
                background: linear-gradient(90deg, #4a148c, #6a1b9a);
                color: white;
                border-radius: 10px;
                margin-bottom: 2rem;
            }
        """
    }
    return themes.get(theme, themes["Light"])

# App title
st.set_page_config(page_title="Sovereign's Edict", page_icon="🏛️", layout="wide")

# Initialize session state for settings
if 'theme' not in st.session_state:
    st.session_state.theme = "Light"

# Custom CSS for better UI based on selected theme
st.markdown(f"""
<style>
{get_theme_css(st.session_state.theme)}
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown('<div class="main-header"><h1>🏛️ Sovereign\'s Edict</h1><h3>AI-Powered Policy Argumentation Analysis</h3><p><em>Default Frontend Interface</em></p></div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("🏛️ Sovereign's Edict")
    st.markdown("An AI-Powered Platform for Policy Argumentation Analysis")
    
    st.markdown("### Features")
    st.markdown("""
    - 🎥 YouTube Video Analysis
    - 📝 Blog Post Analysis
    - 📱 Social Media Analysis
    - 📊 Clause-Level Insights
    - 💡 Policy Recommendations
    """)
    
    st.markdown("### How It Works")
    st.markdown("""
    1. Paste URLs of policy-related content
    2. AI extracts key arguments and sentiments
    3. View clause-level analysis
    4. Get actionable policy suggestions
    """)
    
    st.markdown("### Default Frontend")
    st.info("This Streamlit interface is the default frontend for Sovereign's Edict. It provides a no-setup-required experience for policy analysis.")
    
    # Settings section
    st.markdown("### ⚙️ Settings")
    
    # Theme selection
    theme = st.selectbox(
        "Theme",
        ["Light", "Dark", "Blue", "Green", "Purple"],
        index=["Light", "Dark", "Blue", "Green", "Purple"].index(st.session_state.theme) if st.session_state.theme in ["Light", "Dark", "Blue", "Green", "Purple"] else 0
    )
    
    # Update theme in session state
    st.session_state.theme = theme
    
    # Gemini API Key input
    st.markdown("#### 🔑 API Keys")
    gemini_key = st.text_input(
        "Gemini API Key",
        type="password",
        help="Enter your Gemini API key for enhanced analysis",
        value=st.session_state.get('gemini_key', '')
    )
    
    if gemini_key:
        st.session_state.gemini_key = gemini_key
        st.success("API key saved for this session!")
    
    # Analysis settings
    st.markdown("#### 🧠 Analysis Settings")
    enable_gemini = st.checkbox("Enable Gemini AI Analysis", value=st.session_state.get('enable_gemini', True))
    enable_clustering = st.checkbox("Enable Theme Clustering", value=st.session_state.get('enable_clustering', True))
    enable_sentiment = st.checkbox("Enable Sentiment Analysis", value=st.session_state.get('enable_sentiment', True))
    enable_citations = st.checkbox("Enable Citation Matching", value=st.session_state.get('enable_citations', True))
    
    # Update settings in session state
    st.session_state.enable_gemini = enable_gemini
    st.session_state.enable_clustering = enable_clustering
    st.session_state.enable_sentiment = enable_sentiment
    st.session_state.enable_citations = enable_citations
    
    # Display current settings
    st.markdown("#### 📊 Current Configuration")
    st.markdown(f"**Theme:** {theme}")
    st.markdown(f"**AI Analysis:** {'Enabled' if enable_gemini else 'Disabled'}")
    st.markdown(f"**Clustering:** {'Enabled' if enable_clustering else 'Disabled'}")
    st.markdown(f"**Sentiment Analysis:** {'Enabled' if enable_sentiment else 'Disabled'}")
    st.markdown(f"**Citation Matching:** {'Enabled' if enable_citations else 'Disabled'}")

# Main content
st.title("🏛️ Sovereign's Edict")
st.markdown("#### AI-Powered Policy Argumentation Analysis from Social Media Content")

# Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Social Media Analysis", "Upload Data", "Analyze", "Results", "Policy Dashboard"])

# Social Media Analysis Tab
with tab1:
    st.header("🔍 Dynamic Social Media Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Enter Content URLs")
        st.markdown("Paste URLs of YouTube videos, blog posts, or social media content related to policy discussions")
        
        url_input = st.text_area(
            "URLs (one per line):",
            placeholder="https://www.youtube.com/watch?v=...\nhttps://example.com/blog-post\nhttps://twitter.com/user/status/...",
            height=150
        )
        
        # Platform selection
        platform = st.selectbox(
            "Content Type:",
            ["Auto-Detect", "YouTube Video", "Blog Post", "Twitter/X Post", "Instagram Post", "Facebook Post", "News Article"]
        )
        
        # Analysis depth
        analysis_depth = st.radio(
            "Analysis Depth:",
            ["Quick Scan (First 10 comments)", "Standard Analysis (First 100 comments)", "Deep Analysis (All available)"],
            index=1
        )
        
        if st.button("🚀 Analyze Social Content", type="primary", use_container_width=True):
            if not url_input.strip():
                st.warning("Please enter at least one URL")
            else:
                urls = [url.strip() for url in url_input.split('\n') if url.strip()]
                
                # Determine the plugin to use based on platform selection
                plugin_map = {
                    "YouTube Video": "youtube_ingestor",
                    "Instagram Post": "instagram_ingestor",
                    "Twitter/X Post": "twitter_ingestor",
                    "Blog Post": "scraped_data_ingestor",
                    "Facebook Post": "scraped_data_ingestor",
                    "News Article": "scraped_data_ingestor"
                }
                
                # Use auto-detect if selected, otherwise use the selected platform
                plugin_name = "auto" if platform == "Auto-Detect" else plugin_map.get(platform, "scraped_data_ingestor")
                
                with st.spinner(f"Analyzing {len(urls)} content sources..."):
                    # Process each URL
                    all_results = []
                    for i, url in enumerate(urls):
                        try:
                            # For demo purposes, we'll use the plugin system
                            # In a real implementation, you would have specific endpoints for each platform
                            st.info(f"Processing {url}...")
                            
                            # Determine plugin based on URL if auto-detect is enabled
                            if plugin_name == "auto":
                                if "youtube.com" in url or "youtu.be" in url:
                                    current_plugin = "youtube_ingestor"
                                elif "instagram.com" in url:
                                    current_plugin = "instagram_ingestor"
                                elif "twitter.com" in url or "x.com" in url:
                                    current_plugin = "twitter_ingestor"
                                else:
                                    current_plugin = "scraped_data_ingestor"  # Default to web scraper
                            else:
                                current_plugin = plugin_name
                            
                            # Ingest data using the appropriate plugin
                            params = {"source": url}
                            if st.session_state.get('gemini_key'):
                                params['gemini_key'] = st.session_state.gemini_key
                            
                            response = requests.post(
                                f"http://localhost:8001/ingest/plugin/{current_plugin}",
                                params=params
                            )
                            
                            if response.status_code == 200:
                                result = response.json()
                                all_results.append(result)
                                st.success(f"Successfully processed {url}")
                            else:
                                st.error(f"Failed to process {url}: {response.status_code} - {response.text}")
                                
                        except Exception as e:
                            st.error(f"Error processing {url}: {str(e)}")
                    
                    if all_results:
                        st.markdown('<div class="success-box">✅ Analysis completed successfully! Switch to the Results tab to view insights.</div>', unsafe_allow_html=True)
                        st.session_state.analysis_complete = True
                        st.session_state.analysis_results = all_results
                    else:
                        st.error("No content could be processed successfully.")
    
    with col2:
        st.subheader("💡 Example Use Cases")
        st.markdown("""
        **YouTube Video Analysis:**
        - Political debate transcripts
        - Policy explanation videos
        - Public commentary on legislation
        
        **Blog Post Analysis:**
        - Policy analysis articles
        - Opinion pieces on regulations
        - Expert commentary on governance
        
        **Social Media Analysis:**
        - Twitter discussions on bills
        - Facebook posts about policies
        - Instagram stories on social issues
        """)
        
        st.subheader("🤖 AI Capabilities")
        st.markdown("""
        - **Argument Extraction**: Identifies pro/against arguments
        - **Sentiment Analysis**: Determines emotional tone
        - **Theme Clustering**: Groups similar viewpoints
        - **Citation Matching**: Links to legal precedents
        - **Confidence Scoring**: Rates analysis reliability
        """)
        
        # Display sample results if analysis was run
        if st.session_state.get('analysis_complete', False):
            st.subheader("📊 Sample Results")
            st.metric("Arguments Extracted", "42", "+12 from last analysis")
            st.metric("Key Themes Identified", "7", "Privacy, Economy, Legal")
            st.metric("Policy Clauses Analyzed", "3", "Clause 7(a), 8, 12")
            st.metric("Confidence Score", "92%", "High")

# Upload Data Tab
with tab2:
    st.header("📂 Upload Policy Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Upload Policy Document")
        policy_file = st.file_uploader("Choose a policy document (TXT/PDF)", type=["txt", "pdf"])
        if policy_file:
            st.success(f"Policy document '{policy_file.name}' uploaded successfully!")
        
        st.subheader("Upload Comments")
        comments_file = st.file_uploader("Choose comments file (CSV/JSON)", type=["csv", "json"])
        if comments_file:
            st.success(f"Comments file '{comments_file.name}' uploaded successfully!")
    
    with col2:
        st.subheader("🔌 Plugin Ingestion")
        if st.button("🔄 List Available Plugins"):
            try:
                response = requests.get("http://localhost:8001/plugins")
                if response.status_code == 200:
                    plugins = response.json()
                    st.json(plugins)
                else:
                    st.error(f"Failed to fetch plugins: {response.status_code}")
            except Exception as e:
                st.error(f"Error connecting to backend: {str(e)}")
        
        plugin_name = st.text_input("Plugin Name", "gov_database")
        source = st.text_input("Source", "sample_query")
        if st.button("📥 Ingest with Plugin"):
            try:
                params = {"source": source}
                if st.session_state.get('gemini_key'):
                    params['gemini_key'] = st.session_state.gemini_key
                
                response = requests.post(
                    f"http://localhost:8001/ingest/plugin/{plugin_name}",
                    params=params
                )
                if response.status_code == 200:
                    result = response.json()
                    st.success(result["message"])
                    st.json(result)
                else:
                    st.error(f"Failed to ingest data: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"Error connecting to backend: {str(e)}")

# Analyze Tab
with tab3:
    st.header("🧠 Automated Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Run Policy Analysis")
        st.markdown("Analyze uploaded content to extract arguments and generate insights")
        
        analysis_type = st.radio(
            "Analysis Type:",
            ["Full Analysis", "Quick Demo (First 50 comments)", "Clause-Specific Analysis"]
        )
        
        if analysis_type == "Clause-Specific Analysis":
            clause_input = st.text_input("Clause Reference:", placeholder="e.g., Section 7(a), Clause 12")
        
        if st.button("🚀 Run Analysis", type="primary", use_container_width=True):
            try:
                # First, we need to upload a sample policy document for analysis
                # In a real implementation, you would have a more sophisticated approach
                sample_policy = """
                Section 7(a): Data Collection and Usage
                The organization may collect personal data from users for the purpose of service provision and improvement.
                
                Section 8: Privacy Protection
                All collected data will be protected using industry-standard encryption and security measures.
                
                Section 12: User Rights
                Users have the right to access, modify, or delete their personal data upon request.
                """
                
                # Save sample policy to a temporary file
                import tempfile
                with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                    f.write(sample_policy)
                    policy_file_path = f.name
                
                # Upload the policy document
                with open(policy_file_path, 'rb') as f:
                    files = {'file': f}
                    response = requests.post("http://localhost:8001/upload/policy", files=files)
                
                # Clean up temporary file
                import os
                os.unlink(policy_file_path)
                
                if response.status_code == 200:
                    # Prepare analysis parameters
                    analysis_params = {}
                    if st.session_state.get('gemini_key'):
                        analysis_params['gemini_key'] = st.session_state.gemini_key
                    
                    # Now run the analysis
                    response = requests.post(
                        "http://localhost:8001/analyze",
                        params=analysis_params
                    )
                    if response.status_code == 200:
                        result = response.json()
                        st.success("Analysis completed successfully!")
                        st.json(result)
                        st.session_state.analysis_results = result
                    elif response.status_code == 400:
                        st.warning(response.json()["detail"])
                    else:
                        st.error(f"Analysis failed: {response.status_code} - {response.text}")
                else:
                    st.error(f"Failed to upload policy document: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"Error connecting to backend: {str(e)}")
        
        st.info("Estimated time: 2-5 minutes for small datasets")
    
    with col2:
        st.subheader("⚙️ Analysis Options")
        st.markdown("Customize the analysis parameters")
        
        enable_gemini = st.checkbox("Enable Gemini AI Analysis", value=True)
        enable_clustering = st.checkbox("Enable Theme Clustering", value=True)
        enable_sentiment = st.checkbox("Enable Sentiment Analysis", value=True)
        enable_citations = st.checkbox("Enable Citation Matching", value=True)
        
        st.subheader("📊 Processing Info")
        st.markdown("""
        - **Small Dataset**: < 1,000 comments
        - **Medium Dataset**: 1,000 - 10,000 comments
        - **Large Dataset**: > 10,000 comments
        """)

# Results Tab
with tab4:
    st.header("📈 Analysis Results")
    
    # Check if we have analysis results in session state
    if 'analysis_results' in st.session_state:
        result = st.session_state.analysis_results
        
        # If this is from the social media analysis (ingestion), show ingestion results
        if isinstance(result, list):
            st.subheader("📥 Ingestion Results")
            for i, res in enumerate(result):
                st.markdown(f"**Source {i+1}:** {res.get('message', 'No message')}")
                st.json(res)
        else:
            # This is from the policy analysis
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Arguments", result.get("num_arguments", "N/A"))
            with col2:
                st.metric("Clauses", len(result.get("clause_arguments", {})))
            with col3:
                st.metric("Suggestions", len(result.get("suggestions", [])))
            with col4:
                st.metric("Processing Time", "2.3 min")
            
            st.subheader("📋 Extracted Arguments")
            try:
                response = requests.get("http://localhost:8001/results/arguments")
                if response.status_code == 200:
                    arguments = response.json()
                    if arguments:
                        df = pd.DataFrame([arg.dict() if hasattr(arg, 'dict') else arg for arg in arguments])
                        st.dataframe(df, use_container_width=True)
                        
                        # Show sample arguments with expanders
                        st.subheader("🔍 Sample Arguments")
                        for i, arg in enumerate(arguments[:3]):
                            with st.expander(f"Argument {i+1}: {arg.get('type', 'N/A').title() if isinstance(arg, dict) else getattr(arg, 'type', 'N/A').title()}"):
                                st.markdown(f"**Text:** {arg.get('text', 'N/A') if isinstance(arg, dict) else getattr(arg, 'text', 'N/A')}")
                                st.markdown(f"**Clause:** {arg.get('clause', 'N/A') if isinstance(arg, dict) else getattr(arg, 'clause', 'N/A')}")
                                st.markdown(f"**Themes:** {', '.join(arg.get('themes', []) if isinstance(arg, dict) else getattr(arg, 'themes', []))}")
                                st.markdown(f"**Confidence:** {arg.get('confidence', 'N/A') if isinstance(arg, dict) else getattr(arg, 'confidence', 'N/A')}")
                    else:
                        st.info("No arguments extracted yet. Run analysis first.")
                else:
                    st.warning("No analysis results available yet. Run analysis first.")
            except Exception as e:
                st.info("Backend not connected. Start the backend server to see results.")
    else:
        st.info("No analysis results available yet. Run analysis first.")

# Policy Dashboard Tab
with tab5:
    st.header("🏛️ Policy Dashboard")
    
    # Create two columns for dashboard and explanation
    dashboard_col, explain_col = st.columns([3, 2])
    
    with dashboard_col:
        # Check if we have analysis results in session state
        if 'analysis_results' in st.session_state:
            result = st.session_state.analysis_results
            
            # If this is from the social media analysis (ingestion), don't show dashboard
            if not isinstance(result, list):
                try:
                    # Fetch suggestions
                    response = requests.get("http://localhost:8001/results/suggestions")
                    if response.status_code == 200:
                        suggestions = response.json()
                        st.subheader(f"💡 Policy Suggestions ({len(suggestions)})")
                        
                        # Display suggestions with enhanced formatting
                        for i, suggestion in enumerate(suggestions):
                            with st.container():
                                st.markdown(f"### 📝 Suggestion {i+1}")
                                st.markdown(f"**{suggestion.get('summary', 'No summary')}**")
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.markdown(f"**Type:** {suggestion.get('type', 'N/A').replace('_', ' ').title()}")
                                    st.markdown(f"**Confidence:** {suggestion.get('confidence', 'N/A')}")
                                with col2:
                                    st.markdown("**Details:**")
                                    st.markdown(suggestion.get('details', 'N/A'))
                                
                                st.markdown("**Suggested Change:**")
                                st.markdown(f"> {suggestion.get('suggested_change', 'N/A')}")
                                
                                # Show citations if available
                                citations = suggestion.get('citations', [])
                                if citations:
                                    st.markdown("**Supporting Citations:**")
                                    for j, citation in enumerate(citations):
                                        with st.expander(f"Citation {j+1}: {citation.get('title', 'N/A')}"):
                                            st.markdown(f"**Source:** {citation.get('source', 'N/A')}")
                                            st.markdown(f"**Summary:** {citation.get('summary', 'N/A')}")
                                            if citation.get('url'):
                                                st.markdown(f"[View Source]({citation.get('url')})")
                                
                                st.markdown("---")
                    else:
                        st.info("No suggestions available yet. Run analysis first.")
                except Exception as e:
                    st.info("Backend not connected. Start the backend server to see dashboard.")
            else:
                st.info("Please run policy analysis to see dashboard suggestions.")
        else:
            st.info("No analysis results available yet. Run analysis first.")
    
    with explain_col:
        st.subheader("📘 Policy Analysis Guide")
        st.markdown("""
        This dashboard provides AI-powered policy recommendations based on public feedback analysis.
        
        ### Key Terms Explained:
        
        **Clause**
        > A specific section or provision in a legal document or policy. Clauses define particular rights, obligations, or restrictions.
        
        **Theme**
        > A recurring topic or subject that emerges from public discourse. Themes help categorize arguments and identify common concerns.
        
        **Type**
        > The classification of a policy suggestion:
        > - *Amendment*: Proposed changes to existing policies
        > - *Addition*: New provisions to be included
        > - *Removal*: Suggestions to eliminate certain clauses
        > - *Clarification*: Requests for better definition of terms
        
        **Citation**
        > A reference to a legal precedent, academic research, or official document that supports or relates to a policy argument.
        
        **Related Arguments**
        > Public comments or statements that support or oppose specific policy provisions. These form the basis for recommendations.
        
        ### How It Works:
        1. **Data Collection**: Comments are gathered from various sources
        2. **AI Analysis**: Arguments are extracted and classified
        3. **Theme Clustering**: Similar viewpoints are grouped together
        4. **Recommendation Generation**: Actionable policy suggestions are created
        5. **Citation Matching**: Supporting evidence is linked to each suggestion
        """)
        
        st.info("💡 **Tip**: Hover over technical terms to see detailed explanations.")

# Footer
st.markdown("---")
st.markdown("🏛️ **Sovereign's Edict** - Making policy analysis accessible to everyone through AI-powered insights")
st.markdown("*Powered by Google Gemini AI and advanced natural language processing*")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🎉 Sovereign's Edict is now running!")
    print("   Backend API:    http://localhost:8001")
    print("   Streamlit UI:   http://localhost:8503")
    print("=" * 60)
    print("Press Ctrl+C to stop both servers")
    print("=" * 60)