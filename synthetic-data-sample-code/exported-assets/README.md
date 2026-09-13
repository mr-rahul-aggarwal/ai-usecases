# Synthetic Payslip Dataset for Document Classification & Extraction

## Overview
This dataset contains synthetic payslip documents with complete ground truth annotations for training and evaluating document classification and information extraction models.

## Dataset Statistics
- **Total Samples**: 10 payslips
- **Formats**: 5 India-style, 5 USA-style
- **File Types**: HTML (can be converted to PDF/images)
- **Languages**: English (both formats)

## Key Fields Annotated (Ground Truth)
### Common Fields
- `employee_id` - Unique employee identifier
- `employee_name` - Full name of employee
- `designation` - Job title
- `department` - Department name
- `employer_name` - Company name
- `employer_address` - Company address
- `pay_period_start` - Start date of pay period
- `pay_period_end` - End date of pay period
- `pay_date` - Payment date
- `currency` - INR or USD
- `gross_income` - Total earnings before deductions
- `total_deductions` - Sum of all deductions
- `net_income` - Take-home pay (gross - deductions)

### India-Specific Fields
- `pan` - Permanent Account Number
- `uan` - Universal Account Number
- `earnings.basic_salary` - Base salary component
- `earnings.hra` - House Rent Allowance
- `earnings.special_allowance` - Special allowance
- `earnings.transport_allowance` - Transport allowance
- `deductions.provident_fund` - PF contribution
- `deductions.professional_tax` - Professional tax
- `deductions.tds` - Tax Deducted at Source
- `bank_account` - Bank account number
- `bank_name` - Bank name

### USA-Specific Fields
- `ssn` - Social Security Number (partially masked)
- `earnings.regular_pay` - Regular monthly pay
- `deductions.federal_tax` - Federal income tax
- `deductions.state_tax` - State income tax
- `deductions.social_security` - Social Security contribution
- `deductions.medicare` - Medicare tax
- `deductions.health_insurance` - Health insurance premium
- `deductions.retirement_401k` - 401(k) retirement contribution
- `routing_number` - Bank routing number
- `account_number` - Bank account (partially masked)

## Files
- `payslip_ground_truth.json` - Complete ground truth for all samples
- `payslip_XX_[Country]_[ID].html` - Individual payslip HTML files
- `generate_more_payslips.py` - Script to generate additional samples
- `README.md` - This file

## Ground Truth Format
The ground truth is stored as a JSON array where each object represents one payslip:

```json
{
  "employee_id": "EMP8291",
  "employee_name": "Amit Patel",
  "designation": "Software Engineer",
  "employer_name": "Global Systems India Ltd",
  "gross_income": 153593,
  "net_income": 127563,
  "currency": "INR",
  ...
}
```

## Use Cases
1. **Document Classification**: Classify documents as India-style vs USA-style payslips
2. **Named Entity Recognition (NER)**: Extract employee names, employer names
3. **Key Information Extraction (KIE)**: Extract income, deductions, dates
4. **OCR Post-Processing**: Validate and correct OCR output
5. **Vision-Language Model (VLM) Benchmarking**: Test GPT-4o, Claude, Gemini on extraction tasks
6. **Layout Analysis**: Understand different payslip structures

## Converting to PDF or Images

### Method 1: Browser Print to PDF
1. Open any HTML file in Chrome/Firefox
2. Press Ctrl+P (Cmd+P on Mac)
3. Select "Save as PDF"
4. Save with corresponding filename

### Method 2: Using wkhtmltopdf (Linux/Mac)
```bash
# Install wkhtmltopdf first
sudo apt-get install wkhtmltopdf  # Ubuntu/Debian
brew install wkhtmltopdf          # macOS

# Convert all HTML files
for f in payslip_*.html; do
    wkhtmltopdf "$f" "${f%.html}.pdf"
done
```

### Method 3: Using Python (weasyprint)
```python
from weasyprint import HTML

for html_file in glob.glob('payslip_*.html'):
    pdf_file = html_file.replace('.html', '.pdf')
    HTML(filename=html_file).write_pdf(pdf_file)
```

### Method 4: Convert to Images
```python
from pdf2image import convert_from_path

for pdf_file in glob.glob('payslip_*.pdf'):
    images = convert_from_path(pdf_file, dpi=300)
    images[0].save(pdf_file.replace('.pdf', '.png'))
```

## Generating More Samples
Use the provided script to generate additional payslips:

```bash
python generate_more_payslips.py --count 100 --output-dir ./payslips
```

This will create 100 new payslips (50 India-style, 50 USA-style) with updated ground truth.

## Evaluation Metrics
For extraction tasks, consider:
- **Exact Match Accuracy**: Percentage of fields extracted perfectly
- **Field-level F1 Score**: Precision and recall per field type
- **Character Error Rate (CER)**: For name/address extraction
- **Numerical Accuracy**: For income/deduction amounts

## Data Characteristics
### India-Style Payslips
- Layout: Traditional tabular format
- Currency: INR (₹)
- Salary Range: ₹40,000 - ₹120,000 (basic)
- Common Fields: PAN, UAN, PF, HRA, TDS
- Tax Structure: TDS + Professional Tax + PF

### USA-Style Payslips
- Layout: Modern, summary-first format
- Currency: USD ($)
- Salary Range: $80,000 - $180,000 (annual)
- Common Fields: SSN, 401(k), Federal/State Tax
- Tax Structure: Federal + State + SS + Medicare

## Privacy & Legal
- All data is **100% synthetic**
- No real employee information used
- No privacy concerns
- Safe for public sharing and research
- Suitable for commercial ML model training

## Citation
If you use this dataset in your research, please cite:
```
Synthetic Payslip Dataset for Document Extraction (2024)
Generated using template-based synthesis with realistic salary structures
```

## License
This dataset is released under MIT License. Free for academic and commercial use.

## Contact
For questions or additional samples, please reach out via GitHub issues.
