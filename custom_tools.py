import yfinance as yf
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.application import MIMEApplication
from email import encoders
import requests
import json
from datetime import datetime, timedelta

def fetch_stock_data(ticker: str) -> str:
    """Fetch comprehensive stock data and historical market data with error handling."""
    try:
        stock = yf.Ticker(ticker)
        
        # Fetch current stock information and history of prices
        stock_info = stock.info
        hist = stock.history(period="1mo")
        
        # Handle case where stock info might be empty
        if not stock_info:
            return f"Error: Could not fetch data for ticker {ticker}. Please verify the ticker symbol."

        output = (
            f"Stock Data for {ticker}:\n"
            f"Company Name: {stock_info.get('longName', 'N/A')}\n"
            f"Sector: {stock_info.get('sector', 'N/A')}\n"
            f"Industry: {stock_info.get('industry', 'N/A')}\n"
            f"Current Price: ${stock_info.get('currentPrice', stock_info.get('regularMarketPrice', 'N/A'))}\n"
            f"Previous Close: ${stock_info.get('previousClose', 'N/A')}\n"
            f"Open Price: ${stock_info.get('open', 'N/A')}\n"
            f"Day High: ${stock_info.get('dayHigh', 'N/A')}\n"
            f"Day Low: ${stock_info.get('dayLow', 'N/A')}\n"
            f"52 Week High: ${stock_info.get('fiftyTwoWeekHigh', 'N/A')}\n"
            f"52 Week Low: ${stock_info.get('fiftyTwoWeekLow', 'N/A')}\n"
            f"Market Cap: ${stock_info.get('marketCap', 'N/A')}\n"
            f"Volume: {stock_info.get('volume', 'N/A')}\n"
            f"Average Volume: {stock_info.get('averageVolume', 'N/A')}\n"
            f"P/E Ratio: {stock_info.get('forwardPE', stock_info.get('trailingPE', 'N/A'))}\n"
            f"EPS: {stock_info.get('trailingEps', 'N/A')}\n"
            f"Revenue: ${stock_info.get('totalRevenue', 'N/A')}\n"
            f"Debt to Equity: {stock_info.get('debtToEquity', 'N/A')}\n"
            f"Dividend Yield: {stock_info.get('dividendYield', 'N/A')}\n"
            f"Book Value: ${stock_info.get('bookValue', 'N/A')}\n"
            f"Price to Book: {stock_info.get('priceToBook', 'N/A')}\n"
            f"Beta: {stock_info.get('beta', 'N/A')}\n\n"
        )

        # Add historical data if available
        if not hist.empty:
            output += "Historical Stock Prices (Past Month):\n"
            for date, row in hist.tail(10).iterrows():  # Last 10 days
                output += (
                    f"Date: {date.date()}, Open: ${row['Open']:.2f}, High: ${row['High']:.2f}, "
                    f"Low: ${row['Low']:.2f}, Close: ${row['Close']:.2f}, Volume: {row['Volume']}\n"
                )
        else:
            output += "Historical data not available.\n"

        return output
    
    except Exception as e:
        return f"Error fetching stock data for {ticker}: {str(e)}"

