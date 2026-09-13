# Sample Extraction Tasks for Benchmarking

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
