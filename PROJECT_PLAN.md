# Sovereign's Edict - Project Plan

## Project Overview
Sovereign's Edict is a ground-truthed, scalable, and ethically robust public consultation intelligence engine that delivers real-time, clause-level "argument maps" and suggested policy maneuvers.

## Key Components & Requirements

### 1. Backend Architecture
**Technology Stack:**
- Python (core pipeline)
- FastAPI server for REST & websocket real-time updates
- SQLite/JSON for initial data storage
- spaCy for text analytics
- UMAP or BERTopic for clustering

**Core Modules:**
- Data Ingestion Layer
- Argument Mining Core
- Citation Oracle
- Multi-Source Fusion Engine
- Amendment/Counter-Response Generator
- Edge-to-Cloud Compute Ladder

### 2. AI/ML Components
**LLM Requirements:**
- Quantized llama.cpp or GGUF model (8-bit for RAM efficiency, 4-bit with GPU)
- Cloud option: OpenAI, Gemini, Azure, or self-hosted Mistral
- Local processing for privacy and speed
- Cloud offload for large-scale processing (>10k comments)

**NLP Processing:**
- Text normalization and tokenization
- Section/clause mapping
- Argument extraction
- Theme and clause mapping
- Citation linking

### 3. Frontend Dashboard
**Technology Stack:**
- React/Next.js for interactivity
- D3.js or Chart.js for visualizations
- Real-time updates via WebSocket

**Key Features:**
- Clause-level battlefield map (heatmap)
- Argument cluster reports
- Citation trails and sample comments
- Counter-offensive generator
- Downloadable action briefs

### 4. Data Management
**Data Sources:**
- CSV/JSON comments
- Legal PDF/text corpora
- Mock e-consultation feeds
- Government portal data
- Social media aggregation (anonymized)

**Storage:**
- SQLite/JSON for MVP
- PostgreSQL for production
- Legal citation database

### 5. Deployment Architecture
**Compute Options:**
- Local (laptop) for small-scale analysis
- Hybrid (cloud for large-scale)
- Edge-to-cloud compute ladder

**Deployment Targets:**
- Rural collectorates (offline capability)
- Ministry-level analysis (cloud-scale)
- Parliamentary use (high-performance)

## Implementation Timeline

### Phase 1: MVP Build (7-10 days)
1. Backend core pipeline
2. Basic argument mining engine
3. Simple frontend dashboard
4. Synthetic demo data

### Phase 2: Enhanced Features (3-5 days)
1. Database of citations
2. Multi-source data fusion
3. Validation scripts
4. Improved visualizations

### Phase 3: Polish & Documentation (2-3 days)
1. Demo refinement
2. Documentation
3. Testing and bug fixes

## Technical Requirements

### Development Environment
- Python 3.8+
- Node.js 16+
- Git for version control
- Docker (for containerization)

### Python Dependencies
- FastAPI
- spaCy
- Transformers (Hugging Face)
- llama.cpp (Python bindings)
- UMAP/BERTopic
- SQLite3
- Pandas, NumPy
- WebSocket support

### Frontend Dependencies
- React/Next.js
- D3.js/Chart.js
- WebSocket client
- TailwindCSS or MaterialUI

## Team Roles & Responsibilities

1. **NLP/AI Engineer**
   - LLM fine-tuning
   - Argument/citation mining
   - Text processing pipeline

2. **Backend Developer**
   - API development
   - Data processing pipeline
   - Cloud integration

3. **Frontend Developer**
   - Dashboard development
   - Visualization implementation
   - UX design

4. **Domain Curator**
   - Sample policies
   - Legal databases
   - Scenario data

5. **Demo Lead**
   - Demo scripts
   - Presentation materials
   - Judge interaction

## Risk Mitigation Strategies

1. **AI Hallucination**
   - All output requires citation
   - "NO CITATION, NO SUGGESTION" principle

2. **Scale Management**
   - Automatic routing of heavy jobs to cloud
   - Lightweight processing for small districts

3. **Bias Prevention**
   - Multi-source fusion
   - Explicit citation requirements
   - Cross-validation of arguments

## Success Criteria

1. Clause-level intelligence (not just sentiment)
2. Ground-truthed AI (no hallucinations)
3. Scalable from village to national level
4. Visually impressive demo
5. Actionable insights for policymakers