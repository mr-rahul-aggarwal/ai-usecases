# 🏥 Insurance Claims Processing Agent

An AI-powered insurance claims processing system using **LangGraph**, **RAG**, and **GPT-4o-mini** to automate claim validation, policy retrieval, and decision-making.

## 🚀 Features

- ✅ **Automated Claims Processing**: Parse, validate, and adjudicate insurance claims
- 🔍 **RAG-based Policy Retrieval**: Intelligent retrieval from policy documents using ChromaDB
- 🤖 **LangGraph Workflow**: Structured multi-step agent workflow
- 📊 **Interactive UI**: Streamlit interface for manual entry or JSON upload
- 📝 **Detailed Logging**: Complete audit trail of all agent decisions
- 🐳 **Docker Support**: Easy deployment with Docker

## 📋 Prerequisites

- An API key for the configured OpenAI-compatible endpoint
- Python 3.11 for local Python setup
- Docker Desktop for Docker on a Mac or Windows laptop

## 🛠️ Setup Options

### 1. Build and run on AWS EC2

[AWS_EC2_Deployment_Steps.md](AWS_EC2_Deployment_Steps.md) walks through creating an Ubuntu EC2 instance, building the Docker image there, and running the app.

### 2. Run with Docker on Mac or Windows

[Docker_Deployment_Guide.md](Docker_Deployment_Guide.md) explains how to run the published Docker Hub image or build an image from this repository using Docker Desktop.

### 3. Local Setup on macOS

1. **Install Python 3.11** (macOS with Homebrew):
    ```bash
    # If Homebrew is not installed, follow the instructions at https://brew.sh/
    brew install python@3.11
    python3.11 --version
    ```

2. **Clone the repository**:
    ```bash
    git clone https://github.com/mr-rahul-aggarwal/insurance-agent.git
    cd insurance-agent
    ```

3. **Create and activate a virtual environment**:
    ```bash
    python3.11 -m venv virtual_environment
    source virtual_environment/bin/activate
    ```

4. **Install dependencies**:
    ```bash
    python -m pip install --upgrade pip
    python -m pip install -r requirements.txt
    ```

    **Optional faster installer:** install `uv` once with `brew install uv`. With the virtual environment active, use this instead of the final `pip install` command above:
    ```bash
    uv pip install -r requirements.txt
    ```
    If a large download times out, retry with a longer timeout:
    ```bash
    UV_HTTP_TIMEOUT=300 uv pip install -r requirements.txt
    ```

5. **Configure Environment Variables**:
    *   Create your local `.env` file from the example:
        ```bash
        cp .env.example .env
        ```
    *   Replace `your_openai_api_key_here` with the API key for your provider. The example base URL is for the GreatLearning endpoint; keep it only if your key is for that endpoint. For the standard OpenAI API, set `OPENAI_BASE_URL=https://api.openai.com/v1`.
    *   Keep environment variable values unquoted so the same `.env` file also works with Docker's `--env-file` option.

## Running the Application

1.  **Start the Streamlit server**:
    ```bash
    streamlit run app/main.py
    ```

2.  **Access the Web Interface**:
    *   Open your web browser and go to: `http://localhost:8501`



## Usage

1.  Enter your insurance claim details manually or upload the claim details in the JSON format
2.  Click **"Process Claim"**, to check if the claim is to be Approved or Rejected.
3.  Monitor the **Logs** of the agent.
