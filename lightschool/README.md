# LightSchool

Offline K-5 Learning PWA for Math and English (Grades 1-3).

## What is LightSchool?

LightSchool is a progressive web app (PWA) designed for offline learning. It provides interactive lessons and quizzes in Math and English for grades 1-3, with support for English and Spanish languages. The app caches all content locally, allowing it to work without an internet connection after the initial load.

## Features

- **Offline-First**: Fully functional without internet after first load.
- **Bilingual**: Switch between English and Spanish instantly.
- **Progress Tracking**: Session-based progress with stars and scores.
- **AI Tutor**: Local AI assistance via Ollama (with offline fallback).
- **PWA**: Installable on mobile and desktop.

## Setup

### Prerequisites

- Python 3.10+
- (Optional) Ollama for AI tutor

### Installation

1. Clone or download the project.
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run migrations (if any):
   ```bash
   python manage.py migrate
   ```
5. Collect static files:
   ```bash
   python manage.py collectstatic --noinput
   ```

### Optional: Ollama Setup

1. Install Ollama: `brew install ollama` (macOS)
2. Pull the model: `ollama pull deepseek-r1:1.5b`
3. Start Ollama: `ollama serve`

## Running the App

```bash
python manage.py runserver 0.0.0.0:8000
```

Open `http://localhost:8000` in your browser.

## PWA Installation

- On mobile: Tap "Install App" when prompted.
- On desktop: Use the install button in the address bar (Chrome).

## Demo Script

1. Open the app with Wi-Fi on.
2. Choose Math → Grade 1.
3. View the "Addition Basics" lesson cards.
4. Take the quiz and see your score.
5. Turn off Wi-Fi and reload the page – it should still work.
6. Switch language to Spanish and see content update.
7. Ask the AI tutor a question.

## Development

- Run tests: `python manage.py test`
- Add translations: Use `makemessages` and `compilemessages` for UI labels.

## License

Open source. Use free assets from Google Noto and open emoji.