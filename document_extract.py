import os
from google import genai
from google.genai import types
from pdf2image import convert_from_path
import time 
from datetime import datetime

GEMINI_KEY = ""

# Initialize Gemini client
client = genai.Client(api_key = GEMINI_KEY)

# Prompt for Gemini
prompt = """
Extract all transactions from this bank statement in JSON format. Each transaction should have the following fields:

- transaction_date: The date the transaction occurred (DD-MM-YYYY ).
- value_date: The value date (DD-MM-YYYY ).
- description: The transaction description text.
- withdrawals: The withdrawal amount as a string (if empty, use "0.00").
- deposits: The deposit amount as a string (if empty, use "0.00").
- balance: The balance amount as a string.

Return the response as a JSON array of objects matching this schema:

[
  {
    "transaction_date": "",
    "value_date": "",
    "description": "",
    "withdrawals": "",
    "deposits": "",
    "balance": ""
  }
]

Only include transactions; do not include any metadata or extra text. Preserve numeric values as shown in the document.
"""

pdf_path = "document_data.pdf"
image_dir = "./image"
os.makedirs(image_dir, exist_ok=True)

pages = convert_from_path(pdf_path, dpi=300)
print(f"PDF has {len(pages)} pages")

png_files = []
for i, page in enumerate(pages):
    page_path = os.path.join(image_dir, f"page_{i+1}.png")
    page.save(page_path, "PNG")
    png_files.append(page_path)
    print(f"Saved {page_path}")


# Process Images with Gemini
output_dir = "./output"
os.makedirs(output_dir, exist_ok=True)

for idx, img_path in enumerate(png_files):
    with open(img_path, "rb") as f:
        image_bytes = f.read()

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type="image/png"),
                prompt
            ]
        )

        json_text = response.text.strip()
        
        # Save raw response
        output_file = os.path.join(output_dir, f"transaction_page_{idx+1}.txt")
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(json_text)
        
        print(f"Response saved to {output_file}")

        time.sleep(15)  # Avoid hitting rate limits

    except Exception as e:
        print(f"Error processing page {idx+1}: {e}")
    
