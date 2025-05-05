# Nu - Jewish Texts Explorer

A web application for exploring Jewish texts and Chassidic philosophy using AI-powered search and analysis.

## Features

- Interactive chat interface for asking questions about Jewish texts
- AI-powered text analysis using Google's Gemini model
- Support for multiple Jewish text sources
- Proper Hebrew text formatting and transliteration
- Detailed citations and source references

## Project Structure

```
project/
├── app.py              # Flask application
├── main.py             # Original command-line script
├── templates/          # HTML templates
│   └── index.html      # Main page template
├── static/             # Static assets
│   ├── css/
│   │   └── style.css   # Styling
│   └── js/
│       └── script.js   # Frontend functionality
└── txt/                # Text files (not included in repo)
    └── Chasidut/
        └── Chabad/     # Chabad texts
```

## Setup

1. Clone the repository:
```bash
git clone https://github.com/elyhahami18/nu.git
cd nu
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory and add your Gemini API key:
```
GEMINI_API_KEY=your_api_key_here
```

4. Run the application:
```bash
python app.py
```

The application will be available at http://localhost:8080

## Requirements

- Python 3.7+
- Flask
- Google GenerativeAI Python SDK
- tiktoken
- python-dotenv

## Supported Text Sources

- Tanya
- Torah Ohr
- The Gate of Unity
- Derekh Mitzvotekha/Hebrew
- Likkutei Torah

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Google Gemini AI for powering the responses
- Flask for the web framework
- The Chassidic texts and their authors 