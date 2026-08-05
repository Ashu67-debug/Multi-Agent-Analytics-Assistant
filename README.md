# 🤖 Multi-Agent Analytics Assistant

A **Multi-Agent AI Analytics System** built using **CrewAI, Ollama, MCP (Model Context Protocol), and Streamlit**. The application accepts a natural language analytics request, intelligently assigns work to specialized AI agents, and generates actionable insights using local tools and an MCP server.

---

## 📌 Overview

This project demonstrates how multiple AI agents can collaborate to solve complex analytics problems.

The system consists of three specialized agents:

- **Supervisor Agent**
  - Understands the user's request
  - Creates an execution plan
  - Delegates work to other agents
  - Combines the final response

- **Data Analyst Agent**
  - Performs SQL analysis
  - Generates KPIs
  - Profiles datasets
  - Creates dashboard suggestions
  - Performs exploratory data analysis

- **Data Scientist Agent**
  - Recommends ML solutions
  - Suggests feature engineering
  - Detects ML risks
  - Creates ML pipeline plans
  - Recommends evaluation metrics

All agents communicate through **CrewAI's Hierarchical Process** while using both **local Function Tools** and **MCP Server Tools**.

---

# 🚀 Features

- ✅ Multi-Agent Architecture
- ✅ CrewAI Hierarchical Workflow
- ✅ Local Ollama LLM Support
- ✅ Streamlit Chat Interface
- ✅ MCP (Model Context Protocol) Integration
- ✅ SQL Validation
- ✅ Data Quality Analysis
- ✅ KPI Generation
- ✅ Machine Learning Recommendations
- ✅ Dashboard Suggestions
- ✅ CSV Profiling
- ✅ Automated Report Generation
- ✅ Activity Timeline
- ✅ Delegation Trace
- ✅ Context Usage Monitoring
- ✅ Security Guardrails
- ✅ Automated Unit Tests

---

# 🏗️ System Architecture

```
                    User
                      │
                      ▼
             Streamlit Web Interface
                      │
                      ▼
            Supervisor Agent (CrewAI)
                      │
          ┌───────────┴───────────┐
          ▼                       ▼
 Data Analyst Agent      Data Scientist Agent
          │                       │
          └───────────┬───────────┘
                      ▼
           Function Tools + MCP Tools
                      │
                      ▼
              Final AI Response
```

---

# 📂 Project Structure

```
Multi-Agent-Analytics-Assistant/
│
├── agents/
│   ├── supervisor_agent.py
│   ├── data_analyst_agent.py
│   └── data_scientist_agent.py
│
├── config/
│   ├── agents.yaml
│   └── tasks.yaml
│
├── docs/
│   ├── architecture.md
│   ├── demo_script.md
│   └── mcp_tool_catalog.md
│
├── function_tools/
│   ├── analyst_tools.py
│   ├── scientist_tools.py
│   └── supervisor_tools.py
│
├── mcp_server/
│   ├── server.py
│   ├── client_tools.py
│   ├── sample_data/
│   └── tools/
│
├── tests/
│
├── app.py
├── requirements.txt
└── README.md
```

---

# ⚙️ Technologies Used

- Python
- CrewAI
- Ollama
- Streamlit
- MCP (Model Context Protocol)
- DuckDB
- Pandas
- Polars
- NumPy
- Scikit-Learn
- SQLGlot
- SQLParse
- Plotly
- Matplotlib
- PyYAML
- Pytest

---

# 🧠 AI Agents

## 1. Supervisor Agent

Responsibilities:

- Understand user requests
- Classify analytics tasks
- Create execution plans
- Delegate work
- Merge responses
- Validate output quality

### Local Tools

- classify_user_request()
- create_agent_work_plan()
- summarize_chat_history()
- validate_final_response_structure()
- estimate_context_usage()

---

## 2. Data Analyst Agent

Responsibilities:

- SQL Analysis
- KPI Generation
- Data Profiling
- Dashboard Suggestions
- Business Analytics

### Local Tools

- profile_dataframe()
- suggest_kpi_metrics()
- generate_dashboard_layout()
- validate_sql_safety()
- explain_query_result()

---

## 3. Data Scientist Agent

Responsibilities:

- Machine Learning Planning
- Feature Engineering
- Model Recommendations
- Risk Detection
- Pipeline Design

### Local Tools

- recommend_ml_problem_type()
- suggest_feature_engineering()
- detect_ml_data_risks()
- recommend_evaluation_metrics()
- create_ml_pipeline_plan()

---

# 🔧 MCP Server

The project includes a local MCP server that exposes reusable analytics tools.

Available MCP Tools:

- CSV Profiling
- SQL Execution
- SQL Validation
- Data Quality Detection
- KPI Catalog Generation
- ML Use Case Recommendation
- Feature Engineering Suggestions
- Anomaly Detection
- Data Dictionary Generation
- Markdown Report Generation

---

# 🖥️ Streamlit Dashboard

The application provides an interactive dashboard with:

- Chat Interface
- Activity Timeline
- Delegation Trace
- Context Usage
- Agent Information
- Tool Information
- Model Details

---

# 🛡️ Security Features

- SQL Allow-list Validation
- File Sandbox Protection
- Safe File Extensions
- File Size Limits
- Protected Sample Data Access
- Error Handling without Stack Traces

---

# 📊 Sample Data

The project includes sample datasets for testing:

- Customers Dataset
- Transactions Dataset
- Events Dataset

---

# ▶️ Installation

## Clone Repository

```bash
git clone https://github.com/yourusername/multi-agent-analytics-assistant.git
```

```bash
cd multi-agent-analytics-assistant
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Install Ollama

Download:

https://ollama.com

Pull the required model:

```bash
ollama pull llama3.1
```

---

## Run the Application

```bash
streamlit run app.py
```

The application will open in your browser.

---

# 💬 Example Prompt

```
Design a real-time analytics platform on BigQuery that ingests 1 TB/day of event data, keeps data quality high, and stays cost-efficient.
```

The Supervisor Agent automatically delegates tasks to the Analyst and Data Scientist agents and produces a combined response.

---

# 🧪 Testing

Run all unit tests using:

```bash
pytest
```

The project contains tests for:

- Function Tools
- MCP Server Tools
- Analyst Tools
- Scientist Tools
- Supervisor Tools

---

# 📚 Learning Outcomes

This project demonstrates:

- Multi-Agent AI Systems
- CrewAI Orchestration
- MCP Integration
- AI Agent Collaboration
- Data Analytics Automation
- Machine Learning Planning
- Tool Calling
- Streamlit Application Development
- Local LLM Deployment with Ollama

---

# 📈 Future Improvements

- Support for multiple LLM providers
- Cloud database integration
- Authentication system
- Real-time streaming analytics
- RAG with vector databases
- Data visualization dashboards
- Agent memory
- Report export (PDF/Excel)
- Docker deployment
- Kubernetes support

---

# 👨‍💻 Author

**Ashutosh Gupta**

B.Tech – Electronics & Communication Engineering

Birla Institute of Technology, Mesra (Patna Campus)

GitHub: https://github.com/Ashu67-debug

---

# ⭐ Acknowledgements

- CrewAI
- Ollama
- Streamlit
- Model Context Protocol (MCP)
- DuckDB
- Open Source Python Community

---

## License

This project is developed for educational and learning purposes.
