
import json
import os
from pydantic import BaseModel, Field
from datetime import date
import re
import json
from datetime import datetime
from decimal import Decimal
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages
from datetime import datetime
from fpdf import FPDF


# Function to generate financial report, visualizations, and PDF
def generate_complete_report(df: pd.DataFrame, report_csv="financial_report.csv", daily_csv="daily_summary.csv", pdf_file="financial_report.pdf"):
    # Clean and Prepare Data 
    df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce', dayfirst=True)
    df.sort_values(by='transaction_date', inplace=True)

    df['withdrawals'] = pd.to_numeric(df['withdrawals'], errors='coerce').fillna(0)
    df['deposits'] = pd.to_numeric(df['deposits'], errors='coerce').fillna(0)
    df['balance'] = pd.to_numeric(df['balance'], errors='coerce').fillna(0)

    # Summary Stats 
    total_withdrawals = df['withdrawals'].sum()
    total_deposits = df['deposits'].sum()
    avg_withdrawals = df.loc[df['withdrawals'] > 0, 'withdrawals'].mean()
    avg_deposits = df.loc[df['deposits'] > 0, 'deposits'].mean()
    max_withdrawal = df['withdrawals'].max()
    max_deposit = df['deposits'].max()
    starting_balance = df.iloc[0]['balance']
    ending_balance = df.iloc[-1]['balance']
    net_change = ending_balance - starting_balance

    report = {
        "Total Deposits": round(total_deposits, 2),
        "Total Withdrawals": round(total_withdrawals, 2),
        "Average Deposit": round(avg_deposits, 2),
        "Average Withdrawal": round(avg_withdrawals, 2),
        "Max Deposit": round(max_deposit, 2),
        "Max Withdrawal": round(max_withdrawal, 2),
        "Starting Balance": round(starting_balance, 2),
        "Ending Balance": round(ending_balance, 2),
        "Net Change": round(net_change, 2),
        "Net Change %": round((net_change / starting_balance) * 100, 2)
    }


    # Day-to-Day Summary 
    daily_summary = df.groupby('transaction_date').agg(
        Daily_Withdrawals=('withdrawals', 'sum'),
        Daily_Deposits=('deposits', 'sum'),
        Closing_Balance=('balance', 'last')
    ).reset_index()

    daily_summary['Cumulative_Spend'] = daily_summary['Daily_Withdrawals'].cumsum()
    daily_summary['Cumulative_Deposits'] = daily_summary['Daily_Deposits'].cumsum()
    daily_summary.to_csv(daily_csv, index=False)

    # Visualization 
    sns.set(style="whitegrid")
    plt.figure(figsize=(12, 6))
    plt.plot(daily_summary['transaction_date'], daily_summary['Daily_Withdrawals'], label='Daily Withdrawals', color='red')
    plt.plot(daily_summary['transaction_date'], daily_summary['Daily_Deposits'], label='Daily Deposits', color='green')
    plt.plot(daily_summary['transaction_date'], daily_summary['Cumulative_Spend'], label='Cumulative Spend', color='blue', linestyle='--')
    plt.plot(daily_summary['transaction_date'], daily_summary['Cumulative_Deposits'], label='Cumulative Deposits', color='purple', linestyle='--')
    plt.title("Day-to-Day Withdrawals, Deposits & Cumulative Totals")
    plt.xlabel("Date")
    plt.ylabel("Amount")
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    chart_file = "financial_chart.png"
    plt.savefig(chart_file)
    plt.close()

    # Create PDF Report 
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Title
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, "Financial Statement Report", ln=True, align="C")
    pdf.ln(10)

    # Summary Section
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Summary Statistics", ln=True)
    pdf.set_font("Arial", '', 12)
    for key, value in report.items():
        pdf.cell(0, 8, f"{key}: {value}", ln=True)
    pdf.ln(10)

    # Insert Chart
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Visual Chart", ln=True)
    pdf.image(chart_file, w=180)
    pdf.ln(10)

    pdf.output(pdf_file)
    print(f" Report saved as {pdf_file}")
    print(f" CSVs saved as {report_csv} and {daily_csv}")
    print(f" Chart saved as {chart_file}")



def clean_json_text(text):
    # Remove markdown code fences and extra text
    cleaned = re.sub(r"```(?:json)?", "", text)
    cleaned = cleaned.strip()
    # Extract JSON array using regex if extra text exists
    match = re.search(r"(\[.*\])", cleaned, re.DOTALL)
    return match.group(1) if match else cleaned

def parse_date(date_str):
    """Try multiple date formats for parsing."""
    for fmt in ("%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Unknown date format: {date_str}")

def clean_transaction_data(tx):
    """Convert date strings & remove commas from numbers."""
    tx["transaction_date"] = parse_date(tx["transaction_date"])
    tx["value_date"] = parse_date(tx["value_date"])
    tx["withdrawals"] = float(tx["withdrawals"].replace(",", ""))
    tx["deposits"] = float(tx["deposits"].replace(",", ""))
    tx["balance"] = float(tx["balance"].replace(",", ""))
    return tx


# Define the Pydantic model
class Transaction(BaseModel):
    transaction_date: date = Field(..., description="The date the transaction occurred (DD-MM-YYYY ).")
    value_date: date = Field(..., description="The date the transaction value was applied to the account (DD-MM-YYYY ).")
    description: str = Field(..., description="A description of the transaction.")
    withdrawals: Decimal = Field(..., description="The amount withdrawn, if applicable.")
    deposits: Decimal = Field(..., description="The amount deposited, if applicable.")
    balance: Decimal = Field(..., description="The account balance after the transaction.")


# Parse JSON
output_dir = "./output"
files = [file for file in os.listdir(output_dir) if file.endswith('.txt')]
all_transactions = []
for idx,file in enumerate(files):
    openfile = os.path.join(output_dir,file)
    with open(openfile,'r') as f:
        json_text = f.read()
        json_text = clean_json_text(json_text)
        
        try:
            transactions = json.loads(json_text)
            for transaction in transactions:
                t = clean_transaction_data(transaction.copy())
                tx = Transaction(**t)  # Validate with Pydantic
                all_transactions.append(tx.model_dump())
        except json.JSONDecodeError:
                    print(f"Warning: Page {idx+1} {t} returned invalid JSON")


# Save All Transactions to CSV
df = pd.DataFrame(all_transactions)
df.to_csv(os.path.join(output_dir, "all_transactions.csv"), index=False)
report_csv = os.path.join(output_dir,'financial_report.csv')
daily_csv = os.path.join(output_dir,'daily_summary.csv')
pdf_file = os.path.join(output_dir,'financial_report.pdf')
generate_complete_report(df,report_csv,daily_csv,pdf_file)