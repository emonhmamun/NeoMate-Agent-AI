# NeoMate AI System Architecture

## Overview

This document provides a high-level blueprint of NeoMate AI's modular architecture and data flow. It illustrates how the system's components interact to create an intelligent, responsive AI companion. The architecture emphasizes modularity, scalability, and efficiency, enabling seamless integration of new features and technologies.

## Core Architectural Philosophy

- **Modular Design**: Each component is independent, interchangeable, and reusable, allowing for easy maintenance and updates.
- **Asynchronous Processing**: Built on asyncio for non-blocking operations, ensuring responsiveness even during intensive tasks.
- **Event-Driven Model**: The system reacts to user inputs and system events, conserving resources and improving efficiency.
- **Stateful Interactions**: Maintains context and memory for coherent, personalized conversations over time.
- **Privacy-Focused**: Prioritizes local processing and secure data handling to protect user information.

## System Architecture Diagram

```mermaid
graph TD
    subgraph "User Interface & Sensory Input"
        A[🗣️ User Voice] --> B{Wake Word Detector};
        B -- Trigger --> C{Speech-to-Text Engine};
        D[🖼️ Screen View] --> E{Computer Vision Engine};
        F[🔊 System Sounds] --> G{Audio Analyzer};
    end

    subgraph "Core Logic & Brain"
        C -- Transcribed Text --> H{Cognitive Control Architecture};
        E -- Visual Context --> H;
        G -- Audio Context --> H;

        H -- Task Planning --> I[Task Planner];
        I -- Sub-tasks --> H;

        H -- Needs Intelligence --> J{LLM Brain Selector};
        J -- Online --> K[☁️ Online LLM (API)];
        J -- Offline --> L[🧠 Local LLM (Ollama)];

        K --> H;
        L --> H;
    end

    subgraph "Action & Output System"
        H -- Action Command --> M{Action Engine};
        M -- Mouse/Keyboard --> N[🖱️ OS Control];
        M -- Speech Command --> O{Text-to-Speech Engine};
        O -- Synthesized Voice --> P[📢 Speaker Output];
    end

    subgraph "Memory & Learning"
        H -- Store/Retrieve --> Q[💾 Memory System];
        Q <--> R[Short-term Memory];
        Q <--> S[Long-term Preferences];
    end

    style H fill:#f9f,stroke:#333,stroke-width:4px
```

## Module Descriptions

### Sensory Input System

This module captures environmental data from multiple sources:

- **Voice Input**: Detects wake words and converts speech to text using Whisper.cpp.
- **Visual Input**: Analyzes screen content via OpenCV for context-aware responses.
- **Audio Input**: Processes system sounds to understand background activities.

### Core Logic & Brain (Cognitive Control Architecture)

The central intelligence hub that orchestrates all operations:

- Processes inputs from sensory modules.
- Uses the Task Planner to break down complex requests into executable steps.
- Selects appropriate LLM (online or local) based on availability and requirements.
- Makes decisions on actions, responses, and memory updates.

### Action & Output System

Translates decisions into real-world effects:

- **Action Engine**: Executes commands like mouse clicks, keyboard inputs, or app launches.
- **Text-to-Speech Engine**: Generates natural voice responses using Piper TTS.
- Integrates with OS APIs for seamless control.

### Memory & Learning System

Enables adaptive behavior:

- **Short-term Memory**: Tracks current conversation context.
- **Long-term Preferences**: Stores user habits and preferences for personalization.
- Supports learning from interactions to improve future responses.

## Example Data Flow

Consider the user command: _"Open my browser and search for Python tutorials."_

1. **Input Processing**: Wake Word Detector triggers Speech-to-Text, converting voice to text.
2. **Context Analysis**: Computer Vision scans the screen for open apps; Audio Analyzer checks for background noise.
3. **Task Planning**: Cognitive Control Architecture parses the request, identifying two sub-tasks: "Open browser" and "Search for Python tutorials."
4. **Intelligence Selection**: LLM Brain Selector chooses a local model for quick response or online for advanced reasoning.
5. **Execution**: Action Engine launches the browser and performs the search via keyboard simulation.
6. **Response**: TTS Engine confirms: _"Browser opened and search completed."_
7. **Memory Update**: Stores the interaction for future reference, e.g., user's preferred browser.

## Data Flow Principles

- **Unidirectional Flow**: Data moves from input to processing to output, minimizing loops.
- **Error Handling**: Each module includes fallback mechanisms (e.g., offline mode if API fails).
- **Scalability**: Components can be scaled independently (e.g., multiple LLM instances).
- **Security**: All data flows through encrypted channels; sensitive info never leaves local storage.

## Future Extensions

- **Multi-Modal Integration**: Support for images, videos, and gestures.
- **Distributed Processing**: Cloud offloading for heavy computations.
- **Plugin System**: Allow third-party modules for custom functionalities.

---

_For implementation details, refer to the source code in `src/`. Last updated: [Date]._
