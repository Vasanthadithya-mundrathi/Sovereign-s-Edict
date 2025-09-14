# Sovereign's Edict: An Actionable Intelligence Platform for Clause-Level Policy Argumentation

## Project Overview

Sovereign's Edict is a ground-truthed, scalable, and ethically robust public consultation intelligence engine. Moving beyond shallow sentiment analysis, it delivers real-time, clause-level "argument maps" and suggested policy maneuvers—giving policymakers a true X-ray of public feedback, with every insight backed by verifiable sources.

## Problem Statement

Ministries face thousands of comments on proposed laws but lack tools for extracting actionable intelligence. Mere "sentiment" is useless; real decision-making needs to know the why, where, and how behind opposition and support.

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
- **Framework**: React/Next.js
- **Visualization**: D3.js, Chart.js, Custom Components
- **Real-time**: WebSocket connections

### Deployment
- **Local**: For small-scale/offline use
- **Hybrid**: Cloud offload for large-scale processing
- **Containerization**: Docker support

## Directory Structure

```
Sovereign's Edict/
├── backend/
│   ├── api/          # API endpoints
│   ├── ingestion/    # Data ingestion modules
│   ├── mining/       # Argument mining core with Gemini API integration
│   ├── citation/     # Citation oracle
│   ├── fusion/       # Multi-source fusion engine
│   ├── amendment/    # Amendment generator
│   ├── compute/      # Compute management
│   ├── models/       # Data models
│   ├── utils/        # Utility functions
│   └── tests/        # Unit tests
├── frontend/
│   ├── components/   # React visualization components
│   ├── pages/        # Page components
│   ├── assets/       # Static assets
│   ├── services/     # API services
│   ├── utils/        # Utility functions
│   └── tests/        # Unit tests
├── data/             # Sample data and datasets
├── models/           # AI/ML models
├── docs/             # Documentation
├── requirements.txt  # Python dependencies
├── PROJECT_PLAN.md   # Project plan
└── TECHNICAL_SPEC.md # Technical specification
```

## Getting Started

### Prerequisites
- Python 3.8+
- Node.js 16+
- Google Gemini API Key
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

3. Set up Gemini API key:
   ```bash
   export GEMINI_API_KEY="your-api-key-here"
   ```

4. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   ```

### Running the Application

#### Option 1: Using Docker (Recommended)
```bash
docker-compose up
```

This will start both the backend (port 8000) and frontend (port 3000) services.

#### Option 2: Manual Installation

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

## Development Roadmap

### Phase 1: MVP (Completed)
- Backend core pipeline with Gemini integration
- Advanced argument mining engine
- Enhanced frontend dashboard with visualizations
- Synthetic demo data

### Phase 2: Enhanced Features (In Progress)
- Database of citations
- Multi-source data fusion
- Validation scripts
- Improved visualizations

### Phase 3: Polish & Documentation
- Demo refinement
- Documentation
- Testing and bug fixes

## Team Roles

1. **NLP/AI Engineer**: LLM fine-tuning, argument/citation mining
2. **Backend Dev**: API, data processing pipeline
3. **Frontend Dev**: Dashboard, visualization/UX
4. **Domain Curator**: Sample policies, legal databases, scenario data
5. **Demo Lead**: Scripts, scenario walkthrough, judge interaction

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Acknowledgments

- Ministry of Corporate Affairs for the problem statement
- SIH 2025 organizers
- Legal experts and policy analysts who contributed to the domain knowledge
- Google for the Gemini API