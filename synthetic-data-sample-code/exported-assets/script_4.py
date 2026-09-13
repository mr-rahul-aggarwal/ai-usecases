
# Create a Python script that users can run to generate more payslips
generator_script = """#!/usr/bin/env python3
\"\"\"
Synthetic Payslip Generator
Generate realistic payslip documents with ground truth for ML experiments
\"\"\"

import json
import random
import argparse
from datetime import datetime, timedelta
from pathlib import Path


def generate_employee_data(count=10, seed=None):
    \"\"\"Generate synthetic employee records\"\"\"
    if seed:
        random.seed(seed)
    
    employees = []
    
    first_names = ["Rajesh", "Priya", "Amit", "Sarah", "Michael", "Jennifer", 
                   "Vikram", "Anita", "David", "Emily", "Rahul", "Kavya",
                   "James", "Lisa", "Arjun", "Sneha", "Robert", "Meera"]
    last_names = ["Kumar", "Sharma", "Patel", "Johnson", "Smith", "Williams", 
                  "Singh", "Brown", "Davis", "Wilson", "Reddy", "Gupta",
                  "Anderson", "Nair", "Martinez", "Chen", "Garcia", "Lee"]
    
    companies_us = [
        {"name": "TechCorp Solutions Inc.", "address": "1234 Silicon Valley Blvd, San Jose, CA 95110"},
        {"name": "DataVision Analytics LLC", "address": "5678 Innovation Drive, Austin, TX 78701"},
        {"name": "CloudStream Technologies", "address": "9012 Enterprise Way, Seattle, WA 98101"},
        {"name": "Quantum Computing Corp", "address": "4567 Research Parkway, Boston, MA 02101"},
        {"name": "AI Innovations Inc", "address": "7890 Tech Center, San Francisco, CA 94102"},
    ]
    
    companies_india = [
        {"name": "InfoTech Solutions Pvt Ltd", "address": "Block A, Cyber Towers, HITEC City, Hyderabad 500081"},
        {"name": "Digital Innovations India Pvt Ltd", "address": "Prestige Tech Park, Marathahalli, Bengaluru 560037"},
        {"name": "Global Systems India Ltd", "address": "DLF Cyber City, Gurgaon, Haryana 122002"},
        {"name": "Smart Analytics Pvt Ltd", "address": "Mindspace IT Park, Pune, Maharashtra 411014"},
        {"name": "TechVista India Pvt Ltd", "address": "Technopark Campus, Trivandrum, Kerala 695581"},
    ]
    
    designations = ["Software Engineer", "Senior Software Engineer", "Data Scientist", 
                   "ML Engineer", "DevOps Engineer", "Product Manager", "QA Engineer",
                   "Backend Developer", "Full Stack Developer", "Data Analyst"]
    
    departments = ["Engineering", "Data Science", "Operations", "Product", 
                  "Quality Assurance", "DevOps", "Analytics"]
    
    for i in range(count):
        is_india = i % 2 == 0
        
        company = random.choice(companies_india if is_india else companies_us)
        employee_name = f"{random.choice(first_names)} {random.choice(last_names)}"
        
        pay_date = datetime(2024, random.randint(1, 12), random.choice([15, 28]))
        pay_period_start = pay_date - timedelta(days=30)
        pay_period_end = pay_date - timedelta(days=1)
        
        if is_india:
            basic_salary = random.randint(40000, 120000)
            hra = int(basic_salary * random.uniform(0.35, 0.45))
            special_allowance = int(basic_salary * random.uniform(0.25, 0.35))
            transport_allowance = random.randint(1600, 3200)
            
            gross_income = basic_salary + hra + special_allowance + transport_allowance
            
            pf_deduction = int(basic_salary * 0.12)
            professional_tax = random.choice([200, 208])
            tds = int(gross_income * random.uniform(0.05, 0.15))
            
            total_deductions = pf_deduction + professional_tax + tds
            net_income = gross_income - total_deductions
            
            employee = {
                "employee_id": f"EMP{random.randint(1000, 9999)}",
                "employee_name": employee_name,
                "designation": random.choice(designations),
                "department": random.choice(departments),
                "employer_name": company["name"],
                "employer_address": company["address"],
                "pan": f"{random.choice(['A', 'B', 'C'])}{random.choice(['A', 'B', 'C'])}{random.choice(['C', 'P', 'H'])}{random.choice(['A', 'B', 'C'])}{random.choice(['A', 'B'])}{random.randint(1000, 9999)}{random.choice(['A', 'B', 'C', 'D'])}",
                "uan": f"{random.randint(100000000000, 999999999999)}",
                "pay_period_start": pay_period_start.strftime("%Y-%m-%d"),
                "pay_period_end": pay_period_end.strftime("%Y-%m-%d"),
                "pay_date": pay_date.strftime("%Y-%m-%d"),
                "currency": "INR",
                "earnings": {
                    "basic_salary": basic_salary,
                    "hra": hra,
                    "special_allowance": special_allowance,
                    "transport_allowance": transport_allowance
                },
                "gross_income": gross_income,
                "deductions": {
                    "provident_fund": pf_deduction,
                    "professional_tax": professional_tax,
                    "tds": tds
                },
                "total_deductions": total_deductions,
                "net_income": net_income,
                "country": "India",
                "bank_account": f"{random.randint(10000000000, 99999999999)}",
                "bank_name": random.choice(["HDFC Bank", "ICICI Bank", "State Bank of India", "Axis Bank"])
            }
        else:
            annual_salary = random.randint(80000, 180000)
            gross_income = int(annual_salary / 12)
            
            federal_tax = int(gross_income * random.uniform(0.15, 0.22))
            state_tax = int(gross_income * random.uniform(0.04, 0.08))
            social_security = int(gross_income * 0.062)
            medicare = int(gross_income * 0.0145)
            health_insurance = random.choice([250, 300, 350, 400])
            retirement_401k = int(gross_income * random.uniform(0.03, 0.06))
            
            total_deductions = federal_tax + state_tax + social_security + medicare + health_insurance + retirement_401k
            net_income = gross_income - total_deductions
            
            employee = {
                "employee_id": f"{random.randint(100000, 999999)}",
                "employee_name": employee_name,
                "designation": random.choice(designations),
                "department": random.choice(departments),
                "employer_name": company["name"],
                "employer_address": company["address"],
                "ssn": f"XXX-XX-{random.randint(1000, 9999)}",
                "pay_period_start": pay_period_start.strftime("%Y-%m-%d"),
                "pay_period_end": pay_period_end.strftime("%Y-%m-%d"),
                "pay_date": pay_date.strftime("%Y-%m-%d"),
                "currency": "USD",
                "earnings": {
                    "regular_pay": gross_income
                },
                "gross_income": gross_income,
                "deductions": {
                    "federal_tax": federal_tax,
                    "state_tax": state_tax,
                    "social_security": social_security,
                    "medicare": medicare,
                    "health_insurance": health_insurance,
                    "retirement_401k": retirement_401k
                },
                "total_deductions": total_deductions,
                "net_income": net_income,
                "country": "USA",
                "routing_number": f"{random.randint(100000000, 999999999)}",
                "account_number": f"XXXX{random.randint(1000, 9999)}"
            }
        
        employees.append(employee)
    
    return employees


def create_india_payslip_html(employee):
    \"\"\"Generate India-style payslip HTML\"\"\"
    # Same template as before - keeping it concise for the script file
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Payslip - {employee['employee_name']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .payslip {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; border-bottom: 2px solid #333; padding-bottom: 15px; margin-bottom: 20px; }}
        .company-name {{ font-size: 24px; font-weight: bold; color: #2c3e50; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th {{ background: #34495e; color: white; padding: 10px; text-align: left; }}
        td {{ padding: 8px 10px; border-bottom: 1px solid #ddd; }}
        .amount {{ text-align: right; }}
        .total-row {{ font-weight: bold; background: #ecf0f1; }}
        .net-pay {{ background: #2ecc71; color: white; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="payslip">
        <div class="header">
            <div class="company-name">{employee['employer_name']}</div>
            <div>{employee['employer_address']}</div>
        </div>
        <h2 style="text-align: center;">PAYSLIP FOR {employee['pay_date'][:7]}</h2>
        <p><strong>Employee ID:</strong> {employee['employee_id']} | <strong>Name:</strong> {employee['employee_name']}</p>
        <p><strong>Designation:</strong> {employee['designation']} | <strong>Department:</strong> {employee['department']}</p>
        <p><strong>PAN:</strong> {employee['pan']} | <strong>UAN:</strong> {employee['uan']}</p>
        <p><strong>Pay Period:</strong> {employee['pay_period_start']} to {employee['pay_period_end']}</p>
        <table>
            <tr><th>EARNINGS</th><th class="amount">AMOUNT (INR)</th><th>DEDUCTIONS</th><th class="amount">AMOUNT (INR)</th></tr>
            <tr><td>Basic Salary</td><td class="amount">{employee['earnings']['basic_salary']:,}</td><td>Provident Fund</td><td class="amount">{employee['deductions']['provident_fund']:,}</td></tr>
            <tr><td>HRA</td><td class="amount">{employee['earnings']['hra']:,}</td><td>Professional Tax</td><td class="amount">{employee['deductions']['professional_tax']:,}</td></tr>
            <tr><td>Special Allowance</td><td class="amount">{employee['earnings']['special_allowance']:,}</td><td>TDS</td><td class="amount">{employee['deductions']['tds']:,}</td></tr>
            <tr><td>Transport</td><td class="amount">{employee['earnings']['transport_allowance']:,}</td><td></td><td></td></tr>
            <tr class="total-row"><td>GROSS</td><td class="amount">{employee['gross_income']:,}</td><td>TOTAL DEDUCTIONS</td><td class="amount">{employee['total_deductions']:,}</td></tr>
            <tr class="net-pay"><td colspan="3">NET PAY</td><td class="amount">{employee['net_income']:,}</td></tr>
        </table>
        <p><strong>Bank:</strong> {employee['bank_name']} | <strong>Account:</strong> {employee['bank_account']}</p>
    </div>
</body>
</html>'''


def create_us_payslip_html(employee):
    \"\"\"Generate US-style payslip HTML\"\"\"
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Payslip - {employee['employee_name']}</title>
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; margin: 20px; background: #f0f4f8; }}
        .payslip {{ max-width: 850px; margin: 0 auto; background: white; padding: 35px; box-shadow: 0 2px 15px rgba(0,0,0,0.08); border-top: 4px solid #0066cc; }}
        .header {{ display: flex; justify-content: space-between; border-bottom: 2px solid #0066cc; padding-bottom: 20px; }}
        .company-name {{ font-size: 26px; font-weight: bold; color: #0066cc; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th {{ background: #0066cc; color: white; padding: 12px; text-align: left; }}
        td {{ padding: 10px 12px; border-bottom: 1px solid #e0e0e0; }}
        .amount {{ text-align: right; font-family: 'Courier New', monospace; }}
        .subtotal-row {{ background: #f1f5f9; font-weight: 600; }}
        .net-pay-row {{ background: #10b981; color: white; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="payslip">
        <div class="header">
            <div>
                <div class="company-name">{employee['employer_name']}</div>
                <div>{employee['employer_address']}</div>
            </div>
            <div style="text-align: right;">
                <h2>EARNINGS STATEMENT</h2>
                <div>Pay Date: {employee['pay_date']}</div>
            </div>
        </div>
        <p><strong>Employee ID:</strong> {employee['employee_id']} | <strong>Name:</strong> {employee['employee_name']}</p>
        <p><strong>Position:</strong> {employee['designation']} | <strong>Department:</strong> {employee['department']}</p>
        <p><strong>SSN:</strong> {employee['ssn']} | <strong>Period:</strong> {employee['pay_period_start']} to {employee['pay_period_end']}</p>
        <table>
            <tr><th>EARNINGS</th><th class="amount">CURRENT</th><th>DEDUCTIONS</th><th class="amount">CURRENT</th></tr>
            <tr><td>Regular Pay</td><td class="amount">${employee['earnings']['regular_pay']:,.2f}</td><td>Federal Tax</td><td class="amount">${employee['deductions']['federal_tax']:,.2f}</td></tr>
            <tr><td></td><td></td><td>State Tax</td><td class="amount">${employee['deductions']['state_tax']:,.2f}</td></tr>
            <tr><td></td><td></td><td>Social Security</td><td class="amount">${employee['deductions']['social_security']:,.2f}</td></tr>
            <tr><td></td><td></td><td>Medicare</td><td class="amount">${employee['deductions']['medicare']:,.2f}</td></tr>
            <tr><td></td><td></td><td>Health Insurance</td><td class="amount">${employee['deductions']['health_insurance']:,.2f}</td></tr>
            <tr><td></td><td></td><td>401(k)</td><td class="amount">${employee['deductions']['retirement_401k']:,.2f}</td></tr>
            <tr class="subtotal-row"><td>GROSS</td><td class="amount">${employee['gross_income']:,.2f}</td><td>TOTAL DEDUCTIONS</td><td class="amount">${employee['total_deductions']:,.2f}</td></tr>
            <tr class="net-pay-row"><td colspan="3">NET PAY</td><td class="amount">${employee['net_income']:,.2f}</td></tr>
        </table>
        <p><strong>Routing:</strong> {employee['routing_number']} | <strong>Account:</strong> {employee['account_number']}</p>
    </div>
</body>
</html>'''


def main():
    parser = argparse.ArgumentParser(description='Generate synthetic payslip dataset')
    parser.add_argument('--count', type=int, default=10, help='Number of payslips to generate')
    parser.add_argument('--output-dir', type=str, default='.', help='Output directory')
    parser.add_argument('--seed', type=int, default=None, help='Random seed for reproducibility')
    
    args = parser.parse_args()
    
    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    print(f"Generating {args.count} synthetic payslips...")
    employees = generate_employee_data(args.count, args.seed)
    
    gt_file = output_path / 'payslip_ground_truth.json'
    with open(gt_file, 'w') as f:
        json.dump(employees, f, indent=2)
    print(f"✓ Ground truth saved: {gt_file}")
    
    for i, employee in enumerate(employees, 1):
        filename = f"payslip_{i:03d}_{employee['country']}_{employee['employee_id']}.html"
        filepath = output_path / filename
        
        if employee['country'] == 'India':
            html_content = create_india_payslip_html(employee)
        else:
            html_content = create_us_payslip_html(employee)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    india_count = sum(1 for e in employees if e['country'] == 'India')
    usa_count = args.count - india_count
    
    print(f"✓ Generated {args.count} HTML payslips ({india_count} India, {usa_count} USA)")
    print(f"✓ Files saved in: {output_path}")
    print("\\nNext steps:")
    print("1. Convert HTML to PDF using browser or wkhtmltopdf")
    print("2. Convert PDF to images if needed (pdf2image)")
    print("3. Use payslip_ground_truth.json for training/evaluation")


if __name__ == '__main__':
    main()
\"\"\"

with open('generate_more_payslips.py', 'w', encoding='utf-8') as f:
    f.write(generator_script)

print("✓ Created generate_more_payslips.py")
print("\nUsage examples:")
print("  python generate_more_payslips.py --count 50")
print("  python generate_more_payslips.py --count 100 --output-dir ./dataset --seed 42")
