# Phase 6: No-Setup Deployment Implementation

## Overview
Create Streamlit/Gradio frontends and Docker containerization for easy deployment with zero setup.

## Implementation Steps

### 1. Streamlit Frontend Implementation

#### Step 1: Create Streamlit Application

Create `streamlit_app.py` in the root directory:

```python
"""
Streamlit frontend for Sovereign's Edict
"""
import streamlit as st
import requests
import pandas as pd
import json
import time
from io import StringIO

# Configuration
API_BASE_URL = "http://localhost:8000"

# Page configuration
st.set_page_config(
    page_title="Sovereign's Edict",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6;
    }
    .sidebar .sidebar-content {
        background: #ffffff;
    }
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 10px 20px;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    .success-message {
        padding: 10px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 4px;
        color: #155724;
    }
    .error-message {
        padding: 10px;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 4px;
        color: #721c24;
    }
    .info-message {
        padding: 10px;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 4px;
        color: #0c5460;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data_uploaded' not in st.session_state:
    st.session_state.data_uploaded = False
if 'analysis_complete' not in st.session_state:
    st.session_state.analysis_complete = False
if 'dashboard_data' not in st.session_state:
    st.session_state.dashboard_data = None

def main():
    st.title("🏛️ Sovereign's Edict")
    st.markdown("An Actionable Intelligence Platform for Clause-Level Policy Argumentation")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", [
        "🏠 Home",
        "📤 Upload Data",
        "🔍 Analyze",
        "📊 Dashboard",
        "📖 Glossary",
        "ℹ️ Help"
    ])
    
    if page == "🏠 Home":
        show_home()
    elif page == "📤 Upload Data":
        show_upload()
    elif page == "🔍 Analyze":
        show_analyze()
    elif page == "📊 Dashboard":
        show_dashboard()
    elif page == "📖 Glossary":
        show_glossary()
    elif page == "ℹ️ Help":
        show_help()

def show_home():
    st.header("Welcome to Sovereign's Edict")
    st.markdown("""
    Sovereign's Edict is a ground-truthed, scalable, and ethically robust public consultation 
    intelligence engine. Moving beyond shallow sentiment analysis, it delivers real-time, 
    clause-level "argument maps" and suggested policy maneuvers—giving policymakers a true 
    X-ray of public feedback, with every insight backed by verifiable sources.
    
    ## Key Features
    - **Clause-Level Battlefield Map**: Visually shows where the sharpest opposition or support clusters
    - **Argument Cluster Reports**: Aggregates key positive/negative arguments by theme
    - **Sample Comments & Citation Trails**: Provides actual sample arguments and exact sources
    - **Counter-Offensive Generator**: Suggests precise, data-backed amendments
    """)
    
    st.subheader("Getting Started")
    st.markdown("""
    1. Go to the **Upload Data** page to add policy documents and public comments
    2. Navigate to **Analyze** to process your data
    3. View results in the **Dashboard**
    """)

def show_upload():
    st.header("📤 Upload Data")
    
    # Policy document upload
    st.subheader("Policy Document")
    policy_file = st.file_uploader("Upload policy document (TXT)", type=["txt"])
    
    if policy_file is not None:
        try:
            # Read file content
            content = policy_file.getvalue().decode("utf-8")
            
            # Upload to backend
            files = {"file": (policy_file.name, policy_file, "text/plain")}
            response = requests.post(f"{API_BASE_URL}/upload/policy", files=files)
            
            if response.status_code == 200:
                st.success("Policy document uploaded successfully!")
                st.session_state.data_uploaded = True
                with st.expander("View Policy Content"):
                    st.text_area("Policy Content", content, height=200)
            else:
                st.error(f"Failed to upload policy: {response.text}")
        except Exception as e:
            st.error(f"Error uploading policy: {str(e)}")
    
    # Comments upload
    st.subheader("Public Comments")
    comment_option = st.radio("Upload comments via:", ["File Upload", "Text Input"])
    
    if comment_option == "File Upload":
        comment_file = st.file_uploader("Upload comments (CSV/JSON)", type=["csv", "json"])
        
        if comment_file is not None:
            try:
                if comment_file.name.endswith(".csv"):
                    # Upload CSV
                    files = {"file": (comment_file.name, comment_file, "text/csv")}
                    response = requests.post(f"{API_BASE_URL}/upload/comments/csv", files=files)
                else:
                    # Upload JSON
                    files = {"file": (comment_file.name, comment_file, "application/json")}
                    response = requests.post(f"{API_BASE_URL}/upload/comments/json", files=files)
                
                if response.status_code == 200:
                    st.success("Comments uploaded successfully!")
                    st.session_state.data_uploaded = True
                else:
                    st.error(f"Failed to upload comments: {response.text}")
            except Exception as e:
                st.error(f"Error uploading comments: {str(e)}")
    
    else:  # Text Input
        comment_text = st.text_area("Enter comments (one per line)", height=150)
        if st.button("Add Comments") and comment_text:
            try:
                # Create temporary CSV
                comments_list = [line.strip() for line in comment_text.split("\n") if line.strip()]
                df = pd.DataFrame({"text": comments_list})
                csv_buffer = StringIO()
                df.to_csv(csv_buffer, index=False)
                csv_buffer.seek(0)
                
                # Upload to backend
                files = {"file": ("comments.csv", csv_buffer.getvalue(), "text/csv")}
                response = requests.post(f"{API_BASE_URL}/upload/comments/csv", files=files)
                
                if response.status_code == 200:
                    st.success("Comments added successfully!")
                    st.session_state.data_uploaded = True
                else:
                    st.error(f"Failed to add comments: {response.text}")
            except Exception as e:
                st.error(f"Error adding comments: {str(e)}")

def show_analyze():
    st.header("🔍 Analyze Data")
    
    if not st.session_state.data_uploaded:
        st.warning("Please upload data first in the Upload Data section.")
        return
    
    # Analysis options
    st.subheader("Analysis Options")
    quick_mode = st.checkbox("Quick Demo Mode (First 50 comments)", value=True)
    st.markdown("*Quick mode is recommended for faster results during testing*")
    
    if st.button("🚀 Run Analysis"):
        try:
            with st.spinner("Analyzing data... This may take a few minutes."):
                if quick_mode:
                    response = requests.post(f"{API_BASE_URL}/analyze/quick?limit=50")
                else:
                    response = requests.post(f"{API_BASE_URL}/analyze")
                
                if response.status_code == 200:
                    result = response.json()
                    st.success("Analysis completed successfully!")
                    st.session_state.analysis_complete = True
                    
                    # Display summary
                    st.subheader("Analysis Summary")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Arguments Extracted", result.get("num_arguments", 0))
                    with col2:
                        st.metric("Clauses Analyzed", len(result.get("clause_arguments", {})))
                    with col3:
                        st.metric("Suggestions Generated", len(result.get("suggestions", [])))
                    
                    # Store dashboard data
                    dashboard_response = requests.get(f"{API_BASE_URL}/results/dashboard")
                    if dashboard_response.status_code == 200:
                        st.session_state.dashboard_data = dashboard_response.json()
                else:
                    st.error(f"Analysis failed: {response.text}")
        except Exception as e:
            st.error(f"Error during analysis: {str(e)}")

def show_dashboard():
    st.header("📊 Policy Dashboard")
    
    if not st.session_state.analysis_complete:
        st.warning("Please run analysis first in the Analyze section.")
        return
    
    if st.session_state.dashboard_data is None:
        st.warning("No dashboard data available.")
        return
    
    dashboard_data = st.session_state.dashboard_data
    
    # Policy overview
    if dashboard_data.get("policy"):
        st.subheader(dashboard_data["policy"]["title"])
        with st.expander("View Policy Content"):
            st.text_area("Policy Content", dashboard_data["policy"]["content"], height=200)
    
    # Summary metrics
    st.subheader("Analysis Summary")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Arguments", dashboard_data.get("total_arguments", 0))
    with col2:
        st.metric("Clauses Analyzed", len(dashboard_data.get("clause_analysis", {})))
    with col3:
        st.metric("Suggestions", len(dashboard_data.get("suggestions", [])))
    with col4:
        st.metric("Processing Time", f"{dashboard_data.get('processing_time', 0):.2f}s")
    
    # Clause analysis
    if dashboard_data.get("clause_analysis"):
        st.subheader("Clause-Level Analysis")
        
        # Create DataFrame for visualization
        clause_data = []
        for clause_id, analysis in dashboard_data["clause_analysis"].items():
            clause_data.append({
                "Clause": clause_id,
                "Support": analysis.get("support_count", 0),
                "Objection": analysis.get("objection_count", 0),
                "Total": analysis.get("total_arguments", 0),
                "Controversy": f"{analysis.get('controversy_score', 0)*100:.1f}%",
                "Heat": analysis.get("heat_score", 0)
            })
        
        df = pd.DataFrame(clause_data)
        st.dataframe(df, use_container_width=True)
        
        # Visualizations
        st.subheader("Visualizations")
        chart_type = st.selectbox("Chart Type", ["Bar Chart", "Heatmap"])
        
        if chart_type == "Bar Chart":
            import plotly.graph_objects as go
            from plotly.subplots import make_subplots
            
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            fig.add_trace(
                go.Bar(x=df["Clause"], y=df["Support"], name="Support", marker_color='green'),
                secondary_y=False,
            )
            fig.add_trace(
                go.Bar(x=df["Clause"], y=df["Objection"], name="Objection", marker_color='red'),
                secondary_y=False,
            )
            fig.add_trace(
                go.Scatter(x=df["Clause"], y=df["Heat"], name="Heat Score", line=dict(color='blue')),
                secondary_y=True,
            )
            fig.update_layout(title_text="Clause Analysis")
            fig.update_xaxes(title_text="Clause")
            fig.update_yaxes(title_text="Argument Count", secondary_y=False)
            fig.update_yaxes(title_text="Heat Score", secondary_y=True)
            st.plotly_chart(fig, use_container_width=True)
    
    # Suggestions
    if dashboard_data.get("suggestions"):
        st.subheader("Policy Suggestions")
        for i, suggestion in enumerate(dashboard_data["suggestions"]):
            with st.expander(f"{suggestion.get('type', 'Suggestion').replace('_', ' ').title()}: {suggestion.get('summary', '')}"):
                st.markdown(f"**Clause:** {suggestion.get('clause', 'N/A')}")
                st.markdown(f"**Details:** {suggestion.get('details', '')}")
                st.markdown(f"**Suggested Change:** {suggestion.get('suggested_change', '')}")
                st.markdown(f"**Confidence:** {suggestion.get('confidence', 0)*100:.1f}%")

def show_glossary():
    st.header("📖 Glossary of Terms")
    
    try:
        response = requests.get(f"{API_BASE_URL}/explain/glossary")
        if response.status_code == 200:
            glossary = response.json()
            
            search_term = st.text_input("Search terms...")
            
            terms_to_display = glossary.get("terms", [])
            if search_term:
                terms_to_display = [
                    term for term in terms_to_display
                    if search_term.lower() in term.get("title", "").lower() or
                       search_term.lower() in term.get("definition", "").lower()
                ]
            
            for term in terms_to_display:
                with st.expander(term.get("title", "")):
                    st.markdown(term.get("definition", ""))
                    
                    # Get detailed explanation
                    detail_response = requests.get(f"{API_BASE_URL}/explain/concept/{term.get('id', '')}")
                    if detail_response.status_code == 200:
                        detail = detail_response.json()
                        if "error" not in detail:
                            st.markdown(f"**Why Important:** {detail.get('why_important', '')}")
                            st.markdown(f"**How Calculated:** {detail.get('how_calculated', '')}")
        else:
            st.error("Failed to load glossary")
    except Exception as e:
        st.error(f"Error loading glossary: {str(e)}")

def show_help():
    st.header("ℹ️ Help & Getting Started")
    
    try:
        response = requests.get(f"{API_BASE_URL}/explain/walkthrough")
        if response.status_code == 200:
            walkthrough = response.json()
            
            st.subheader("Step-by-Step Guide")
            for step in walkthrough.get("steps", []):
                st.markdown(f"### Step {step.get('step', 0)}: {step.get('title', '')}")
                st.markdown(step.get('description', ''))
                st.markdown(f"*{step.get('details', '')}*")
                st.markdown("---")
        else:
            st.error("Failed to load help guide")
    except Exception as e:
        st.error(f"Error loading help guide: {str(e)}")
    
    st.subheader("Need More Help?")
    st.markdown("""
    - Check the [Documentation](https://github.com/your-repo/docs)
    - Report issues on [GitHub](https://github.com/your-repo/issues)
    - Contact support: support@sovereignsedict.com
    """)

if __name__ == "__main__":
    main()
```

