# Phase 8: Community/Operator Mode Implementation

## Overview
Implement .csv/.json uploads, PDF policy processing, and PDF report export for community and operator use.

## Implementation Steps

### 1. Enhanced File Upload Support

#### Step 1: Add PDF Policy Processing

Create `backend/ingestion/pdf_processor.py`:

```python
"""
PDF policy document processor for Sovereign's Edict
"""
import PyPDF2
import pdfplumber
import re
from typing import List, Dict
from ..models.policy import PolicyDocument, PolicyClause
import uuid

def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from PDF using multiple methods for better accuracy
    """
    text = ""
    
    # Method 1: PyPDF2
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"PyPDF2 extraction failed: {str(e)}")
    
    # Method 2: pdfplumber (if PyPDF2 didn't work well)
    if not text.strip():
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"pdfplumber extraction failed: {str(e)}")
    
    return text

def identify_clauses(text: str) -> List[Dict]:
    """
    Identify policy clauses/sections in text
    """
    clauses = []
    
    # Pattern for common section headings
    patterns = [
        r'(?:Section|Clause|Article|Paragraph)\s+(\d+[A-Z]*)[:.]*\s*(.*?)(?=\n(?:Section|Clause|Article|Paragraph)|\Z)',
        r'(\d+[A-Z]*)[:.]*\s*(.*?)(?=\n\d+[A-Z]*[:.]|\Z)',
        r'(?:SEC\.|CLAUSE|ARTICLE)\s*(\d+[A-Z]*)[:.]*\s*(.*?)(?=\n(?:SEC\.|CLAUSE|ARTICLE)|\Z)'
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
        for match in matches:
            if len(match.groups()) >= 2:
                section_id = match.group(1).strip()
                content = match.group(2).strip()
                
                if content and len(content) > 20:  # Filter out very short sections
                    clauses.append({
                        "id": f"clause_{len(clauses) + 1}",
                        "section": section_id,
                        "text": content
                    })
    
    # If no structured clauses found, split by paragraphs
    if not clauses:
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip() and len(p.strip()) > 50]
        for i, paragraph in enumerate(paragraphs):
            clauses.append({
                "id": f"clause_{i + 1}",
                "section": f"Section {i + 1}",
                "text": paragraph
            })
    
    return clauses

def process_pdf_policy(file_path: str) -> PolicyDocument:
    """
    Process PDF policy document and convert to PolicyDocument
    """
    # Extract text
    text = extract_text_from_pdf(file_path)
    
    if not text.strip():
        raise Exception("Failed to extract text from PDF")
    
    # Identify clauses
    clauses_data = identify_clauses(text)
    
    # Create PolicyClause objects
    clauses = []
    for clause_data in clauses_data:
        clause = PolicyClause(
            id=clause_data["id"],
            text=clause_data["text"],
            section=clause_data["section"]
        )
        clauses.append(clause)
    
    # Create PolicyDocument
    policy = PolicyDocument(
        id=str(uuid.uuid4()),
        title="Policy from PDF Document",
        content=text,
        clauses=clauses
    )
    
    return policy
```

#### Step 2: Enhance File Upload Endpoints

Update `backend/main.py`:

