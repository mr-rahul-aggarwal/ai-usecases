
import csv
import json

# Load ground truth
with open('payslip_ground_truth.json', 'r') as f:
    gt_data = json.load(f)

# Create field mapping CSV
field_mapping = [
    ["Field Name", "Type", "Description", "India", "USA", "Example (India)", "Example (USA)"],
    ["employee_id", "string", "Unique employee identifier", "✓", "✓", "EMP8291", "931744"],
    ["employee_name", "string", "Full name of employee", "✓", "✓", "Amit Patel", "Sarah Johnson"],
    ["designation", "string", "Job title/position", "✓", "✓", "Software Engineer", "Data Scientist"],
    ["department", "string", "Department name", "✓", "✓", "Engineering", "Data Science"],
    ["employer_name", "string", "Company name", "✓", "✓", "Global Systems India Ltd", "TechCorp Solutions Inc."],
    ["employer_address", "string", "Company address", "✓", "✓", "DLF Cyber City, Gurgaon", "1234 Silicon Valley Blvd"],
    ["pay_period_start", "date", "Start of pay period", "✓", "✓", "2024-02-14", "2024-01-15"],
    ["pay_period_end", "date", "End of pay period", "✓", "✓", "2024-03-14", "2024-02-14"],
    ["pay_date", "date", "Payment date", "✓", "✓", "2024-03-15", "2024-02-15"],
    ["currency", "string", "Currency code", "✓", "✓", "INR", "USD"],
    ["gross_income", "integer", "Total earnings before deductions", "✓", "✓", "153593", "12500"],
    ["total_deductions", "integer", "Sum of all deductions", "✓", "✓", "26030", "3245"],
    ["net_income", "integer", "Take-home pay", "✓", "✓", "127563", "9255"],
    ["country", "string", "Country style", "✓", "✓", "India", "USA"],
    ["pan", "string", "Permanent Account Number", "✓", "✗", "BAHAA4569C", "N/A"],
    ["uan", "string", "Universal Account Number", "✓", "✗", "360237077075", "N/A"],
    ["bank_account", "string", "Bank account number", "✓", "✗", "99598203352", "N/A"],
    ["bank_name", "string", "Bank name", "✓", "✗", "State Bank of India", "N/A"],
    ["ssn", "string", "Social Security Number (masked)", "✗", "✓", "N/A", "XXX-XX-4523"],
    ["routing_number", "string", "Bank routing number", "✗", "✓", "N/A", "345678901"],
    ["account_number", "string", "Bank account (masked)", "✗", "✓", "N/A", "XXXX5678"],
    ["earnings.basic_salary", "integer", "Base salary", "✓", "✗", "88808", "N/A"],
    ["earnings.hra", "integer", "House Rent Allowance", "✓", "✗", "35523", "N/A"],
    ["earnings.special_allowance", "integer", "Special allowance", "✓", "✗", "26642", "N/A"],
    ["earnings.transport_allowance", "integer", "Transport allowance", "✓", "✗", "2620", "N/A"],
    ["earnings.regular_pay", "integer", "Regular monthly pay", "✗", "✓", "N/A", "12500"],
    ["deductions.provident_fund", "integer", "PF contribution", "✓", "✗", "10656", "N/A"],
    ["deductions.professional_tax", "integer", "Professional tax", "✓", "✗", "200", "N/A"],
    ["deductions.tds", "integer", "Tax Deducted at Source", "✓", "✗", "15174", "N/A"],
    ["deductions.federal_tax", "integer", "Federal income tax", "✗", "✓", "N/A", "2250"],
    ["deductions.state_tax", "integer", "State income tax", "✗", "✓", "N/A", "625"],
    ["deductions.social_security", "integer", "Social Security tax", "✗", "✓", "N/A", "775"],
    ["deductions.medicare", "integer", "Medicare tax", "✗", "✓", "N/A", "181"],
    ["deductions.health_insurance", "integer", "Health insurance premium", "✗", "✓", "N/A", "300"],
    ["deductions.retirement_401k", "integer", "401(k) contribution", "✗", "✓", "N/A", "500"],
]

