import ollama
from langgraph.graph import StateGraph, END
from typing import TypedDict
import yfinance as yf
from datetime import datetime, timedelta, timezone

# Define agent roles
AGENT_ROLES = {
    "data_collector": "Expert in collecting financial data and historical prices",
    "financial_analyst": "CFA-certified financial analyst expert in fundamental analysis",
    "news_analyst": "Financial news analyst expert in market sentiment and NLP",
    "report_generator": "Senior investment analyst and report writer"
}

# Define system state

MODEL_NAME = "llama3.2"


class AnalysisState(TypedDict):
    stock_symbol: str
    historical_data: dict
    financials: dict
    technical_analysis: dict
    news: list
    financial_analysis: str
    news_analysis: str
    report: str

# Initialize Yahoo Finance client


def get_yfinance_data(symbol: str):
    stock = yf.Ticker(symbol)
    hist = stock.history(period="1y")
    financials = stock.financials
    news = stock.get_news(count=10000)
    return {
        "historical_data": hist.reset_index().to_dict(orient="list"),
        "financials": financials.reset_index().to_dict(orient="list") if not financials.empty else {},
        "news": news
    }

# Define agents


def data_collector(state: AnalysisState):
    """Collects financial data and news from Yahoo Finance"""
    print("Collecting data...")
    symbol = state["stock_symbol"]
    data = get_yfinance_data(symbol)
    return {
        "historical_data": data["historical_data"],
        "financials": data["financials"],
        "news": data["news"]
    }


def financial_analyst(state: AnalysisState):
    """Analyzes financial statements and valuation"""
    print("Analyzing financials...")
    messages = [
        {
            "role": "system",
            "content": f"{AGENT_ROLES['financial_analyst']}"
        },
        {
            "role": "user",
            "content": (
                f"Please provide a detailed analysis of the following financial data for {state['stock_symbol']}. "
                "Include an evaluation of profitability, liquidity, and solvency, and highlight any significant trends or red flags. "
                f"Data: {state['financials']}"
            )
        }
    ]
    response = ollama.chat(model=MODEL_NAME, messages=messages)
    return {"financial_analysis": response['message']['content']}


def news_analyst(state: AnalysisState):
    """Analyzes market news and sentiment"""
    print("Analyzing news...")
    recent_news = []
    for n in state["news"]:
        try:
            timestamp = n["content"]["pubDate"]
            publish_time = datetime.fromisoformat(timestamp)
            if publish_time > (datetime.now(timezone.utc) - timedelta(days=15)):
                filtered_n = {
                    "title": n["content"].get("title", "No Title"),
                    "publish_date": publish_time.strftime("%Y-%m-%d"),
                    "summary": n["content"].get("summary", "")
                }
                recent_news.append(filtered_n)
        except Exception as e:
            print(e)
    # Sort news by publication date (descending) and limit to 10 articles
    recent_news = sorted(
        recent_news, key=lambda x: x["publish_date"], reverse=True)[:25]

    messages = [
        {
            "role": "system",
            "content": f"{AGENT_ROLES['news_analyst']}"
        },
        {
            "role": "user",
            "content": (
                f"Please analyze the following news articles related to {state['stock_symbol']}. "
                "Provide a summary of the prevailing market sentiment, key themes, and potential impacts on the stock's performance. "
                f"News Articles: {recent_news}"
            )
        }
    ]

    response = ollama.chat(model=MODEL_NAME, messages=messages)
    return {"news_analysis": response['message']['content']}


def technical_analyst(state: AnalysisState):
    """Performs technical analysis using historical price data."""
    print("Performing technical analysis...")

    # Extract historical price data (assumes keys like "Date" and "Close" are available)
    historical_data = state.get("historical_data", {})
    dates = historical_data.get("Date", [])
    close_prices = historical_data.get("Close", [])

    # Use only a recent subset (e.g., last 30 records) to avoid overwhelming the prompt
    # if len(close_prices) > 30 and len(dates) > 30:
    #     dates_subset = dates[-30:]
    #     close_prices_subset = close_prices[-30:]
    # else:
    dates_subset = dates
    close_prices_subset = close_prices

    # Create a list of dictionaries for the data sample
    data_sample = [{"date": d, "close": c}
                   for d, c in zip(dates_subset, close_prices_subset)]

    # Construct the prompt for the technical analysis
    prompt = (
        "Based on the following historical price data (date and closing price) for the stock, "
        "please perform a detailed technical analysis. Consider the following points:\n"
        "1. Identify short-term trends and patterns.\n"
        "2. Evaluate moving averages (e.g., 10-day and 30-day, 50-day, 100-day, cl200-day) and their crossovers.\n"
        "3. Highlight potential support and resistance levels.\n"
        "4. Comment on any other technical indicators (e.g., RSI, MACD) if relevant.\n\n"
        f"Data sample: {data_sample}"
    )

    messages = [
        {
            "role": "system",
            "content": "You are an expert technical analyst specialized in chart patterns, moving averages, and technical indicators."
        },
        {
            "role": "user",
            "content": prompt
        }
    ]

    response = ollama.chat(model=MODEL_NAME, messages=messages)
    return {"technical_analysis": response['message']['content']}


def report_generator(state: AnalysisState):
    """Generates final investment report"""
    print("Generating report...")
    prompt = f"""
Stock: {state['stock_symbol']}

Financial Analysis Summary:
{state['financial_analysis']}

News Analysis Summary:
{state['news_analysis']}

Technical Analysis Summary:
{state['technical_analysis']}


Historical Price Data Snapshot (Last 90 records):
{list(zip(state['historical_data']['Date'], state['historical_data']['Close']))[-90:]}

Based on the above information, generate a comprehensive investment report that includes:
1. An overview of the company's financial health and performance trends.
2. Key takeaways from recent news and market sentiment.
3. A technical analysis of price trends, highlighting any support/resistance levels or patterns.
4. A thorough risk assessment addressing both market-wide and company-specific risks.
5. A clear investment recommendation supported by your analysis.

Ensure the report is structured, concise, and provides actionable insights.
"""
    
    print(prompt)
    messages = [
        {
            "role": "system",
            "content": f"{AGENT_ROLES['report_generator']}"
        },
        {
            "role": "user",
            "content": prompt
        }
    ]
    response = ollama.chat(model=MODEL_NAME, messages=messages)
    return {"report": response['message']['content']}


# Create workflow
workflow = StateGraph(AnalysisState)
workflow.add_node("data_collector", data_collector)
workflow.add_node("financial_analyst", financial_analyst)
workflow.add_node("news_analyst", news_analyst)
workflow.add_node("report_generator", report_generator)
workflow.add_node("technical_analyst", technical_analyst)

# Define edges
workflow.set_entry_point("data_collector")
workflow.add_edge("data_collector", "financial_analyst")
workflow.add_edge("data_collector", "news_analyst")
workflow.add_edge("data_collector", "technical_analyst")
workflow.add_edge("financial_analyst", "report_generator")
workflow.add_edge("news_analyst", "report_generator")
workflow.add_edge("technical_analyst", "report_generator")
workflow.add_edge("report_generator", END)

# Compile the graph
stock_analyzer = workflow.compile()

# Run the analysis


def analyze_stock(symbol: str):
    results = stock_analyzer.invoke({"stock_symbol": symbol})
    return results["report"]


# Example usage
if __name__ == "__main__":
    report = analyze_stock("AAPL")
    print("\nFINAL INVESTMENT REPORT:")
    print(report)