```python
# Add import
from .ingestion.pdf_processor import process_pdf_policy

# Enhance policy upload endpoint
@app.post("/upload/policy")
async def upload_policy_document(file: UploadFile = File(...)):
    """
    Upload policy document (TXT, PDF)
    """
    try:
        # Save file temporarily
        file_extension = file.filename.split('.')[-1].lower()
        temp_file_path = f"/tmp/{uuid.uuid4()}.{file_extension}"
        
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process based on file type
        if file_extension == 'txt':
            # Parse text policy document
            policy = parse_policy_document(temp_file_path)
        elif file_extension == 'pdf':
            # Process PDF policy document
            policy = process_pdf_policy(temp_file_path)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_extension}")
        
        stored_data["policies"].append(policy)
        
        # Clean up
        os.remove(temp_file_path)
        
        return {
            "message": "Successfully uploaded policy document",
            "policy_id": policy.id,
            "title": policy.title,
            "clauses_count": len(policy.clauses)
        }
    except Exception as e:
        # Clean up on error
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(status_code=400, detail=str(e))

# Enhance comments upload endpoint
@app.post("/upload/comments")
async def upload_comments(file: UploadFile = File(...)):
    """
    Upload comments (CSV, Excel, JSON)
    """
    try:
        # Save file temporarily
        file_extension = file.filename.split('.')[-1].lower()
        temp_file_path = f"/tmp/{uuid.uuid4()}.{file_extension}"
        
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process based on file type
        if file_extension == 'csv':
            comments = parse_csv_comments(temp_file_path)
        elif file_extension in ['xlsx', 'xls']:
            comments = parse_excel_comments(temp_file_path)
        elif file_extension == 'json':
            comments = parse_json_comments(temp_file_path)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_extension}")
        
        stored_data["comments"].extend(comments)
        
        # Clean up
        os.remove(temp_file_path)
        
        return {
            "message": f"Successfully uploaded {len(comments)} comments",
            "file_type": file_extension,
            "comment_ids": [comment.id for comment in comments]
        }
    except Exception as e:
        # Clean up on error
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(status_code=400, detail=str(e))

# Add new helper function for Excel parsing
def parse_excel_comments(file_path: str) -> List[Comment]:
    """
    Parse comments from Excel file
    """
    try:
        df = pd.read_excel(file_path)
        
        # Check for required columns
        required_columns = ['text']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise Exception(f"Missing required columns: {missing_columns}")
        
        comments = []
        for index, row in df.iterrows():
            comment = Comment(
                id=str(uuid.uuid4()),
                text=str(row['text']),
                source=row.get('source', 'excel_upload'),
                timestamp=row.get('timestamp', index),
                policy_clause=row.get('policy_clause', 'excel_upload')
            )
            comments.append(comment)
        
        return comments
        
    except Exception as e:
        raise Exception(f"Failed to parse Excel comments: {str(e)}")
```

### 2. PDF Report Export

#### Step 1: Create PDF Report Generator

Create `backend/reports/pdf_generator.py`:

```python
"""
PDF report generator for Sovereign's Edict
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import matplotlib.pyplot as plt
import numpy as np
import io
import base64
from typing import Dict, List
import os

def generate_analysis_report(analysis_data: Dict, output_path: str):
    """
    Generate PDF report from analysis data
    """
    # Create document
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    
    story.append(Paragraph("Sovereign's Edict", title_style))
    story.append(Paragraph("Policy Argumentation Analysis Report", styles['Heading2']))
    story.append(Spacer(1, 20))
    
    # Executive Summary
    story.append(Paragraph("Executive Summary", styles['Heading2']))
    
    summary_data = [
        ["Metric", "Value"],
        ["Total Arguments", str(analysis_data.get("total_arguments", 0))],
        ["Clauses Analyzed", str(len(analysis_data.get("clause_analysis", {})))],
        ["Suggestions Generated", str(len(analysis_data.get("suggestions", [])))],
        ["Processing Time", f"{analysis_data.get('processing_time', 0):.2f} seconds"]
    ]
    
    summary_table = Table(summary_data)
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(summary_table)
    story.append(Spacer(1, 20))
    
    # Policy Information
    if analysis_data.get("policy"):
        story.append(Paragraph("Policy Information", styles['Heading2']))
        story.append(Paragraph(f"Title: {analysis_data['policy']['title']}", styles['Normal']))
        story.append(Spacer(1, 10))
    
    # Clause Analysis
    story.append(Paragraph("Clause-Level Analysis", styles['Heading2']))
    
    # Create chart
    chart_buffer = create_clause_chart(analysis_data.get("clause_analysis", {}))
    if chart_buffer:
        story.append(Image(chart_buffer, width=6*inch, height=4*inch))
        story.append(Spacer(1, 20))
    
    # Detailed Clause Analysis
    clause_analysis = analysis_data.get("clause_analysis", {})
    if clause_analysis:
        story.append(Paragraph("Detailed Clause Analysis", styles['Heading3']))
        
        for clause_id, analysis in clause_analysis.items():
            story.append(Paragraph(f"Clauses {clause_id}", styles['Heading4']))
            
            clause_data = [
                ["Metric", "Value"],
                ["Support Arguments", str(analysis.get("support_count", 0))],
                ["Objection Arguments", str(analysis.get("objection_count", 0))],
                ["Total Arguments", str(analysis.get("total_arguments", 0))],
                ["Controversy Score", f"{analysis.get('controversy_score', 0)*100:.1f}%"],
                ["Heat Score", str(analysis.get("heat_score", 0))]
            ]
            
            clause_table = Table(clause_data)
            clause_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(clause_table)
            story.append(Spacer(1, 10))
    
    # Suggestions
    suggestions = analysis_data.get("suggestions", [])
    if suggestions:
        story.append(Paragraph("Policy Suggestions", styles['Heading2']))
        
        for i, suggestion in enumerate(suggestions[:10]):  # Limit to top 10
            story.append(Paragraph(f"{i+1}. {suggestion.get('summary', '')}", styles['Heading4']))
            story.append(Paragraph(f"Clause: {suggestion.get('clause', 'N/A')}", styles['Normal']))
            story.append(Paragraph(f"Details: {suggestion.get('details', '')}", styles['Normal']))
            story.append(Paragraph(f"Suggested Change: {suggestion.get('suggested_change', '')}", styles['Normal']))
            story.append(Paragraph(f"Confidence: {suggestion.get('confidence', 0)*100:.1f}%", styles['Normal']))
            story.append(Spacer(1, 10))
    
    # Build PDF
    doc.build(story)

def create_clause_chart(clause_analysis: Dict) -> io.BytesIO:
    """
    Create clause analysis chart
    """
    try:
        if not clause_analysis:
            return None
        
        # Prepare data
        clauses = list(clause_analysis.keys())
        support_counts = [analysis.get("support_count", 0) for analysis in clause_analysis.values()]
        objection_counts = [analysis.get("objection_count", 0) for analysis in clause_analysis.values()]
        
        # Create bar chart
        fig, ax = plt.subplots(figsize=(10, 6))
        x = np.arange(len(clauses))
        width = 0.35
        
        ax.bar(x - width/2, support_counts, width, label='Support', color='green', alpha=0.7)
        ax.bar(x + width/2, objection_counts, width, label='Objection', color='red', alpha=0.7)
        
        ax.set_xlabel('Clauses')
        ax.set_ylabel('Argument Count')
        ax.set_title('Support vs Objection Arguments by Clause')
        ax.set_xticks(x)
        ax.set_xticklabels(clauses, rotation=45, ha='right')
        ax.legend()
        
        plt.tight_layout()
        
        # Save to buffer
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
        buffer.seek(0)
        
        plt.close(fig)
        return buffer
        
    except Exception as e:
        print(f"Failed to create chart: {str(e)}")
        return None
```