#### Step 2: Update Requirements

Update `requirements.txt` to include Streamlit dependencies:

```
# Streamlit frontend
streamlit>=1.25.0
plotly>=5.15.0
```

#### Step 3: Create Streamlit Startup Script

Create `start_streamlit.sh`:

```bash
#!/bin/bash
# Start Streamlit frontend for Sovereign's Edict

echo "Starting Sovereign's Edict Streamlit frontend..."

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "Starting backend server..."
    cd backend
    python main.py &
    cd ..
    sleep 5
fi

# Start Streamlit
streamlit run streamlit_app.py --server.port 8501 --server.address 0.0.0.0
```

Make it executable:

```bash
chmod +x start_streamlit.sh
```

### 2. Gradio Frontend Implementation

#### Step 1: Create Gradio Application

Create `gradio_app.py` in the root directory:

```python
"""
Gradio frontend for Sovereign's Edict
"""
import gradio as gr
import requests
import pandas as pd
import json
import time

# Configuration
API_BASE_URL = "http://localhost:8000"

# Custom CSS
custom_css = """
.gradio-container {
    font-family: 'Arial', sans-serif;
}
.header {
    text-align: center;
    padding: 20px;
    background-color: #f0f8ff;
    border-radius: 10px;
    margin-bottom: 20px;
}
.step {
    background-color: #e6f3ff;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 15px;
}
.success-box {
    background-color: #d4edda;
    border: 1px solid #c3e6cb;
    border-radius: 4px;
    padding: 15px;
    margin: 10px 0;
}
.error-box {
    background-color: #f8d7da;
    border: 1px solid #f5c6cb;
    border-radius: 4px;
    padding: 15px;
    margin: 10px 0;
}
"""

def upload_policy(policy_file):
    """Upload policy document"""
    if policy_file is None:
        return "Please select a policy file"
    
    try:
        files = {"file": (policy_file.name, open(policy_file.name, 'rb'), "text/plain")}
        response = requests.post(f"{API_BASE_URL}/upload/policy", files=files)
        
        if response.status_code == 200:
            return "✅ Policy document uploaded successfully!"
        else:
            return f"❌ Failed to upload policy: {response.text}"
    except Exception as e:
        return f"❌ Error uploading policy: {str(e)}"

def upload_comments(comment_file):
    """Upload comments file"""
    if comment_file is None:
        return "Please select a comments file"
    
    try:
        if comment_file.name.endswith(".csv"):
            files = {"file": (comment_file.name, open(comment_file.name, 'rb'), "text/csv")}
            response = requests.post(f"{API_BASE_URL}/upload/comments/csv", files=files)
        else:
            files = {"file": (comment_file.name, open(comment_file.name, 'rb'), "application/json")}
            response = requests.post(f"{API_BASE_URL}/upload/comments/json", files=files)
        
        if response.status_code == 200:
            return "✅ Comments uploaded successfully!"
        else:
            return f"❌ Failed to upload comments: {response.text}"
    except Exception as e:
        return f"❌ Error uploading comments: {str(e)}"

def run_analysis(quick_mode):
    """Run policy analysis"""
    try:
        if quick_mode:
            response = requests.post(f"{API_BASE_URL}/analyze/quick?limit=50")
        else:
            response = requests.post(f"{API_BASE_URL}/analyze")
        
        if response.status_code == 200:
            result = response.json()
            summary = f"""
            ✅ Analysis completed successfully!
            
            **Summary:**
            - Arguments Extracted: {result.get('num_arguments', 0)}
            - Clauses Analyzed: {len(result.get('clause_arguments', {}))}
            - Suggestions Generated: {len(result.get('suggestions', []))}
            """
            return summary
        else:
            return f"❌ Analysis failed: {response.text}"
    except Exception as e:
        return f"❌ Error during analysis: {str(e)}"

def get_dashboard():
    """Get dashboard data"""
    try:
        response = requests.get(f"{API_BASE_URL}/results/dashboard")
        if response.status_code == 200:
            data = response.json()
            
            # Create summary
            summary = f"""
            ## Analysis Summary
            
            - Total Arguments: {data.get('total_arguments', 0)}
            - Clauses Analyzed: {len(data.get('clause_analysis', {}))}
            - Suggestions: {len(data.get('suggestions', []))}
            """
            
            # Create clause data table
            if data.get('clause_analysis'):
                clause_data = []
                for clause_id, analysis in data['clause_analysis'].items():
                    clause_data.append([
                        clause_id,
                        analysis.get('support_count', 0),
                        analysis.get('objection_count', 0),
                        analysis.get('total_arguments', 0),
                        f"{analysis.get('controversy_score', 0)*100:.1f}%",
                        analysis.get('heat_score', 0)
                    ])
                
                clause_df = pd.DataFrame(
                    clause_data,
                    columns=["Clause", "Support", "Objection", "Total", "Controversy %", "Heat Score"]
                )
                
                return summary, clause_df
            else:
                return summary, pd.DataFrame()
        else:
            return f"❌ Failed to get dashboard data: {response.text}", pd.DataFrame()
    except Exception as e:
        return f"❌ Error getting dashboard data: {str(e)}", pd.DataFrame()

def get_glossary():
    """Get glossary terms"""
    try:
        response = requests.get(f"{API_BASE_URL}/explain/glossary")
        if response.status_code == 200:
            glossary = response.json()
            terms = []
            for term in glossary.get('terms', []):
                terms.append([term.get('title', ''), term.get('definition', '')])
            return pd.DataFrame(terms, columns=['Term', 'Definition'])
        else:
            return pd.DataFrame({'Error': [f"Failed to load glossary: {response.text}"]})
    except Exception as e:
        return pd.DataFrame({'Error': [f"Error loading glossary: {str(e)}"]})

# Create Gradio interface
with gr.Blocks(css=custom_css) as demo:
    gr.Markdown("""
    <div class="header">
    <h1>🏛️ Sovereign's Edict</h1>
    <p>An Actionable Intelligence Platform for Clause-Level Policy Argumentation</p>
    </div>
    """)
    
    with gr.Tab("Upload Data"):
        gr.Markdown("## Step 1: Upload Policy Document")
        with gr.Row():
            with gr.Column():
                policy_file = gr.File(label="Upload Policy Document (TXT)", file_types=[".txt"])
                upload_policy_btn = gr.Button("Upload Policy")
                policy_output = gr.Textbox(label="Upload Status", interactive=False)
        
        gr.Markdown("## Step 2: Upload Comments")
        with gr.Row():
            with gr.Column():
                comment_file = gr.File(label="Upload Comments (CSV/JSON)", file_types=[".csv", ".json"])
                upload_comments_btn = gr.Button("Upload Comments")
                comments_output = gr.Textbox(label="Upload Status", interactive=False)
        
        upload_policy_btn.click(upload_policy, inputs=policy_file, outputs=policy_output)
        upload_comments_btn.click(upload_comments, inputs=comment_file, outputs=comments_output)
    
    with gr.Tab("Analyze"):
        gr.Markdown("## Step 3: Run Analysis")
        with gr.Row():
            with gr.Column():
                quick_mode = gr.Checkbox(label="Quick Demo Mode (First 50 comments)", value=True)
                analyze_btn = gr.Button("🚀 Run Analysis")
                analysis_output = gr.Textbox(label="Analysis Status", interactive=False)
        
        analyze_btn.click(run_analysis, inputs=quick_mode, outputs=analysis_output)
    
    with gr.Tab("Dashboard"):
        gr.Markdown("## Step 4: View Results")
        with gr.Row():
            with gr.Column():
                dashboard_btn = gr.Button("📊 Get Dashboard Data")
                dashboard_output = gr.Textbox(label="Analysis Summary", interactive=False)
                clause_table = gr.Dataframe(label="Clause Analysis")
        
        dashboard_btn.click(get_dashboard, inputs=None, outputs=[dashboard_output, clause_table])
    
    with gr.Tab("Glossary"):
        gr.Markdown("## Glossary of Terms")
        with gr.Row():
            with gr.Column():
                glossary_btn = gr.Button("📖 Load Glossary")
                glossary_table = gr.Dataframe(label="Terms and Definitions")
        
        glossary_btn.click(get_glossary, inputs=None, outputs=glossary_table)
    
    with gr.Tab("Help"):
        gr.Markdown("""
        ## Getting Started Guide
        
        ### Step 1: Upload Data
        - Upload your policy document in TXT format
        - Upload public comments in CSV or JSON format
        
        ### Step 2: Run Analysis
        - Click "Run Analysis" to process your data
        - Use Quick Demo Mode for faster results during testing
        
        ### Step 3: View Results
        - Check the Dashboard tab for analysis results
        - View clause-level analysis and policy suggestions
        
        ### Step 4: Learn More
        - Browse the Glossary for term definitions
        - Contact support if you need help
        """)

# Launch the app
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
```

