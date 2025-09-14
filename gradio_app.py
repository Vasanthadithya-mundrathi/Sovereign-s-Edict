"""
Gradio frontend for Sovereign's Edict
"""
import gradio as gr
import requests
import json

def upload_policy(file):
    """Upload a policy document"""
    if file is None:
        return "No file selected"
    
    try:
        # In a real implementation, you would send the file to the backend
        return f"Policy document '{file.name}' uploaded successfully!"
    except Exception as e:
        return f"Error uploading policy: {str(e)}"

def upload_comments(file):
    """Upload comments"""
    if file is None:
        return "No file selected"
    
    try:
        # In a real implementation, you would send the file to the backend
        return f"Comments file '{file.name}' uploaded successfully!"
    except Exception as e:
        return f"Error uploading comments: {str(e)}"

def list_plugins():
    """List available plugins"""
    try:
        response = requests.get("http://localhost:8001/plugins")
        if response.status_code == 200:
            plugins = response.json()
            return json.dumps(plugins, indent=2)
        else:
            return f"Failed to fetch plugins: {response.status_code}"
    except Exception as e:
        return f"Error connecting to backend: {str(e)}"

def ingest_with_plugin(plugin_name, source):
    """Ingest data using a plugin"""
    if not plugin_name or not source:
        return "Please provide both plugin name and source"
    
    try:
        response = requests.post(
            f"http://localhost:8001/ingest/plugin/{plugin_name}",
            json={"source": source}
        )
        if response.status_code == 200:
            result = response.json()
            return json.dumps(result, indent=2)
        else:
            return f"Failed to ingest data: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error connecting to backend: {str(e)}"

def run_analysis():
    """Run analysis"""
    try:
        response = requests.post("http://localhost:8001/analyze")
        if response.status_code == 200:
            result = response.json()
            return json.dumps(result, indent=2)
        elif response.status_code == 400:
            return f"Analysis failed: {response.json()['detail']}"
        else:
            return f"Analysis failed: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Error connecting to backend: {str(e)}"

def get_results():
    """Get analysis results"""
    try:
        response = requests.get("http://localhost:8001/results/arguments")
        if response.status_code == 200:
            arguments = response.json()
            return json.dumps(arguments, indent=2)
        else:
            return f"Failed to fetch results: {response.status_code}"
    except Exception as e:
        return f"Error connecting to backend: {str(e)}"

def get_suggestions():
    """Get policy suggestions"""
    try:
        response = requests.get("http://localhost:8001/results/suggestions")
        if response.status_code == 200:
            suggestions = response.json()
            return json.dumps(suggestions, indent=2)
        else:
            return f"Failed to fetch suggestions: {response.status_code}"
    except Exception as e:
        return f"Error connecting to backend: {str(e)}"

# Create the Gradio interface
with gr.Blocks(title="Sovereign's Edict") as demo:
    gr.Markdown("# 🏛️ Sovereign's Edict")
    gr.Markdown("An Actionable Intelligence Platform for Clause-Level Policy Argumentation")
    
    with gr.Tab("Upload Data"):
        with gr.Row():
            with gr.Column():
                gr.Markdown("## Upload Policy Document")
                policy_file = gr.File(label="Policy Document", file_types=[".txt", ".pdf"])
                policy_upload_btn = gr.Button("Upload Policy")
                policy_output = gr.Textbox(label="Upload Status")
                policy_upload_btn.click(upload_policy, inputs=policy_file, outputs=policy_output)
            
            with gr.Column():
                gr.Markdown("## Upload Comments")
                comments_file = gr.File(label="Comments File", file_types=[".csv", ".json"])
                comments_upload_btn = gr.Button("Upload Comments")
                comments_output = gr.Textbox(label="Upload Status")
                comments_upload_btn.click(upload_comments, inputs=comments_file, outputs=comments_output)
        
        with gr.Row():
            gr.Markdown("## Ingest Data Using Plugins")
            with gr.Column():
                list_plugins_btn = gr.Button("List Available Plugins")
                plugins_output = gr.Textbox(label="Available Plugins")
                list_plugins_btn.click(list_plugins, outputs=plugins_output)
            
            with gr.Column():
                plugin_name = gr.Textbox(label="Plugin Name", value="gov_database")
                source = gr.Textbox(label="Source", value="sample_query")
                ingest_btn = gr.Button("Ingest with Plugin")
                ingest_output = gr.Textbox(label="Ingestion Result")
                ingest_btn.click(ingest_with_plugin, inputs=[plugin_name, source], outputs=ingest_output)
    
    with gr.Tab("Analyze"):
        gr.Markdown("## Automated Analysis")
        analyze_btn = gr.Button("Run Analysis")
        analyze_output = gr.Textbox(label="Analysis Result")
        analyze_btn.click(run_analysis, outputs=analyze_output)
        gr.Markdown("*Estimated time: 2-5 minutes for small datasets*")
    
    with gr.Tab("Results"):
        gr.Markdown("## Analysis Results")
        results_btn = gr.Button("Get Results")
        results_output = gr.Textbox(label="Extracted Arguments")
        results_btn.click(get_results, outputs=results_output)
    
    with gr.Tab("Dashboard"):
        gr.Markdown("## Policy Dashboard")
        suggestions_btn = gr.Button("Get Policy Suggestions")
        suggestions_output = gr.Textbox(label="Policy Suggestions")
        suggestions_btn.click(get_suggestions, outputs=suggestions_output)

# Launch the app
if __name__ == "__main__":
    demo.launch()