#### Step 2: Add PDF Export Endpoint

Update `backend/main.py`:

```python
# Add import
from .reports.pdf_generator import generate_analysis_report

# Add PDF export endpoint
@app.get("/export/pdf")
async def export_pdf_report():
    """
    Export analysis results as PDF report
    """
    if not stored_data.get("analysis_results"):
        raise HTTPException(status_code=400, detail="No analysis completed")
    
    try:
        # Get dashboard data
        dashboard_response = requests.get("http://localhost:8000/results/dashboard")
        if dashboard_response.status_code != 200:
            raise HTTPException(status_code=500, detail="Failed to get dashboard data")
        
        dashboard_data = dashboard_response.json()
        
        # Generate PDF
        output_path = f"/tmp/sovereigns_edict_report_{int(time.time())}.pdf"
        generate_analysis_report(dashboard_data, output_path)
        
        # Return file
        return FileResponse(
            output_path,
            media_type='application/pdf',
            filename='sovereigns_edict_analysis_report.pdf'
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate PDF report: {str(e)}")
```

### 3. Frontend Updates for Community Features

#### Step 1: Update Streamlit Frontend

Update `streamlit_app.py`:

```python
# Add PDF export functionality
def show_dashboard():
    # ... existing dashboard code ...
    
    # Add export button
    if st.button("📥 Export as PDF Report"):
        try:
            response = requests.get(f"{API_BASE_URL}/export/pdf")
            if response.status_code == 200:
                st.success("PDF report generated successfully!")
                st.download_button(
                    label="Download PDF Report",
                    data=response.content,
                    file_name="sovereigns_edict_analysis_report.pdf",
                    mime="application/pdf"
                )
            else:
                st.error(f"Failed to generate PDF report: {response.text}")
        except Exception as e:
            st.error(f"Error generating PDF report: {str(e)}")

# Update upload section to support PDF
def show_upload():
    st.header("📤 Upload Data")
    
    # Policy document upload
    st.subheader("Policy Document")
    policy_file = st.file_uploader("Upload policy document (TXT, PDF)", type=["txt", "pdf"])
    
    # ... rest of existing code ...

# Update comments upload to be more generic
def show_upload():
    # ... existing policy upload code ...
    
    # Comments upload
    st.subheader("Public Comments")
    comment_file = st.file_uploader("Upload comments (CSV, Excel, JSON)", type=["csv", "xlsx", "xls", "json"])
    
    # ... rest of existing code ...
```