#### Step 2: Update Requirements

Update `requirements.txt` to include Gradio dependencies:

```
# Gradio frontend
gradio>=3.40.0
```

#### Step 3: Create Gradio Startup Script

Create `start_gradio.sh`:

```bash
#!/bin/bash
# Start Gradio frontend for Sovereign's Edict

echo "Starting Sovereign's Edict Gradio frontend..."

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "Starting backend server..."
    cd backend
    python main.py &
    cd ..
    sleep 5
fi

# Start Gradio
python gradio_app.py
```

Make it executable:

```bash
chmod +x start_gradio.sh
```

### 3. Docker Containerization

#### Step 1: Create Main Dockerfile

Update the main `Dockerfile`:

```dockerfile
# Sovereign's Edict - Main Application
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Command to run the application
CMD ["python", "backend/main.py"]
```

#### Step 2: Create Streamlit Dockerfile

Create `Dockerfile.streamlit`:

```dockerfile
# Sovereign's Edict - Streamlit Frontend
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install additional Streamlit dependencies
RUN pip install streamlit plotly

# Copy application code
COPY . .

# Expose ports
EXPOSE 8000 8501

# Command to run the application
CMD ["sh", "start_streamlit.sh"]
```

#### Step 3: Create Gradio Dockerfile

Create `Dockerfile.gradio`:

