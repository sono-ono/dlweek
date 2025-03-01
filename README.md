# dlweek
Team Yurifiers' Repository for NTU Deep Learning Week 2025

# Deepfake Detection Application

A modern web application for detecting AI-generated deepfake content in images and videos.

## Features

- Upload and analyze images and videos for potential AI manipulation
- Face recognition for Singapore politicians
- Detailed analysis of authenticity and potential malicious intent
- Modern, responsive UI with Material-UI components

## Project Structure

```
├── app.py                 # Flask backend
├── mlmodel.py             # ML model integration
├── chatmodel.py           # LLM integration
├── recognition_api.py     # Face recognition API
├── frontend/              # React frontend
│   ├── public/            # Static assets
│   └── src/               # React source code
│       ├── components/    # React components
│       └── App.js         # Main React application
└── requirements.txt       # Python dependencies
```

## Prerequisites

- Python 3.8 or higher
- Node.js and npm (required for the React frontend)
  - Install from https://nodejs.org/

## Setup and Installation

### Quick Start

The easiest way to run the application is using the provided run script:

```
python run.py
```

This will:
1. Check if npm is installed
2. Install frontend dependencies if needed
3. Start both the Flask backend and React frontend
4. Open the application in your default browser

### Manual Setup

#### Backend Setup

1. Create and activate a virtual environment:
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create an `env` file with your API keys:
   ```
   hf_access_token=your_huggingface_token
   gemini_token=your_gemini_token
   test_api_url=your_recognition_api_url
   ```

4. Run the Flask backend:
   ```
   python app.py
   ```

#### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Start the development server:
   ```
   npm start
   ```

4. The application will be available at http://localhost:3000

## Usage

1. Open the application in your web browser
2. Upload an image or video file using the drag-and-drop interface or file browser
3. Wait for the analysis to complete
4. Review the detailed analysis results

## Troubleshooting

### npm not found error

If you see an error about npm not being found, you need to install Node.js and npm:

1. Download and install Node.js from https://nodejs.org/
2. Restart your terminal/command prompt
3. Run the application again

### Port already in use

If port 3000 or 5000 is already in use, you may need to:

1. Find and stop the process using that port
2. Or modify the port in the code:
   - For Flask: Change `app.run(debug=True, port=5000)` in app.py
   - For React: Create a `.env` file in the frontend directory with `PORT=3001`

## Technologies Used

- **Backend**: Flask, Python
- **Frontend**: React, Material-UI
- **AI Models**: HuggingFace, Google Gemini
- **Face Recognition**: Custom API