#### Step 2: Update Gradio Frontend

Update `gradio_app.py`:

```python
# Add PDF export function
def export_pdf_report():
    """Export analysis results as PDF"""
    try:
        response = requests.get(f"{API_BASE_URL}/export/pdf")
        if response.status_code == 200:
            # Save PDF to temporary file
            pdf_path = f"/tmp/report_{int(time.time())}.pdf"
            with open(pdf_path, 'wb') as f:
                f.write(response.content)
            return pdf_path
        else:
            return f"❌ Failed to generate PDF: {response.text}"
    except Exception as e:
        return f"❌ Error generating PDF: {str(e)}"

# Update dashboard tab
with gr.Tab("Dashboard"):
    # ... existing dashboard code ...
    
    with gr.Row():
        with gr.Column():
            pdf_btn = gr.Button("📥 Export as PDF Report")
            pdf_output = gr.File(label="Download PDF Report")
    
    pdf_btn.click(export_pdf_report, inputs=None, outputs=pdf_output)

# Update upload tabs to support more file types
with gr.Tab("Upload Data"):
    gr.Markdown("## Step 1: Upload Policy Document")
    with gr.Row():
        with gr.Column():
            policy_file = gr.File(label="Upload Policy Document (TXT, PDF)", file_types=[".txt", ".pdf"])
            # ... rest of existing code ...
    
    gr.Markdown("## Step 2: Upload Comments")
    with gr.Row():
        with gr.Column():
            comment_file = gr.File(label="Upload Comments (CSV, Excel, JSON)", file_types=[".csv", ".xlsx", ".xls", ".json"])
            # ... rest of existing code ...
```

### 4. Bulk Processing for Operators

#### Step 1: Create Batch Processing Endpoint

Update `backend/main.py`:

```python
# Add batch processing endpoint
@app.post("/batch/process")
async def batch_process_policies(policies: List[UploadFile] = File(...), comments_files: List[UploadFile] = File(...)):
    """
    Batch process multiple policy/comment files
    """
    results = []
    
    try:
        # Process each policy
        for policy_file in policies:
            try:
                # Save policy file temporarily
                policy_extension = policy_file.filename.split('.')[-1].lower()
                policy_temp_path = f"/tmp/policy_{uuid.uuid4()}.{policy_extension}"
                
                with open(policy_temp_path, "wb") as buffer:
                    content = await policy_file.read()
                    buffer.write(content)
                
                # Process policy
                if policy_extension == 'txt':
                    policy = parse_policy_document(policy_temp_path)
                elif policy_extension == 'pdf':
                    policy = process_pdf_policy(policy_temp_path)
                else:
                    raise Exception(f"Unsupported policy file type: {policy_extension}")
                
                stored_data["policies"].append(policy)
                os.remove(policy_temp_path)
                
                # Process associated comments
                policy_comments = []
                for comment_file in comments_files:
                    try:
                        # Save comment file temporarily
                        comment_extension = comment_file.filename.split('.')[-1].lower()
                        comment_temp_path = f"/tmp/comment_{uuid.uuid4()}.{comment_extension}"
                        
                        with open(comment_temp_path, "wb") as buffer:
                            content = await comment_file.read()
                            buffer.write(content)
                        
                        # Process comments
                        if comment_extension == 'csv':
                            comments = parse_csv_comments(comment_temp_path)
                        elif comment_extension in ['xlsx', 'xls']:
                            comments = parse_excel_comments(comment_temp_path)
                        elif comment_extension == 'json':
                            comments = parse_json_comments(comment_temp_path)
                        else:
                            raise Exception(f"Unsupported comment file type: {comment_extension}")
                        
                        policy_comments.extend(comments)
                        stored_data["comments"].extend(comments)
                        os.remove(comment_temp_path)
                        
                    except Exception as e:
                        print(f"Failed to process comment file {comment_file.filename}: {str(e)}")
                
                results.append({
                    "policy_title": policy.title,
                    "policy_id": policy.id,
                    "comments_processed": len(policy_comments),
                    "status": "success"
                })
                
            except Exception as e:
                results.append({
                    "policy_file": policy_file.filename,
                    "status": "error",
                    "error": str(e)
                })
        
        return {
            "message": "Batch processing completed",
            "results": results
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch processing failed: {str(e)}")
```