```dockerfile
# Sovereign's Edict - Gradio Frontend
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install additional Gradio dependencies
RUN pip install gradio

# Copy application code
COPY . .

# Expose ports
EXPOSE 8000 7860

# Command to run the application
CMD ["sh", "start_gradio.sh"]
```

#### Step 4: Update Docker Compose

Update `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app/backend
      - ./data:/app/data
    environment:
      - ENV=development
    command: python backend/main.py

  streamlit:
    build:
      context: .
      dockerfile: Dockerfile.streamlit
    ports:
      - "8501:8501"
    depends_on:
      - backend
    environment:
      - BACKEND_URL=http://backend:8000

  gradio:
    build:
      context: .
      dockerfile: Dockerfile.gradio
    ports:
      - "7860:7860"
    depends_on:
      - backend
    environment:
      - BACKEND_URL=http://backend:8000

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.frontend
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - CHOKIDAR_USEPOLLING=true
    depends_on:
      - backend
```

### 4. Single-Command Installation

#### Step 1: Create Installation Script

Create `install.sh`:

```bash
#!/bin/bash
# One-click installation script for Sovereign's Edict

echo "🏛️ Installing Sovereign's Edict..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ and try again."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip is not installed. Please install pip and try again."
    exit 1
fi

# Check if Node.js is installed (for React frontend)
if ! command -v node &> /dev/null; then
    echo "⚠️ Node.js is not installed. React frontend will not be available."
    echo "You can still use Streamlit or Gradio frontends."
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv sovereign_venv

# Activate virtual environment
source sovereign_venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Install frontend dependencies if Node.js is available
if command -v node &> /dev/null; then
    echo "Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "Please edit .env to add your GEMINI_API_KEY"
fi

echo "✅ Installation complete!"
echo ""
echo "To run the application:"
echo "1. Activate the virtual environment: source sovereign_venv/bin/activate"
echo "2. Start the backend: cd backend && python main.py"
echo "3. In a new terminal, start the frontend of your choice:"
echo "   - Streamlit: streamlit run streamlit_app.py"
echo "   - Gradio: python gradio_app.py"
echo "   - React: cd frontend && npm start"
echo ""
echo "Visit http://localhost:8501 (Streamlit) or http://localhost:7860 (Gradio) in your browser"
```