def fetch_stock_financials(ticker: str) -> str:
    """Fetch financial statements for the stock with error handling."""
    try:
        stock = yf.Ticker(ticker)
        
        # Try to get financial data
        try:
            income_stmt = stock.income_stmt
            balance_sheet = stock.balance_sheet
            cash_flow = stock.cashflow
        except Exception:
            return f"Financial statements not available for {ticker}"

        output = f"Financial Statements for {ticker}:\n\n"
        
        # Check if data is available
        if not income_stmt.empty:
            output += "Income Statement (Most Recent Year):\n"
            # Get the most recent year data
            recent_year = income_stmt.columns[0]
            key_metrics = ['Total Revenue', 'Gross Profit', 'Operating Income', 'Net Income']
            
            for metric in key_metrics:
                if metric in income_stmt.index:
                    value = income_stmt.loc[metric, recent_year]
                    output += f"{metric}: ${value:,.0f}\n"
            output += "\n"
        
        if not balance_sheet.empty:
            output += "Balance Sheet (Most Recent Year):\n"
            recent_year = balance_sheet.columns[0]
            key_metrics = ['Total Assets', 'Total Debt', 'Total Equity', 'Cash And Cash Equivalents']
            
            for metric in key_metrics:
                if metric in balance_sheet.index:
                    value = balance_sheet.loc[metric, recent_year]
                    output += f"{metric}: ${value:,.0f}\n"
            output += "\n"
        
        if not cash_flow.empty:
            output += "Cash Flow Statement (Most Recent Year):\n"
            recent_year = cash_flow.columns[0]
            key_metrics = ['Operating Cash Flow', 'Investing Cash Flow', 'Financing Cash Flow']
            
            for metric in key_metrics:
                if metric in cash_flow.index:
                    value = cash_flow.loc[metric, recent_year]
                    output += f"{metric}: ${value:,.0f}\n"

        return output
    
    except Exception as e:
        return f"Error fetching financial data for {ticker}: {str(e)}"

def fetch_stock_news(ticker: str) -> str:
    """Fetch recent news articles related to the company stock with error handling."""
    try:
        stock = yf.Ticker(ticker)
        news_items = stock.news
        
        if not news_items:
            return f"No recent news available for {ticker}"
        
        # Format the news into a readable summary
        news_summary = []
        for i, item in enumerate(news_items[:7]):  # Limit to top 7 news articles
            title = item.get('title', 'No title available')
            publisher = item.get('publisher', 'Unknown publisher')
            link = item.get('link', 'No link available')
            
            # Try to get publish time
            publish_time = item.get('providerPublishTime', 0)
            if publish_time:
                publish_date = datetime.fromtimestamp(publish_time).strftime('%Y-%m-%d %H:%M')
            else:
                publish_date = 'Date not available'
            
            summary = f"{i+1}. {title} - {publisher} ({publish_date})\n   Link: {link}\n"
            news_summary.append(summary)
        
        # Join all summaries into a single string
        return f"Recent News for {ticker}:\n\n" + "\n".join(news_summary)
    
    except Exception as e:
        return f"Error fetching news for {ticker}: {str(e)}"

def get_stock_analysis_summary(ticker: str) -> str:
    """Get a comprehensive summary combining all stock data."""
    try:
        # Fetch all data
        stock_data = fetch_stock_data(ticker)
        financial_data = fetch_stock_financials(ticker)
        news_data = fetch_stock_news(ticker)
        
        # Combine all data
        full_summary = f"""
COMPREHENSIVE STOCK ANALYSIS FOR {ticker.upper()}
{"="*50}

{stock_data}

{financial_data}

{news_data}

Analysis completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        return full_summary
    
    except Exception as e:
        return f"Error generating comprehensive analysis for {ticker}: {str(e)}"

def send_report(sender_email, receiver_email, password, subject, body, file_name):
    """Send report via email with improved error handling."""
    try:
        # Create a multipart message container
        message = MIMEMultipart()
        message['From'] = sender_email  
        message['To'] = receiver_email  
        message['Subject'] = subject  

        # Attach the text body of the email
        message.attach(MIMEText(body, 'plain'))

        # Check if file exists before attaching
        import os
        if not os.path.exists(file_name):
            raise FileNotFoundError(f"File {file_name} not found")

        # Open the file and attach it
        with open(file_name, "rb") as attachment:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            
            # Add header for attachment
            part.add_header(
                "Content-Disposition",
                f"attachment; filename={os.path.basename(file_name)}",
            )
            message.attach(part)

        # Send the email
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())
        server.quit()
        print("Email sent successfully!")
        
    except Exception as e:
        print(f"Error sending email: {e}")
        raise e