### 5. Data Validation and Quality Checks

#### Step 1: Create Data Validator

Create `backend/utils/data_validator.py`:

```python
"""
Data validator for Sovereign's Edict
"""
import pandas as pd
from typing import List, Dict, Tuple
from ..models.comment import Comment

def validate_comments_data(comments: List[Comment]) -> Dict:
    """
    Validate comments data quality
    """
    validation_results = {
        "total_comments": len(comments),
        "valid_comments": 0,
        "invalid_comments": 0,
        "issues": []
    }
    
    for i, comment in enumerate(comments):
        issues = []
        
        # Check text quality
        if not comment.text or not comment.text.strip():
            issues.append("Empty or whitespace-only text")
        elif len(comment.text.strip()) < 10:
            issues.append("Text too short (less than 10 characters)")
        elif len(comment.text.strip()) > 5000:
            issues.append("Text too long (more than 5000 characters)")
        
        # Check source
        if not comment.source or not comment.source.strip():
            issues.append("Missing source information")
        
        # Check policy clause
        if not comment.policy_clause or not comment.policy_clause.strip():
            issues.append("Missing policy clause reference")
        
        if issues:
            validation_results["invalid_comments"] += 1
            validation_results["issues"].append({
                "comment_id": comment.id,
                "comment_index": i,
                "issues": issues
            })
        else:
            validation_results["valid_comments"] += 1
    
    return validation_results

def validate_csv_structure(file_path: str) -> Tuple[bool, List[str]]:
    """
    Validate CSV file structure
    """
    issues = []
    
    try:
        df = pd.read_csv(file_path)
        
        # Check required columns
        required_columns = ['text']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            issues.append(f"Missing required columns: {missing_columns}")
        
        # Check for empty rows
        empty_rows = df[df.isnull().all(axis=1)]
        if len(empty_rows) > 0:
            issues.append(f"Found {len(empty_rows)} completely empty rows")
        
        # Check text column for empty values
        if 'text' in df.columns:
            empty_text = df[df['text'].isnull() | (df['text'].astype(str).str.strip() == '')]
            if len(empty_text) > 0:
                issues.append(f"Found {len(empty_text)} rows with empty text")
        
        return len(issues) == 0, issues
        
    except Exception as e:
        return False, [f"Failed to read CSV file: {str(e)}"]

def validate_excel_structure(file_path: str) -> Tuple[bool, List[str]]:
    """
    Validate Excel file structure
    """
    issues = []
    
    try:
        df = pd.read_excel(file_path)
        
        # Check required columns
        required_columns = ['text']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            issues.append(f"Missing required columns: {missing_columns}")
        
        # Check for empty rows
        empty_rows = df[df.isnull().all(axis=1)]
        if len(empty_rows) > 0:
            issues.append(f"Found {len(empty_rows)} completely empty rows")
        
        # Check text column for empty values
        if 'text' in df.columns:
            empty_text = df[df['text'].isnull() | (df['text'].astype(str).str.strip() == '')]
            if len(empty_text) > 0:
                issues.append(f"Found {len(empty_text)} rows with empty text")
        
        return len(issues) == 0, issues
        
    except Exception as e:
        return False, [f"Failed to read Excel file: {str(e)}"]

def validate_json_structure(file_path: str) -> Tuple[bool, List[str]]:
    """
    Validate JSON file structure
    """
    issues = []
    
    try:
        import json
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        if not isinstance(data, list):
            issues.append("JSON file should contain an array of comment objects")
            return len(issues) == 0, issues
        
        # Check required fields in each object
        for i, item in enumerate(data):
            if not isinstance(item, dict):
                issues.append(f"Item {i} is not a valid object")
                continue
            
            if 'text' not in item:
                issues.append(f"Item {i} missing required 'text' field")
        
        return len(issues) == 0, issues
        
    except Exception as e:
        return False, [f"Failed to read JSON file: {str(e)}"]
```

