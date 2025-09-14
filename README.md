# Sovereign's Edict: An Actionable Intelligence Platform for Clause-Level Policy Argumentation

## Project Overview

Sovereign's Edict is a ground-truthed, scalable, and ethically robust public consultation intelligence engine. Moving beyond shallow sentiment analysis, it delivers real-time, clause-level "argument maps" and suggested policy maneuvers—giving policymakers a true X-ray of public feedback, with every insight backed by verifiable sources.

## Key Features

1. **Clause-Level Battlefield Map**: Visually shows where (which clauses/sections) the sharpest opposition or support clusters.

2. **Argument Cluster Reports**: Clearly aggregates key positive/negative arguments by theme ("privacy," "enforcement," "economic impact").

3. **Sample Comments & Citation Trails**: Provides policymakers actual sample arguments—as well as exact sources/precedents, for confidence in decisions.

4. **Counter-Offensive Generator**: Suggests precise, data-backed amendments or responses to top arguments (with traceable citations).

5. **Ethical & Robust Architecture**: 
   - No Data Biasing: No generative opinions—every recommendation is rooted in real public argument or verified expert record.
   - Inclusive & Democratic: Collects from e-governance, grassroots, and formal town hall platforms, not just social media.

## Technical Architecture

### Backend
- **Language**: Python
- **Framework**: FastAPI
- **AI/ML**: Google Gemini API for advanced argument mining, spaCy, BERTopic
- **Database**: SQLite (MVP), PostgreSQL (Production)

### Frontend
- **Default**: Streamlit (no setup required)
- **Alternative**: React/Next.js
- **Visualization**: D3.js, Chart.js, Custom Components
- **Real-time**: WebSocket connections

### Deployment
- **Local**: For small-scale/offline use
- **Hybrid**: Cloud offload for large-scale processing
- **Containerization**: Docker support

## Getting Started

### Prerequisites
- Python 3.8+
- Google Gemini API Key
- Docker (optional, for containerized deployment)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Vasanthadithya-mundrathi/Sovereign-s-Edict.git
   cd "Sovereign's Edict"
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env file to add your GEMINI_API_KEY and other required API keys
   ```

### Security Notice
**Important**: Never commit sensitive information like API keys to the repository. 
The `.env` file is included in `.gitignore` to prevent accidental exposure of credentials.
Always use `.env.example` as a template for required environment variables.

### Running the Application

#### Option 1: Default Setup (Streamlit Frontend) - Recommended
```bash
python start_streamlit.py
```

This will start both the backend (port 8001) and Streamlit frontend (port 8503) services.

#### Option 2: Using Docker
```bash
docker-compose up
```

This will start both the backend (port 8000) and frontend (port 3000) services.

#### Option 3: Manual Installation

1. Start the backend server:
   ```bash
   cd backend
   python main.py
   ```

2. In a separate terminal, start the Streamlit frontend:
   ```bash
   streamlit run streamlit_app.py
   ```

#### Option 4: React Frontend (Advanced)
1. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. Start the React frontend:
   ```bash
   npm start
   ```

#### Option 5: Gradio Frontend (Alternative)
```bash
python gradio_app.py
```

## Enhanced Features

### Advanced Argument Mining with Gemini API
The platform now uses Google's Gemini Pro model for sophisticated natural language understanding:
- Contextual argument classification (support/objection/neutral)
- Intelligent theme extraction
- Confidence scoring for analysis quality
- Citation identification and linking

### Modern Frontend Dashboard
Completely redesigned user interface with:
- Interactive clause-level heatmap visualization
- Thematic argument clustering
- Citation management panel
- Data-backed policy amendment suggestions
- Responsive design for all device sizes

### Plugin System
Sovereign's Edict now supports a modular plugin architecture:
- **YouTube Ingestor**: Ingest comments from YouTube videos using the YouTube Data API
- **Instagram Ingestor**: Ingest comments from Instagram posts using the Instagram Graph API
- **LinkedIn Ingestor**: Ingest comments from LinkedIn posts using the LinkedIn API
- **Government Database Ingestor**: Access government consultation databases
- **Scraped Data Ingestor**: Process data collected from high-scraping tools
- **Indian Legal Policy Ingestor**: Process Indian legal policy documents
- **Extensible Framework**: Create your own plugins for new data sources

For more information about the plugin system, see [Plugin Documentation](backend/plugins/README.md)

### Multiple Frontend Options
Choose the frontend that works best for your needs:
- **Streamlit (Default)**: Simple, no-setup required interface
- **React Web App**: Full-featured web application
- **Gradio**: Alternative no-setup interface

## Deployment

### Streamlit Cloud Deployment

1. Fork this repository to your GitHub account
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Create a new app and connect it to your forked repository
4. Set the main file path to `streamlit_app.py`
5. Add your API keys in the Secrets section:
   - `GEMINI_API_KEY`: Your Google Gemini API key
   - Other optional keys as needed

### Heroku Deployment

1. Install the Heroku CLI
2. Login to Heroku: `heroku login`
3. Create a new Heroku app: `heroku create your-app-name`
4. Set environment variables:
   ```bash
   heroku config:set GEMINI_API_KEY=your_gemini_api_key
   ```
5. Deploy the app: `git push heroku main`

### Docker Deployment

1. Build the Docker images:
   ```bash
   docker-compose build
   ```

2. Run the application:
   ```bash
   docker-compose up
   ```

## Development

### Running Tests

```bash
make test
```

### Code Style

- Follow PEP 8 guidelines for Python code
- Use meaningful variable and function names
- Write docstrings for all functions and classes

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Ministry of Corporate Affairs for the problem statement
- SIH 2025 organizers
- Legal experts and policy analysts who contributed to the domain knowledge
- Google for the Gemini API

## Security

The project follows strict security practices to protect sensitive information:

- Environment variables are managed through `.env` files that are excluded from version control
- All sensitive data is properly handled according to data protection regulations
- Regular security audits are conducted to identify and address vulnerabilities
- Dependencies are regularly updated to patch known security issues

For more detailed information, see [SECURITY.md](SECURITY.md).