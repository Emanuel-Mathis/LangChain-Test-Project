## Project Structure

- `app/`: Main Python application.
- `Dockerfile`: Instructions for building the Docker image.
- `requirements.txt`: Python dependencies.
- `build.py` and `run.py`: Python scripts for building and running the Docker image.
- `.env`: Environment variables loaded at runtime, including the OpenAI API key.

## Setting Up and Running the Project

1. Clone the repository.
2. Install Docker.
3. Create a `.env` file with your OpenAI API & Firebase Keys (eg. `OPENAI_API_KEY=your-openai-api-key`).
4. Install Python dependencies (`pip install -r requirements.txt`).
5. Build the Docker image (`python build.py`).
6. Run the application (`python run.py`).

The application runs inside a Docker container on port 5567.

## API Endpoints

1. `POST /v1/quiz` - This endpoint takes a query to generate a quiz and responds with multiple MCQs.

