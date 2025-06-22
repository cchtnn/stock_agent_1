import os
import streamlit as st
import markdown
import pdfkit

# Import config first to set environment variables
from config import initialize_app

# Initialize the app configuration
initialize_app()

# Now import the crew after config is set
from agents_tasks import crew
from custom_tools import send_report

st.title("Stock Analysis Report Generator")

# Ensure session state tracks whether the report has been generated and store the output logs
if 'report_generated' not in st.session_state:
    st.session_state['report_generated'] = False

if 'crew_output' not in st.session_state:
    st.session_state['crew_output'] = None

# Input field to enter the company name
company_name = st.text_input("Enter Company Name or Stock Ticker", "")

# Button to generate the stock analysis report
if st.button("Generate Report"):
    if company_name != "":
        with st.spinner("Generating stock analysis report..."):
            try:
                crew_output = crew.kickoff(inputs={"company_stock": company_name})
                st.session_state['crew_output'] = crew_output
                
                # Crew output logs 
                print(f"\nRaw Output:\n {crew_output.raw}")
                print(f"\nTasks Output:\n {crew_output.tasks_output}")
                print(f"\nToken Usage:\n {crew_output.token_usage}")
                
                st.success(f"Report for {company_name} generated successfully!")
                st.session_state['report_generated'] = True
                
            except Exception as e:
                st.error(f"An error occurred while generating the report: {str(e)}")
                print(f"Error details: {e}")
                st.session_state['report_generated'] = False
    else:
        st.error("Please enter a valid company name or stock ticker.")
        st.session_state['report_generated'] = False  

# Check if the report has been generated 
if st.session_state['report_generated'] and st.session_state['crew_output']:
    crew_output = st.session_state['crew_output']
    
    # Display generated report 
    st.markdown("## Generated Report")
    st.markdown(crew_output.raw)

    # Save and convert report to different formats
    try:
        # Save stock analysis report 
        with open("stock_report.txt", "r", encoding='utf-8') as file:
            markdown_text = file.read()

        # Convert to HTML
        html = markdown.markdown(markdown_text)
        with open("stock_report.html", "w", encoding='utf-8') as file:
            file.write(html)

        # Convert HTML to PDF report (only if wkhtmltopdf is available)
        try:
            config = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")
            pdfkit.from_file("stock_report.html", "stock_report.pdf", configuration=config)
            pdf_available = True
        except Exception as pdf_error:
            st.warning("PDF generation failed. Please ensure wkhtmltopdf is installed.")
            print(f"PDF generation error: {pdf_error}")
            pdf_available = False

        # Display chain of thought reasoning and API call metrics 
        with st.expander("Show Chain of Thought"):
            if hasattr(crew_output, 'tasks_output'):
                st.markdown("### Tasks Output")
                st.text(str(crew_output.tasks_output))
            if hasattr(crew_output, 'token_usage'):
                st.markdown("### Token Usage")
                st.text(str(crew_output.token_usage))

        # Send report by email
        st.markdown("## Send Report via Email")
        email_address = st.text_input("Enter your email", "")
        if st.button("Send Email"):
            if email_address and pdf_available:
                try:
                    sender_email = os.getenv('SENDER_EMAIL')  
                    password = os.getenv('EMAIL_PASSWORD') 
                    
                    if not sender_email or not password:
                        st.error("Email credentials not configured. Please set SENDER_EMAIL and EMAIL_PASSWORD in your .env file.")
                    else:
                        subject = f"Stock Analysis Report: {company_name}"  
                        body = "Please find the attached stock analysis report." 
                        file_name = "stock_report.pdf"

                        send_report(sender_email, email_address, password, subject, body, file_name)
                        st.success(f"Email sent successfully to {email_address}!")
                        
                except Exception as email_error:
                    st.error(f"Failed to send email: {str(email_error)}")
            elif not pdf_available:
                st.error("Cannot send email: PDF generation failed.")
            else:
                st.error("Please enter a valid email address.")
                
    except Exception as file_error:
        st.error(f"Error processing report files: {str(file_error)}")