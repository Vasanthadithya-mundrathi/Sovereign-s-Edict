# Sovereign's Edict - Usage Guide

## Getting Started

### Prerequisites
- Python 3.8+
- Node.js 16+
- Docker (optional, for containerized deployment)

### Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd "Sovereign's Edict"
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   ```

## Running the Application

### Option 1: Using Docker (Recommended)
```bash
docker-compose up
```

This will start both the backend (port 8000) and frontend (port 3000) services.

### Option 2: Manual Installation

1. Start the backend server:
   ```bash
   cd backend
   python main.py
   ```

2. In a separate terminal, start the frontend:
   ```bash
   cd frontend
   npm start
   ```

## Using the Application

### 1. Upload Data
- Navigate to the "Upload Data" tab in the frontend
- Upload a policy document (text format)
- Upload comments (CSV or JSON format)

### 2. Analyze Data
- Click "Run Analysis" in the "Analyze" tab
- Wait for the analysis to complete

### 3. View Results
- Switch to the "Results" tab to see argument extraction results
- View the "Dashboard" for visualizations

## API Endpoints

### Upload Endpoints
- `POST /upload/comments/csv` - Upload comments in CSV format
- `POST /upload/comments/json` - Upload comments in JSON format
- `POST /upload/policy` - Upload policy document

### Analysis Endpoints
- `POST /analyze` - Run analysis on uploaded data

### Results Endpoints
- `GET /results/arguments` - Get all extracted arguments
- `GET /results/clause/{clause_id}` - Get analysis for a specific clause
- `GET /results/suggestions` - Get amendment suggestions

## Data Formats

### Comments CSV Format
The CSV file should have the following columns:
- `text`: The comment text
- `source`: Source of the comment
- `timestamp`: When the comment was made (ISO format)
- `policy_clause`: The clause the comment refers to

Example:
```csv
text,source,timestamp,policy_clause
"This is a sample comment",e-consultation_portal,2023-01-15T10:30:00Z,Section 3
```

### Comments JSON Format
The JSON file should be an array of objects with the following fields:
- `text`: The comment text
- `source`: Source of the comment
- `timestamp`: When the comment was made (ISO format)
- `policy_clause`: The clause the comment refers to

Example:
```json
[
  {
    "text": "This is a sample comment",
    "source": "e-consultation_portal",
    "timestamp": "2023-01-15T10:30:00Z",
    "policy_clause": "Section 3"
  }
]
```

### Policy Document Format
The policy document should be a plain text file with the policy content.

## Development

### Backend Development
The backend is built with FastAPI and is organized into modules:
- `api/`: API endpoints
- `ingestion/`: Data parsing and ingestion
- `mining/`: Argument extraction and analysis
- `citation/`: Citation management
- `fusion/`: Multi-source data fusion
- `amendment/`: Amendment suggestion generation
- `compute/`: Compute resource management
- `models/`: Data models
- `tests/`: Unit tests

### Frontend Development
The frontend is built with React and organized into:
- `components/`: Reusable UI components
- `pages/`: Main application pages
- `services/`: API service calls
- `assets/`: Static assets
- `utils/`: Utility functions

### Running Tests
```bash
cd backend
python -m pytest tests/
```

## Deployment

### Local Deployment
For small-scale or offline use, the application can run entirely locally with the quantized LLM.

### Cloud Deployment
For large-scale processing (>10,000 comments), the application can offload processing to cloud resources.

## Troubleshooting

### Common Issues
1. **Port already in use**: Change the port in the Dockerfile or docker-compose.yml
2. **Dependency installation errors**: Ensure you're using the correct Python and Node.js versions
3. **API connection errors**: Verify that both backend and frontend services are running

### Getting Help
If you encounter issues not covered in this guide, please:
1. Check the console logs for error messages
2. Verify all installation steps were completed
3. Consult the project documentation
4. Reach out to the development team