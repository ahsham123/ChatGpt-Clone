# ChatGPT Clone

A full-stack application that clones ChatGPT functionality, including login, signup, and custom document uploading. Currently using the GPT-4.1 model from OpenAI.

## Features

- User authentication (login/signup)
- Chat interface similar to ChatGPT
- Custom document uploading
- Integration with OpenAI's GPT-4.1 model

## Setup Instructions

### Frontend

```bash
cd frontend
npm install
npm start
```

### Backend

```bash
cd app
python -m venv env
env\Scripts\activate  # Windows
# Or source env/bin/activate for Unix/MacOS
pip install -r requirements.txt
uvicorn main:app --reload
```

## Technologies Used

- Frontend: React.js
- Backend: FastAPI (Python)
- AI: OpenAI GPT-4.1 API