with open('field_mapping.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerows(field_mapping)

print("✓ Created field_mapping.csv")

# Create a sample extraction task file
extraction_tasks = """# Sample Extraction Tasks for Benchmarking

## Task 1: Core Information Extraction
Extract the following fields:
- employee_name
- employer_name  
- gross_income
- net_income

**Evaluation**: Exact match accuracy per field

## Task 2: Date Extraction
Extract all date fields:
- pay_period_start
- pay_period_end
- pay_date

**Evaluation**: Exact match (YYYY-MM-DD format)

## Task 3: Country Classification
Classify payslip as India-style or USA-style

**Evaluation**: Classification accuracy

## Task 4: Complete Field Extraction (India)
For India-style payslips, extract all 20+ fields including:
- Basic employee info (name, ID, designation)
- Indian-specific fields (PAN, UAN)
- Earnings breakdown (basic, HRA, allowances)
- Deductions breakdown (PF, tax, TDS)
- Banking details

**Evaluation**: Field-level F1 score

## Task 5: Complete Field Extraction (USA)
For USA-style payslips, extract all 15+ fields including:
- Basic employee info (name, ID, position)
- USA-specific fields (SSN, routing number)
- Gross pay
- Detailed deductions (federal, state, SS, medicare, 401k, insurance)
- Net pay

**Evaluation**: Field-level F1 score

## Task 6: Numerical Accuracy Test
Extract and verify arithmetic:
- gross_income - total_deductions = net_income
- Sum of individual earnings = gross_income
- Sum of individual deductions = total_deductions

**Evaluation**: Calculation accuracy rate

## Sample Prompts for Vision LLMs

### Prompt 1: Simple Extraction
```
Extract the following information from this payslip:
- Employee Name
- Employer Name
- Gross Income
- Net Income

Return as JSON.
```

### Prompt 2: Structured Extraction
```
You are a document processing expert. Analyze this payslip image and extract all available information in the following JSON format:

{
  "employee_id": "",
  "employee_name": "",
  "employer_name": "",
  "pay_date": "",
  "gross_income": 0,
  "net_income": 0,
  "currency": ""
}

Be precise with numerical values and dates.
```

### Prompt 3: Detailed Extraction with Validation
```
Extract all information from this salary slip. Follow these rules:
1. Extract numeric values without currency symbols or commas
2. Use YYYY-MM-DD format for all dates
3. Include country-specific fields (PAN/UAN for India, SSN for USA)
4. Break down earnings and deductions into individual components
5. Verify that gross_income - total_deductions = net_income

Return complete JSON with all available fields.
```

## Evaluation Metrics to Track

1. **Exact Match Accuracy**: Percentage of fields extracted perfectly
2. **Character Error Rate (CER)**: For text fields like names and addresses
3. **Numerical Accuracy**: For amounts (tolerance: ±1 for rounding)
4. **Date Format Accuracy**: Correct YYYY-MM-DD parsing
5. **Field Detection Rate**: Percentage of expected fields found
6. **Extraction Time**: Time per document (for efficiency benchmarking)
7. **Confidence Scores**: If model provides them
8. **Country Classification Accuracy**: India vs USA style

## Recommended Test Split
- Training: 60% (6 documents)
- Validation: 20% (2 documents)  
- Test: 20% (2 documents)

Or generate more samples (100+) for robust evaluation:
- Training: 70 documents
- Validation: 15 documents
- Test: 15 documents
"""

with open('extraction_tasks.md', 'w', encoding='utf-8') as f:
    f.write(extraction_tasks)

print("✓ Created extraction_tasks.md")

# Print summary
print("\n" + "="*60)
print("DATASET GENERATION COMPLETE")
print("="*60)
print("\nFiles created:")
print("1. payslip_ground_truth.json - Complete ground truth annotations")
print("2. payslip_01 to payslip_10 (HTML files) - Synthetic payslip documents")
print("3. field_mapping.csv - Field reference guide")
print("4. extraction_tasks.md - Sample benchmark tasks and prompts")
print("5. generate_more_payslips.py - Script to generate more samples")
print("6. README.md - Complete documentation")

print("\n" + "="*60)
print("DATASET STATISTICS")
print("="*60)
print(f"Total samples: {len(gt_data)}")
print(f"India-style: {sum(1 for d in gt_data if d['country'] == 'India')}")
print(f"USA-style: {sum(1 for d in gt_data if d['country'] == 'USA')}")
print(f"Total extractable fields (India): 20+")
print(f"Total extractable fields (USA): 15+")
print(f"Common fields (both): 13")

print("\n" + "="*60)
print("NEXT STEPS")
print("="*60)
print("1. Convert HTML to PDF:")
print("   - Open in browser → Print → Save as PDF")
print("   - Or use: wkhtmltopdf payslip_*.html")
print("\n2. Convert PDF to images (optional):")
print("   - Use pdf2image library")
print("   - Or ImageMagick: convert -density 300 file.pdf file.png")
print("\n3. Start experiments:")
print("   - Test OCR engines (Tesseract, Google Vision, AWS Textract)")
print("   - Benchmark Vision LLMs (GPT-4o, Claude, Gemini)")
print("   - Evaluate extraction accuracy using ground truth")
print("\n4. Generate more samples:")
print("   python generate_more_payslips.py --count 100")
