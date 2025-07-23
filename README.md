# Bank Statement Transaction Extractor & Financial Report Generator
(Please note that I have not uploaded the any files here except the code)    
This project extracts **transaction information** from scanned bank statements using **Google Gemini (LLM)** and generates **statistical and visual financial reports**.
The solution demonstrates the use of **Generative AI (Gemini)** for OCR-based extraction and **data analytics with justification metrics** for insights.

---

## Features
* **Justification Metrics for LLM**
* **Problems faced and yet to solve**.
* **OCR with LLM (Google Gemini)**: Extract transactions from PDF statements.
* **Data Cleaning & Validation**: Ensures structured data with Pydantic models.
* **Statistical Report**
* **Visual Charts**
* **Automated PDF Report**:
  * Summary statistics
  * Charts

## Justification of LLM

* **LLM Role**: Extract transactions from semi-structured PDF statements.
* **Metrics & Validation**:
  * Used Gemini-2.5-flash becuase of it is one of the state of the art visual reasoning and OCR model.     
  * For finanical purposes Field-Level Accuracy, Field Value Accuracy, Character Error Rate (CER) and Word Error Rate (WER) are most important, Gemini 2.5 flash excels at this.    
  * Also, since I dont have GPU, I could not use open source models, the models dont fit in my RAM.    
  * Additionaly the model tops various benchmark such as https://getomni.ai/blog/ocr-benchmark,       
---

## Problems faced and yet to solve:
  * Page break caused few descriptions to be incorrect. Solution tried: Concatenated two page images into one and then tried extracted information which overlapped between the pages. Still did not work properly.
  * one of the extracted line does not validate with pydantic.   
  * two of the lines and minus sign in withdrawals, so it is added automatically by the LLM in deposits.   
  --- 

## Tech Stack

* **Google Gemini** for OCR & transaction extraction
* **Python** for processing & visualization
* **Libraries**:

  * `pdf2image`, `fpdf`
  * `pandas`, `seaborn`, `matplotlib`
  * `pydantic` for validation

---

## Project Structure

```
.
├── document_data.pdf           # Input bank statement, Have not uploaded. PLease upload your document
├── Document_extract.py         # Extract transactions using Gemini OCR
├── Data_processing.py          # Clean, analyze, and generate reports
├── output/                     # Stores extracted transactions & reports
│   ├── all_transactions.csv
│   ├── financial_report.pdf
│   ├── financial_report.csv
│   ├── daily_summary.csv
│   └── transaction_page_*.txt
└── README.md
```

---

## How It Works

### 1. **Extract Transactions**

`Document_extract.py`:

* Converts **PDF → PNG** (using `pdf2image`)
* Sends each page to **Gemini LLM** for structured JSON extraction
* Saves responses to `output/transaction_page_*.txt`

### 2. **Process & Analyze**

`Data_processing.py`:

* Cleans and validates transactions (dates, numeric fields)
* Aggregates daily summaries and calculates metrics
* Generates charts and compiles a **PDF financial report**

---

## Example Metrics in Report

* **Total Deposits**: ₹XXX
* **Total Withdrawals**: ₹XXX
* **Average Deposit**: ₹XXX
* **Max Withdrawal**: ₹XXX
* **Net Change**: ₹XXX (XX%)

---

## Installation & Usage

### **1. Clone the Repository**

```bash
git clone https://github.com/yogheswaran-A/Task.git
cd Task
```

### **2. Install Dependencies**

```bash
pip install -r requirements.txt
```

### **3. Set Google Gemini API Key**
In the document_extractor.py set the KPI
```python
GEMINI_KEY = "your_api_key_here"
```

### **4. Run Extraction**

```bash
python Document_extract.py
```

### **5. Generate Reports**

```bash
python Data_processing.py
```

Reports and CSVs will be available in the `output/` folder. 

---

## Output Examples

* `all_transactions.csv` – All extracted transactions
* `financial_report.pdf` – Summary report with charts
* `daily_summary.csv` – Daily summary of spend and deposits


