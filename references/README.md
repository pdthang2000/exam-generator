# Exam Generator

Upload a PDF and instantly get 10 multiple choice questions based on its content.

## Prerequisites

- Python 3.9+
- An API key for the AI portal

## Setup

**1. Clone the repository**

```bash
git clone <repo-url>
cd ExamGenerator
```

**2. Create a virtual environment and install dependencies**

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**3. Configure environment variables**

Copy the example env file and fill in your credentials:

```bash
cp .env.example .env
```

Open `.env` and set your values:

```
OPENAI_BASE_URL=https://aiportalapi.stu-platform.live/jpe
OPENAI_API_KEY=your-api-key-here
```

**4. Run the app**

```bash
python app.py
```

Open your browser and go to `http://localhost:8080`.

## Usage

1. Click **Choose PDF** or drag and drop a PDF file onto the upload area.
2. Click **Generate Questions** and wait a few seconds while the AI processes the document.
3. Answer the 10 multiple choice questions one by one.
4. View your score and a full answer review at the end.
