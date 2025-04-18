Tried out OpenAI's Latest Codex CLI, and used it to build a full stack application of ChatGPT Clone, including Login, signup, and Custom Document Uploading, currently using gpt-4.1 model.

How to run it.
cd frontend
npm install
npm start


cd ../app
python -m venv env
env/Scripts/activate
pip install -r requirements.txt
uvicorn main:app
