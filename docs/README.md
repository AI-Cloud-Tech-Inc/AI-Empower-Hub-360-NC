# AI Empower Hub 360

Empower Hub 360 NC serves startups, entrepreneurs, and growing businesses seeking practical AI solutions to automate operations, scale faster, and innovate affordably.

## Our Focus

We specialize in four core service areas for startup and SMB clients:

1. **AI Virtual Assistants & Chatbots** - Custom conversational AI for customer service and business operations
2. **Workflow Automation** - AI-powered automation to streamline SMB operations
3. **Cloud AI Deployment** - GPU computing and enterprise platform integration
4. **AI Strategy Consulting** - Adoption guidance, model selection, and staff training

## Project Structure

```
ai-empower-hub-360/
├── src/                    # Source code
│   ├── api/               # API endpoints
│   ├── models/            # Data models
│   ├── services/          # Business logic
│   ├── utils/             # Utility functions
│   ├── core/              # Core functionality
│   └── main.py            # Application entry point
├── tests/                 # Test files
│   ├── unit/              # Unit tests
│   └── integration/       # Integration tests
├── config/                # Configuration files
├── docs/                  # Documentation
├── scripts/               # Utility scripts
├── data/                  # Data files
├── requirements.txt       # Python dependencies
└── pyproject.toml         # Project configuration
```

## Installation

1. Clone the repository:

```bash
git clone https://github.com/aicloudtech/ai-empower-hub-360.git
cd ai-empower-hub-360
```

1. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

1. Install dependencies:

```bash
pip install -r requirements.txt
```

1. Configure environment:

```bash
cp .env.example .env
# Edit .env with your configuration
```

1. Run the application:

```bash
python -m src.main
```

## Development

Run tests:

```bash
pytest
```

Run with coverage:

```bash
pytest --cov=src
```

## License

MIT License - see [LICENSE](../LICENSE) for details.
