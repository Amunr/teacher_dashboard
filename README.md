# Flask Backend Project

A simple Flask backend with SQL database support and CORS enabled for frontend integration.

## Setup Instructions

### 1. Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Application
```bash
python app.py
```

The server will start on `http://localhost:5000`

## Available Endpoints

- `GET /` - Main index page with available endpoints
- `GET /home` - Returns "Hello World" message
- `GET /health` - Health check endpoint

## Project Structure

```
KEF/
├── app.py              # Main Flask application
├── config.py           # Configuration settings
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── venv/              # Virtual environment (created after setup)
```

## Next Steps

1. Set up database models and migrations
2. Create frontend with charts
3. Connect frontend to backend APIs 