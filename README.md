<p align="center">
  <h1 align="center">🚀 Marketing Strategy Multi-Agent System</h1>
  <p align="center">
    <em>Three specialized AI agents collaborate to research your market, craft a winning strategy, and generate ready-to-use marketing content — all in one seamless pipeline.</em>
  </p>
  <p align="center">
    <img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python">
    <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License">
    <img src="https://img.shields.io/badge/framework-LangGraph-orange.svg" alt="LangGraph">
    <img src="https://img.shields.io/badge/ui-Streamlit-ff4b4b.svg" alt="Streamlit">
  </p>
</p>

---

## 📖 Table of Contents

- [✨ Features](#-features)
- [🏗️ Architecture](#-architecture)
- [🚀 Quick Start](#-quick-start)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Run the Web App](#run-the-web-app)
  - [Run the CLI](#run-the-cli)
- [🐳 Docker Deployment](#-docker-deployment)
- [📁 Project Structure](#-project-structure)
- [🔧 How It Works](#-how-it-works)
- [🌐 API Keys](#-api-keys)
- [📊 Output](#-output)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

---

## ✨ Features

- **🤖 Multi-Agent Pipeline** — Three specialized AI agents work sequentially: Market Research → Strategy Formulation → Content Creation
- **🔍 Real-Time Web Search** — The Research Agent uses Bocha Search API to gather live market data, competitor info, and industry trends
- **🎨 Modern Web UI** — Built with Streamlit, featuring a polished dark-themed sidebar, progress animations, and one-click example inputs
- **📥 Export & Download** — Results are saved as Markdown files and can be downloaded directly from the web interface
- **🐳 Docker Ready** — Includes Dockerfile and docker-compose.yml for one-command deployment
- **🔌 Multi-Model Architecture** — Each agent uses a different best-fit LLM for its task

---

## 🏗️ Architecture

```
┌─────────────┐     ┌─────────────────┐     ┌──────────────────┐
│   🔍 Market  │────▶│  🎯 Strategy    │────▶│  ✍️ Content      │
│   Research   │     │  Formulation    │     │  Creator         │
│   Agent      │     │  Agent          │     │  Agent           │
├─────────────┤     ├─────────────────┤     ├──────────────────┤
│ GLM-4 Plus  │     │ GLM-5.1         │     │ Qwen3.7-Max      │
│ + Web Search│     │ (Zhipu AI)      │     │ (Alibaba Cloud)  │
│ (Zhipu AI)  │     │                 │     │                  │
└─────────────┘     └─────────────────┘     └──────────────────┘
       │                    │                       │
       ▼                    ▼                       ▼
  Market Report      Marketing Strategy       Content Pieces
  • Target audience  • Positioning           • Social media posts
  • Competitors      • Channels              • Email templates
  • Market trends    • Messaging             • Blog topics
  • Pricing analysis • Budget & timeline     • Ad copy & more
```

The pipeline is orchestrated by **LangGraph**, with each agent passing its output to the next as structured state.

---

## 🚀 Quick Start

### Prerequisites

- Python **3.10+**
- API keys from:
  - [Zhipu AI](https://open.bigmodel.cn/) (for GLM models)
  - [Alibaba Cloud DashScope](https://dashscope.aliyuncs.com/) (for Qwen model)
  - [Bocha AI](https://open.bochaai.com/) (for web search)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/marketing-multi-agent.git
cd marketing-multi-agent

# 2. Create a virtual environment (recommended)
python -m venv .venv
# On Linux / macOS:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

### Configuration

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and fill in your API keys
```

Your `.env` file should look like:

```env
ZHIPU_API_KEY=sk-your-zhipu-api-key
DASHSCOPE_API_KEY=sk-your-dashscope-api-key
BOCHA_API_KEY=sk-your-bocha-api-key
```

| Variable | Provider | Purpose | Get Key From |
|---|---|---|---|
| `ZHIPU_API_KEY` | Zhipu AI | GLM-4 Plus & GLM-5.1 models | [open.bigmodel.cn](https://open.bigmodel.cn/) |
| `DASHSCOPE_API_KEY` | Alibaba Cloud | Qwen3.7-Max model | [dashscope.aliyun.com](https://dashscope.aliyuncs.com/) |
| `BOCHA_API_KEY` | Bocha AI | Web search capability | [open.bochaai.com](https://open.bochaai.com/) |

### Run the Web App

```bash
streamlit run app.py
```

Open your browser at **http://localhost:8501**, enter a product name, and click **Generate**. The three agents will collaborate to produce your marketing plan.

### Run the CLI

```bash
python main.py
```

This runs the pipeline on the default example product ("eco-friendly reusable water bottle") and prints the results to the terminal.

---

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

```bash
# Build and start
docker compose up -d

# View logs
docker compose logs -f

# Stop
docker compose down
```

The web app will be available at **http://localhost:8501**.

### Using Docker Directly

```bash
# Build the image
docker build -t marketing-multi-agent .

# Run the container
docker run -d \
  --name marketing-app \
  -p 8501:8501 \
  --env-file .env \
  marketing-multi-agent
```

---

## 📁 Project Structure

```
market/
├── main.py              # Core logic: LangGraph workflow, agents, state management
├── app.py               # Streamlit web UI with custom CSS
├── requirements.txt     # Python dependencies
├── Dockerfile           # Docker image definition
├── docker-compose.yml   # Docker Compose configuration
├── .env.example         # Environment variable template
├── .gitignore           # Git ignore rules
├── .dockerignore        # Docker build ignore rules
└── output/              # Generated marketing reports (Markdown)
```

---

## 🔧 How It Works

### Agent 1 — Market Research (`market_research_node`)

- **Model:** GLM-4 Plus (Zhipu AI)
- **Capability:** Tool-use with **Bocha web search**
- **Output:** Comprehensive market research report covering:
  - Target audience analysis
  - Market size and growth potential
  - Competitor landscape (strengths & weaknesses)
  - Current industry trends
  - Pricing strategies
  - Opportunities and challenges

### Agent 2 — Strategy Formulation (`strategy_node`)

- **Model:** GLM-5.1 (Zhipu AI)
- **Input:** The research report from Agent 1
- **Output:** Detailed marketing strategy including:
  - Customer segmentation
  - Value proposition & positioning
  - Marketing channel recommendations
  - Key messaging points
  - Budget considerations
  - Success metrics & timeline

### Agent 3 — Content Creator (`content_creator_node`)

- **Model:** Qwen3.7-Max (Alibaba Cloud)
- **Input:** The strategy from Agent 2
- **Output:** Ready-to-use marketing content:
  - Social media campaign outlines
  - Email marketing templates
  - Blog post topics (3+)
  - Ad copy for multiple platforms
  - Influencer collaboration ideas
  - Landing page content
  - Call-to-action suggestions

### Pipeline Orchestration

The entire workflow is built with **LangGraph**, using a directed graph:

```
START → market_research → strategy → content_creator → END
```

State is passed between agents through a typed `State` dictionary, ensuring structured data flow throughout the pipeline.

---

## 🌐 API Keys

This project uses three different LLM providers, each chosen for its strengths:

- **Zhipu AI (智谱 AI)** — Provides GLM-4 Plus (with tool-use for web search) and GLM-5.1 (for strategic reasoning). [Get API key →](https://open.bigmodel.cn/)
- **Alibaba Cloud DashScope (阿里云百炼)** — Provides Qwen3.7-Max for creative content generation. [Get API key →](https://dashscope.aliyuncs.com/)
- **Bocha AI** — Provides the web search API used by the Research Agent. [Get API key →](https://open.bochaai.com/)

> **💡 Pricing:** All three platforms offer free trial credits for new users, making it easy to test the system before committing.

---

## 📊 Output

Results are saved as Markdown files in the `output/` directory with the naming format:

```
{product-name}_{timestamp}.md
```

Example: `ai-powered-language-learning-app_20260615_212819.md`

Each file contains all three sections — research, strategy, and content — in a single, well-formatted document.

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add some amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Ideas for Contributions

- Add support for more LLM providers (OpenAI, Anthropic, etc.)
- Expand the agent pipeline with additional stages (e.g., SEO optimization, A/B testing plans)
- Add streaming output for real-time result display
- Create a Docker image for one-click cloud deployment
- Add multi-language support for international markets
- Implement result caching and comparison features

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <sub>Built with ❤️ using LangGraph, Streamlit, and Chinese AI models</sub>
</p>
