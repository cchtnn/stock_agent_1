from crewai import Agent, Task, Crew, Process
from crewai.tasks import TaskOutput 
from crewai_tools import WebsiteSearchTool, ScrapeWebsiteTool
from crewai import LLM
from custom_tools import fetch_stock_data, fetch_stock_financials, fetch_stock_news
import os

# Initialize tools
search_tool = WebsiteSearchTool()
scrape_tool = ScrapeWebsiteTool()

# Create LLM instance with Groq configuration
llm = LLM(
    model="groq/llama3-8b-8192",
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
    temperature=0.1,
    max_tokens=2048
)

# Data collection agent - Use custom tools instead of problematic web tools
data_collector = Agent(
    role="Stock Data Collector",
    goal="Efficiently gather stock market data for financial analysis using available data sources.",
    backstory=("A reliable financial data collector who specializes in extracting comprehensive stock market data from financial APIs and databases."),
    tools=[],  # Remove problematic web tools, use custom functions
    verbose=True,
    max_iter=3,
    allow_delegation=False,
    llm=llm,
)

data_collection_task = Task(
    description="""
    Collect comprehensive stock data for {company_stock}. 
    
    Your task is to gather the following key financial metrics:
    - Current stock price information (open, close, high, low)
    - P/E ratio and EPS
    - Market capitalization
    - Revenue and financial ratios
    - Recent trading volume
    - Dividend information if available
    
    Use the ticker symbol format and provide a structured summary of all collected data.
    """,
    expected_output="A comprehensive report containing all relevant financial metrics and stock data for the specified company.",
    agent=data_collector,
    async_execution=False,
)

# News Researcher with better error handling
news_reader = Agent(
    role="Financial News Analyst",
    goal="Analyze and summarize recent financial news and market developments.",
    backstory=("A financial news analyst who specializes in identifying and summarizing key market developments and news that impact stock performance."),
    tools=[],  # Remove problematic web tools
    verbose=True,
    max_iter=3,
    allow_delegation=False,
    llm=llm,
)

news_reader_task = Task(
    description="""
    Research and analyze recent financial news for {company_stock}.
    
    Focus on:
    - Recent earnings reports or announcements
    - Market developments affecting the company
    - Industry news and trends
    - Analyst recommendations or rating changes
    - Any significant corporate events
    
    Provide a structured summary of the most important news items.
    """,
    expected_output="A detailed summary of recent financial news and developments related to the company, organized by importance and relevance.",
    agent=news_reader,
    async_execution=False,
)

# Stock Market Researcher with simplified approach
stock_market_researcher = Agent(
    role="Market Research Analyst",
    goal="Provide comprehensive market analysis and industry insights.",
    backstory=("An experienced market analyst who provides detailed analysis of market conditions, industry trends, and competitive positioning."),
    tools=[],  # Remove problematic web tools
    verbose=True,
    max_iter=3,
    allow_delegation=False,
    max_execution_time=120,
    max_retry_limit=2,
    llm=llm,
)

stock_market_research_task = Task( 
    description="""
    Conduct comprehensive market research analysis for {company_stock}.
    
    Analyze the following areas:
    1. Current market trends affecting the company's sector
    2. Industry position and competitive landscape
    3. Market conditions and economic factors
    4. Risk factors and growth opportunities
    5. Technical analysis indicators if relevant
    
    Provide insights based on available market data and general industry knowledge.
    """,
    expected_output="A comprehensive market analysis report covering industry trends, competitive position, risks, and opportunities.",
    agent=stock_market_researcher,
    async_execution=False,
)

# Financial Analyst with enhanced reporting
financial_analyst = Agent(
    role="Senior Financial Analyst",
    goal="Create comprehensive financial analysis reports based on collected data and research.",
    backstory=("A senior financial analyst with expertise in equity research, financial modeling, and investment analysis. Specializes in creating detailed, actionable investment reports."),
    verbose=True,
    max_iter=3,
    allow_delegation=False,
    llm=llm,
)

financial_analysis_task = Task(
    description="""
    Create a comprehensive stock analysis report for {company_stock} based on all collected data and research.
    
    Your report should include:
    1. Executive Summary
    2. Company Overview
    3. Financial Performance Analysis
    4. Market Position and Competitive Analysis
    5. Recent News and Developments
    6. Risk Assessment
    7. Investment Recommendation
    8. Conclusion
    
    Use all the information gathered from previous tasks to provide a well-structured, professional analysis.
    """,
    expected_output="""
    A comprehensive stock analysis report in the following format:
    
    # Stock Analysis Report: [Company Name]
    
    ## Executive Summary
    [Brief overview of key findings and recommendation]
    
    ## Company Overview
    [Basic company information and business description]
    
    ## Financial Performance Analysis
    [Analysis of financial metrics, ratios, and performance]
    
    ## Market Position and Industry Analysis
    [Competitive position and market conditions]
    
    ## Recent News and Developments
    [Summary of relevant news and events]
    
    ## Risk Assessment
    [Key risks and challenges]
    
    ## Investment Recommendation
    [Clear recommendation with rationale]
    
    ## Conclusion
    [Final summary and key takeaways]
    """,
    agent=financial_analyst,
    output_file="stock_report.txt",
    async_execution=False,
    context=[data_collection_task, news_reader_task, stock_market_research_task],
)

# Manager agent with improved configuration
manager = Agent(
    role="Senior Portfolio Manager",
    goal="Oversee the entire stock analysis process and ensure high-quality, comprehensive research output.",
    backstory=(
        "A senior portfolio manager with over 15 years of experience in equity research and investment analysis. "
        "Expert in coordinating research teams and ensuring thorough, accurate financial analysis. "
        "Responsible for maintaining research quality standards and delivering actionable investment insights."
    ),
    allow_delegation=True,
    verbose=True,
    max_iter=5,
    llm=llm,
)

# Create crew with sequential process for better error handling
crew = Crew(
    agents=[data_collector, news_reader, stock_market_researcher, financial_analyst],
    tasks=[data_collection_task, news_reader_task, stock_market_research_task, financial_analysis_task],
    process=Process.sequential,  # Changed from hierarchical to sequential for better stability
    manager_agent=manager,
    full_output=True,
    verbose=True, 
    memory=False,  # Disable memory to avoid chromadb issues
    planning=False,  # Keep planning disabled
    max_rpm=10,  # Add rate limiting
)