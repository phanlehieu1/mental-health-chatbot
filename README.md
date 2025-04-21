# Mental Health Chatbot with RAG

A conversational AI system designed to provide mental health support using Retrieval-Augmented Generation (RAG) technology. The chatbot retrieves relevant mental health information from a knowledge base to provide accurate, context-aware responses.

## Features
- Interactive chat interface
- Real-time response generation
- Document retrieval system for accurate information
- Streaming response option for better user experience

## Technologies
- **Backend**: FastAPI, Python
- **Frontend**: React
- **NLP**: Embedding models for semantic search
- **Data Processing**: Custom document processor

## Installation

### Prerequisites
- Python 3.8+
- Node.js and npm

### Setup
1. **Clone the repository**:
   ```bash
   git clone https://github.com/your-repo/mental-health-chatbot.git
   cd mental-health-chatbot
   ```

2. **Set up the backend**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up the frontend**:
   ```bash
   cd frontend
   npm install
   ```

## Running the Application

### Backend Server
Start the FastAPI server:
```bash
cd backend
uvicorn main:app --reload
```
The backend will be available at `http://localhost:8000`.

### Frontend Application
Run the React frontend:
```bash
cd frontend
npm start
```
The frontend will be available at `http://localhost:3000`.

### Document Processor
To process and update the knowledge base documents:
```bash
cd backend
python document_processor.py
```
This script processes mental health documents and updates embeddings in `backend/data/`.

## Project Structure
- `backend/`: FastAPI server, embedding services, and retrieval logic
- `frontend/`: React-based user interface
- `backend/data/`: Storage for mental health documents and embeddings

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.