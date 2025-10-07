# NeoMate AI: Technical Specifications

## Table of Contents

- [System Requirements](#system-requirements)
- [Installation Guide](#installation-guide)
- [Core Dependencies & Versions](#core-dependencies--versions)
- [External APIs & Endpoints](#external-apis--endpoints)
- [Configuration Options](#configuration-options)
- [Supported Models](#supported-models)
- [Network Requirements](#network-requirements)
- [Security Considerations](#security-considerations)
- [Performance Benchmarks](#performance-benchmarks)
- [Data Privacy](#data-privacy)
- [Compatibility Notes](#compatibility-notes)
- [Troubleshooting](#troubleshooting)
- [Changelog](#changelog)

## System Requirements

### Operating System

- **Minimum**: Windows 10/11 (64-bit), Ubuntu 20.04+ (64-bit), macOS 11+ (Big Sur)
- **Recommended**: Windows 11 (64-bit), Ubuntu 22.04+ (64-bit), macOS 12+ (Monterey)

### Processor (CPU)

- **Minimum**: 4-core CPU (e.g., Intel Core i5, AMD Ryzen 5)
- **Recommended**: 8-core CPU (e.g., Intel Core i7, AMD Ryzen 7)

### Memory (RAM)

- **Minimum**: 8 GB RAM (for online LLM usage)
- **Recommended**: 16 GB RAM (32 GB preferred for local LLM models)

### Graphics Card (GPU)

- **Minimum**: Optional; improves performance for Whisper.cpp and local LLMs
- **Recommended**: NVIDIA GPU with 8 GB+ VRAM (CUDA support required)

### Storage

- **Minimum**: 10 GB free space (application and basic models)
- **Recommended**: 50 GB+ free space (multiple local LLM models)

### Software

- **Python**: 3.10+
- **Git**: Latest stable version
- **Optional**: Conda, Docker

## Installation Guide

1. **Clone Repository**:

   ```bash
   git clone https://github.com/emonhmamun/NeoMate-AI.git
   cd NeoMate-AI
   ```

2. **Install Dependencies**:

   - Using Pip:
     ```bash
     pip install -r requirements.txt
     ```
   - Using Poetry:
     ```bash
     poetry install
     ```
   - Using Conda:
     ```bash
     conda env create -f environment.yml
     ```

3. **Run Application**:

   ```bash
   python src/main.py
   ```

4. **Optional: Install Ollama for Local LLMs**:
   ```bash
   # Download from https://ollama.ai/
   ollama pull llama2
   ```

## Core Dependencies & Versions

| Dependency    | Version       | Purpose              |
| ------------- | ------------- | -------------------- |
| Python        | ^3.10         | Core runtime         |
| PyQt6         | ^6.6          | GUI framework        |
| OpenCV-Python | ^4.9          | Computer vision      |
| Whisper.cpp   | Latest stable | Speech-to-text       |
| Piper TTS     | Latest stable | Text-to-speech       |
| Ollama        | Latest        | Local LLM management |
| LangChain     | ^0.1          | LLM integration      |
| PyTorch       | ^2.0          | Machine learning     |
| NumPy         | ^1.24         | Numerical computing  |
| Requests      | ^2.31         | HTTP client          |
| FastAPI       | ^0.104        | API framework        |
| Uvicorn       | ^0.24         | ASGI server          |

## External APIs & Endpoints

### LLM Providers

- **OpenRouter**: [https://openrouter.ai/docs](https://openrouter.ai/docs)
- **GroqCloud**: [https://console.groq.com/docs](https://console.groq.com/docs)
- **OpenAI**: [https://platform.openai.com/docs/api-reference](https://platform.openai.com/docs/api-reference)
- **DeepSeek AI**: [https://platform.deepseek.com/api-docs](https://platform.deepseek.com/api-docs)

### Search Providers

- **Brave Search API**: [https://brave.com/search/api/](https://brave.com/search/api/)
- **SearXNG**: Self-hosted; refer to [official docs](https://docs.searxng.org/)

## Configuration Options

- **Environment Variables**:

  - `OPENAI_API_KEY`: For OpenAI integration
  - `GROQ_API_KEY`: For GroqCloud
  - `OLLAMA_HOST`: Local Ollama server URL

- **Config File**: `config/settings.json` for UI preferences and model settings.

## Supported Models

- **Local LLMs**: Llama 2, Mistral, Phi-2 via Ollama
- **Online LLMs**: GPT-4, Claude, Gemini via APIs
- **Speech Models**: Whisper (multiple languages)
- **TTS Models**: Piper (various voices)

## Network Requirements

- **Core Functionality**: Runs offline.
- **Online Features**: Stable internet connection required for online LLMs, search, and self-updates.
- **Bandwidth**: Minimum 1 Mbps for basic usage; 10 Mbps+ recommended for streaming responses.

## Security Considerations

- All API keys stored securely using environment variables.
- No sensitive data logged or transmitted without encryption.
- Regular dependency updates to address vulnerabilities.
- Local data processing to minimize external exposure.

## Performance Benchmarks

- **Local LLM Inference**: ~5-10 tokens/sec on recommended hardware.
- **Speech Processing**: Real-time on GPU; ~2x slower on CPU.
- **GUI Responsiveness**: <100ms latency for user interactions.
- **Startup Time**: <5 seconds on SSD.

## Data Privacy

- User data processed locally where possible.
- Online queries anonymized.
- No data collection without consent.
- Compliant with GDPR and CCPA standards.

## Compatibility Notes

- Tested on specified OS versions; may work on others but not guaranteed.
- CUDA required for GPU acceleration on NVIDIA cards.
- Docker support for containerized deployment.

## Troubleshooting

- **Common Issues**:

  - GPU not detected: Ensure CUDA drivers installed.
  - Model download fails: Check internet and storage.
  - API errors: Verify keys and endpoints.

- **Logs**: Check `logs/` directory for error details.

## Changelog

- **v1.0.0**: Initial release with core features.
- **v1.1.0**: Added local LLM support.

---

_Last updated: [Date]. For latest versions, check pyproject.toml. Contact: maintainers@neomate.ai_