#### Step 2: Integrate Validation into Upload Endpoints

Update `backend/main.py`:

```python
# Add import
from .utils.data_validator import validate_comments_data, validate_csv_structure, validate_excel_structure, validate_json_structure

# Update comments upload endpoint with validation
@app.post("/upload/comments")
async def upload_comments(file: UploadFile = File(...), validate: bool = True):
    """
    Upload comments (CSV, Excel, JSON) with optional validation
    """
    try:
        # Save file temporarily
        file_extension = file.filename.split('.')[-1].lower()
        temp_file_path = f"/tmp/{uuid.uuid4()}.{file_extension}"
        
        with open(temp_file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Validate file structure if requested
        if validate:
            if file_extension == 'csv':
                is_valid, issues = validate_csv_structure(temp_file_path)
            elif file_extension in ['xlsx', 'xls']:
                is_valid, issues = validate_excel_structure(temp_file_path)
            elif file_extension == 'json':
                is_valid, issues = validate_json_structure(temp_file_path)
            else:
                is_valid, issues = True, []
            
            if not is_valid:
                os.remove(temp_file_path)
                raise HTTPException(status_code=400, detail=f"File validation failed: {'; '.join(issues)}")
        
        # Process based on file type
        if file_extension == 'csv':
            comments = parse_csv_comments(temp_file_path)
        elif file_extension in ['xlsx', 'xls']:
            comments = parse_excel_comments(temp_file_path)
        elif file_extension == 'json':
            comments = parse_json_comments(temp_file_path)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_extension}")
        
        # Validate comments data quality
        if validate:
            validation_results = validate_comments_data(comments)
            if validation_results["invalid_comments"] > 0:
                # Log issues but don't fail upload
                print(f"Validation issues found: {validation_results['invalid_comments']} invalid comments")
        
        stored_data["comments"].extend(comments)
        
        # Clean up
        os.remove(temp_file_path)
        
        return {
            "message": f"Successfully uploaded {len(comments)} comments",
            "file_type": file_extension,
            "comment_ids": [comment.id for comment in comments],
            "validation": validate_comments_data(comments) if validate else None
        }
    except Exception as e:
        # Clean up on error
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.remove(temp_file_path)
        raise HTTPException(status_code=400, detail=str(e))
```

### 6. Documentation Updates

#### Step 1: Update README with Community Features

Update `README.md`:

```markdown
## Community/Operator Mode

Sovereign's Edict includes enhanced features for community organizations and operators:

### File Format Support

- **Policy Documents**: TXT, PDF
- **Comments**: CSV, Excel (XLSX/XLS), JSON

### PDF Report Export

Generate professional PDF reports of your analysis for sharing and presentation.

### Batch Processing

Process multiple policy/comment files in a single operation.

### Data Validation

Built-in validation ensures data quality and identifies potential issues.

### Usage Examples

#### Upload Policy Document
```bash
curl -X POST "http://localhost:8000/upload/policy" -F "file=@policy.pdf"
```

#### Upload Comments
```bash
curl -X POST "http://localhost:8000/upload/comments" -F "file=@comments.xlsx"
```

#### Export PDF Report
```bash
curl -X GET "http://localhost:8000/export/pdf" -o analysis_report.pdf
```

#### Batch Process Multiple Files
```bash
curl -X POST "http://localhost:8000/batch/process" \
  -F "policies=@policy1.pdf" \
  -F "policies=@policy2.txt" \
  -F "comments_files=@comments1.csv" \
  -F "comments_files=@comments2.xlsx"
```
```

#### Step 2: Create Community Guide

Create `docs/COMMUNITY_GUIDE.md`:

