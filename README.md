# youtube-automation


# 🎬 Automated News Video Generator

An autonomous system that scrapes trending topics, gathers news data, generates engaging video content, and publishes it to YouTube - all without human intervention.

## 🔍 Overview

This project creates a fully automated pipeline that:
1. Monitors trending topics and current events
2. Collects relevant news data
3. Generates scripts and image prompts using AI
4. Creates audio narration via text-to-speech
5. Generates images from prompts
6. Compiles everything into video content
7. Publishes the finished videos to YouTube

The entire workflow runs on a scheduled basis (hourly) with a supervisor agent orchestrating all components.

## 🏗️ Architecture

![System Architecture Diagram](architecture-diagram.png)

The system follows a distributed architecture with the following components:

### External Trigger
- **Cron Job**: Initiates the workflow on an hourly schedule

### Orchestration & State
- **Master Agent (LangGraph)**: Coordinates all worker components and maintains workflow state

### Data Acquisition Workers
- **Trends Scraping Agent**: Uses Selenium to gather trending topics
- **News Collector Agent**: Leverages Event Registry API to fetch relevant news data

### Content Generation Workers
- **Script & Image Prompt Generator**: Uses DeepSeek R1 (via Groq) to create video scripts and image prompts
- **Text-to-Speech Agent**: Converts script to spoken audio via Google TTS
- **Image Generation Agent**: Creates visual content using Polynation API

### Video Production
- **Video Editing Tool**: MoviePy-based component that assembles audio, images, and music

### Distribution
- **YouTube Uploading Agent**: Handles publishing via YouTube API

### Shared Resources
- **File System / Temp Storage**: Stores intermediary and final assets
- **Background Music Source**: Provides audio tracks for videos

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Docker (optional, for containerized deployment)
- API keys for:
  - Event Registry
  - Groq (for DeepSeek)
  - Google TTS
  - Polynation
  - YouTube API

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/automated-news-video-generator.git
cd automated-news-video-generator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a configuration file:
```bash
cp config.example.yaml config.yaml
```

4. Edit `config.yaml` with your API keys and preferences

### Running the System

#### Local Development
```bash
python run_supervisor.py
```

#### Production Deployment
```bash
docker-compose up -d
```

## 📂 Project Structure

```
.
├── config/                  # Configuration files
├── data/                    # Temporary data storage
├── logs/                    # Log files
├── src/
│   ├── agents/              # Agent implementations
│   │   ├── master.py        # Supervisor agent (LangGraph)
│   │   ├── trends.py        # Trends scraping agent
│   │   ├── news.py          # News collection agent
│   │   ├── script_gen.py    # Script/prompt generation agent
│   │   ├── tts.py           # Text-to-speech agent
│   │   ├── image_gen.py     # Image generation agent
│   │   └── youtube.py       # YouTube upload agent
│   ├── tools/
│   │   ├── video_editor.py  # MoviePy video assembly
│   │   └── file_manager.py  # File system management
│   └── utils/               # Helper functions and utilities
├── tests/                   # Unit and integration tests
├── Dockerfile               # Docker container definition
├── docker-compose.yml       # Multi-container orchestration
├── requirements.txt         # Python dependencies
└── run_supervisor.py        # Entry point script
```

## ⚙️ Configuration

The `config.yaml` file allows you to customize:

- API credentials
- Content preferences
- Video style settings
- Publishing schedule
- Background music options
- Temporary file management

## 🔧 Troubleshooting

Common issues and solutions:

- **API Rate Limiting**: Implement exponential backoff in the relevant agent
- **Disk Space Concerns**: Configure automatic cleanup of temporary files
- **Failed Video Generation**: Check logs in `logs/video_editor.log`
- **YouTube Upload Issues**: Verify API quota and authentication

## 📝 Logging

Logs are stored in the `logs/` directory with different files for each component:
- `master.log` - Supervisor agent activities
- `data_acquisition.log` - Trends and news collection
- `content_generation.log` - Script, audio, and image generation
- `video_editor.log` - Video assembly process
- `youtube.log` - YouTube uploading

## 🛣️ Roadmap

- [ ] Add more trend sources
- [ ] Implement more sophisticated video templates
- [ ] Add support for multiple languages
- [ ] Create a web dashboard for monitoring
- [ ] Add multi-platform publishing (TikTok, Instagram, etc.)

## 🤝 Contributing

Contributions are welcome! Please check out our [contribution guidelines](CONTRIBUTING.md).

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgements

- [LangGraph](https://github.com/langchain-ai/langgraph) for the agent orchestration framework
- [Event Registry](https://eventregistry.org/) for news data
- [Groq](https://groq.com/) for fast LLM inference
- [Polynation](https://polynation.ai/) for image generation
- [MoviePy](https://zulko.github.io/moviepy/) for video editing capabilities

