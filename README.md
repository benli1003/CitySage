# CitySage

A comprehensive smart city dashboard that provides real-time insights into urban infrastructure and services. CitySage combines traffic monitoring, public transit alerts, weather data, and AI-powered analytics to deliver actionable city intelligence.

## Features

### 🚦 Traffic Monitoring
- Real-time traffic detection using computer vision on Maryland DOT highway cameras
- Multi-camera support with automated vehicle counting and congestion analysis
- Live video streams from major Maryland highways (I-95, I-495, etc.)

### 🚌 Transit Intelligence
- WMATA (Washington Metro) real-time alerts and service disruptions
- Bus and rail incident monitoring
- Integration with regional transit APIs

### 🌤️ Weather Integration
- Current weather conditions and forecasts
- Weather impact analysis on transportation systems

### 🤖 AI-Powered Analytics
- Intelligent summaries of city conditions
- Pattern recognition in traffic and transit data
- Automated insights and recommendations

## Technology Stack

### Backend
- **Flask** - Python web framework
- **Computer Vision** - Real-time traffic detection and analysis
- **API Integration** - WMATA transit data, weather services
- **Multithreading** - Concurrent camera processing

### Frontend
- **React + TypeScript** - Modern web interface
- **Vite** - Fast build tooling
- **Tailwind CSS** - Utility-first styling
- **shadcn/ui** - Component library
- **Framer Motion** - Smooth animations
- **HLS.js** - Live video streaming

### Infrastructure
- **Docker** - Containerized deployment
- **AWS CloudFront** - CDN and distribution
- **Real-time Streaming** - Live camera feeds

## Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+
- WMATA API key
- Weather API key

### Installation

1. Clone the repository
2. Set up the backend:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. Set up the frontend:
   ```bash
   cd frontend
   npm install
   ```

4. Configure environment variables for API keys

### Running the Application

**Development:**
```bash
# Backend
cd backend && python app.py

# Frontend
cd frontend && npm run dev
```

**Production:**
```bash
docker-compose up
```

## Architecture

CitySage follows a microservices architecture with:
- **Traffic Detection Service** - Processes multiple camera streams simultaneously
- **Alert Scraping Service** - Monitors WMATA and other transit APIs
- **Data Aggregation** - Combines multiple data sources
- **Real-time Dashboard** - Responsive web interface

## Project Structure

```
CitySage/
├── backend/                 # Python Flask API
│   ├── traffic/            # Traffic detection system
│   │   ├── detection/      # Computer vision processing
│   │   └── config/         # Camera configurations
│   ├── scrapers/           # Data collection services
│   └── models/             # Data models
├── frontend/               # React TypeScript app
│   └── src/
│       ├── components/     # UI components
│       ├── pages/          # Application pages
│       └── hooks/          # Custom React hooks
└── docker-compose.yml      # Container orchestration
```

## Contributing

This project is part of University of Maryland research into smart city infrastructure and urban data analytics.