Make it executable:

```bash
chmod +x install.sh
```

#### Step 2: Update README with Installation Instructions

Update `README.md`:

```markdown
## No-Setup Deployment

Sovereign's Edict offers multiple easy deployment options:

### One-Click Installation

Run the installation script:

```bash
./install.sh
```

This will:
- Create a virtual environment
- Install all Python dependencies
- Install frontend dependencies (if Node.js is available)
- Set up environment configuration

### Docker Deployment

For organizations that prefer containerized deployment:

```bash
docker-compose up
```

This will start:
- Backend API on port 8000
- Streamlit frontend on port 8501
- Gradio frontend on port 7860
- React frontend on port 3000

### Individual Frontend Options

#### Streamlit Frontend
```bash
streamlit run streamlit_app.py
```
Access at: http://localhost:8501

#### Gradio Frontend
```bash
python gradio_app.py
```
Access at: http://localhost:7860

#### React Frontend
```bash
cd frontend
npm start
```
Access at: http://localhost:3000

All frontends connect to the backend API at http://localhost:8000
```

### 5. Testing and Verification

#### Step 1: Test Streamlit Frontend
```bash
# Start backend
cd backend
python main.py &

# Start Streamlit
streamlit run ../streamlit_app.py
```

#### Step 2: Test Gradio Frontend
```bash
# Start Gradio
python gradio_app.py
```

#### Step 3: Test Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up --build
```

#### Step 4: Test Installation Script
```bash
# Run installation script
./install.sh
```

### 6. Documentation Updates

Update the README.md to include information about deployment options:

```markdown
## Deployment Options

Sovereign's Edict can be deployed in multiple ways to suit different needs:

### Local Development
Run directly on your machine with Python and Node.js.

### Containerized Deployment
Use Docker for consistent deployment across environments.

### Single-Command Installation
One-click setup script for quick installation.

### Multiple Frontend Options
Choose from React, Streamlit, or Gradio interfaces.
```

## Next Steps

After implementing no-setup deployment:
1. Proceed to Phase 7: Lightweight, Offline-First
2. Update user documentation with deployment instructions
3. Test all deployment options on different platforms
4. Create release packages for easy distribution