```markdown
# Community User Guide

## Overview

This guide explains how to use Sovereign's Edict for community organizations, NGOs, and operators who need to analyze policy feedback at scale.

## Supported File Formats

### Policy Documents
- **TXT**: Plain text policy documents
- **PDF**: PDF policy documents (automatically converted to text)

### Comments
- **CSV**: Comma-separated values files
- **Excel**: XLSX and XLS spreadsheet files
- **JSON**: JavaScript Object Notation files

## File Structure Requirements

### CSV/Excel Comments
Required columns:
- `text`: The comment content (required)
- `source`: Source of the comment (optional)
- `timestamp`: Comment timestamp (optional)
- `policy_clause`: Relevant policy clause (optional)

Example:
```csv
text,source,timestamp,policy_clause
"This policy will help protect our community.",community_forum,1623456789,Section 3
"I'm concerned about the implementation costs.",public_hearing,1623456790,Section 7
```

### JSON Comments
Array of objects with at least a `text` field:

```json
[
  {
    "text": "This policy will help protect our community.",
    "source": "community_forum",
    "timestamp": 1623456789,
    "policy_clause": "Section 3"
  },
  {
    "text": "I'm concerned about the implementation costs.",
    "source": "public_hearing",
    "timestamp": 1623456790,
    "policy_clause": "Section 7"
  }
]
```

## Uploading Data

### Using the Web Interface
1. Navigate to the Upload Data section
2. Select your policy document file (TXT or PDF)
3. Select your comments file (CSV, Excel, or JSON)
4. Click Upload

### Using the API
```bash
# Upload policy document
curl -X POST "http://localhost:8000/upload/policy" -F "file=@your_policy.pdf"

# Upload comments
curl -X POST "http://localhost:8000/upload/comments" -F "file=@your_comments.xlsx"
```

## Data Validation

Uploaded data is automatically validated for quality:
- Empty or very short comments are flagged
- Missing source information is noted
- File structure is checked

Validation results are included in upload responses.

## Batch Processing

Process multiple files at once:

```bash
curl -X POST "http://localhost:8000/batch/process" \
  -F "policies=@policy1.pdf" \
  -F "policies=@policy2.txt" \
  -F "comments_files=@comments1.csv" \
  -F "comments_files=@comments2.xlsx"
```

## Exporting Results

### PDF Reports
Generate professional PDF reports for sharing:

```bash
curl -X GET "http://localhost:8000/export/pdf" -o policy_analysis_report.pdf
```

PDF reports include:
- Executive summary
- Clause-level analysis
- Visual charts
- Policy suggestions
- Detailed findings

### Data Export
Export processed data in various formats:
- JSON for further analysis
- CSV for spreadsheet processing
- Excel for detailed review

## Best Practices

### For Large Datasets
- Use batch processing for multiple files
- Enable quick demo mode for initial testing
- Validate data before full analysis

### For Community Organizations
- Use sample data to understand the platform
- Export PDF reports for stakeholder presentations
- Leverage data validation to ensure quality

### For Operators
- Use batch processing for regular analysis workflows
- Implement automated data validation in pipelines
- Customize export formats for organizational needs

## Troubleshooting

### Upload Issues
- Ensure files are in supported formats
- Check that required columns are present
- Verify file permissions

### Processing Errors
- Check validation reports for data quality issues
- Review file structure requirements
- Contact support for persistent issues

### Export Problems
- Ensure analysis is complete before exporting
- Check available disk space
- Verify PDF generation dependencies are installed
```

### 7. Testing and Verification

#### Step 1: Test File Uploads
```bash
# Test PDF policy upload
curl -X POST "http://localhost:8000/upload/policy" -F "file=@test_policy.pdf"

# Test Excel comments upload
curl -X POST "http://localhost:8000/upload/comments" -F "file=@test_comments.xlsx"

# Test JSON comments upload
curl -X POST "http://localhost:8000/upload/comments" -F "file=@test_comments.json"
```

#### Step 2: Test PDF Export
```bash
# Generate PDF report
curl -X GET "http://localhost:8000/export/pdf" -o test_report.pdf
```

#### Step 3: Test Batch Processing
```bash
# Batch process multiple files
curl -X POST "http://localhost:8000/batch/process" \
  -F "policies=@policy1.pdf" \
  -F "policies=@policy2.txt" \
  -F "comments_files=@comments1.csv" \
  -F "comments_files=@comments2.xlsx"
```

#### Step 4: Test Frontend Integration
1. Start the backend server
2. Start the Streamlit/Gradio frontend
3. Test uploading PDF policies
4. Test uploading Excel/JSON comments
5. Generate and download PDF reports
6. Verify batch processing works

## Next Steps

After implementing community/operator mode:
1. Proceed to Phase 9: Privacy and Transparency
2. Update user documentation with community features
3. Create sample datasets for community users
4. Test with actual community organizations