# CapitalPilot: Multi-Agent Investment Report Generator

## Description

CapitalPilot is a Python-based project that leverages a multi-agent workflow to generate comprehensive investment reports for publicly traded companies. The tool collects financial data, news articles, and historical price information from Yahoo Finance and then employs several specialized AI agents to perform detailed analyses:

- **Data Collection:** Retrieves historical stock prices, financial statements, and news.
- **Financial Analysis:** Evaluates a company’s financial health (profitability, liquidity, and solvency) using fundamental analysis.
- **News Sentiment Analysis:** Assesses recent news articles to gauge market sentiment and identify key trends.
- **Technical Analysis:** Analyzes historical price data for trends, moving averages, and potential support/resistance levels.
- **Report Generation:** Synthesizes the analyses into a structured, actionable investment report.

The workflow is orchestrated using the LangGraph state graph framework and utilizes the Ollama AI chat model (`llama3.2`) to generate detailed textual insights at every stage.

---

## Prerequisites

- **Python 3.8+**

### Required Packages

- [ollama](https://github.com/ollama/ollama) (for AI-based chat interactions)
- [langgraph](https://github.com/langgraph/langgraph) (for building the state graph workflow)
- [yfinance](https://pypi.org/project/yfinance/) (for retrieving financial data)
- Standard libraries: `datetime`, `typing`

*Tip:* Consider using a virtual environment for dependency management.

---

## Installation

1. **Clone the Repository:**

   ```bash
   git clone https://github.com/yourusername/stock-analyzer.git
   cd stock-analyzer
   ```

2. **(Optional) Create and Activate a Virtual Environment:**

   ```bash
   python -m venv env
   source env/bin/activate  # On Windows use: env\Scripts\activate
   ```

3. **Install Dependencies:**


   ```bash
   pip install -r requirements.txt
   ```

   Otherwise, install the necessary packages individually as shown in the prerequisites.

---

## Usage

The main script, `stock_analyzer.py`, sets up the analysis workflow and executes the following steps:

1. **Data Collection:** Retrieves historical stock prices, financial statements, and news articles from Yahoo Finance.
2. **Financial Analysis:** Invokes an AI agent to provide insights into the company’s financial health.
3. **News Analysis:** Processes recent news articles to summarize market sentiment.
4. **Technical Analysis:** Examines historical price data to uncover trends and technical indicators.
5. **Report Generation:** Aggregates all analyses into a comprehensive investment report.

### Running the Analysis

To generate an investment report for a stock (e.g., Apple Inc. with ticker `AAPL`), run:

```bash
python stock_analyzer.py
```

The script will output the final investment report to the console.

---

## Contributing

Contributions, suggestions, and improvements are welcome! Please feel free to open an issue or submit a pull request if you have ideas to enhance the project.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## How It Works

1. **Agent Roles:**  
   Each agent (data collector, financial analyst, news analyst, technical analyst, and report generator) has a dedicated role with specific expertise. Their roles are defined to guide the AI model in generating focused responses.

2. **State Graph Workflow:**  
   The project uses a state graph (via the `langgraph` module) to orchestrate the sequential and parallel execution of tasks. Data flows from the initial collection phase through various analysis nodes and finally into report generation.

3. **AI Integration:**  
   The project uses the `ollama.chat` API with the `llama3.2` model to perform text-based analysis, ensuring that each part of the workflow benefits from advanced natural language processing.

4. **Financial Data Source:**  
   Yahoo Finance, accessed via the `yfinance` package, provides real-time and historical data which form the backbone of the analysis.

By combining these elements, Stock Analyzer offers a robust framework for generating insightful, data-driven investment reports.
