
import json

# Load the ground truth data
with open('payslip_ground_truth.json', 'r') as f:
    employees_data = json.load(f)

# HTML template for India-style payslip
def create_india_payslip_html(employee):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Payslip - {employee['employee_name']}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .payslip {{
            max-width: 800px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            border-bottom: 2px solid #333;
            padding-bottom: 15px;
            margin-bottom: 20px;
        }}
        .company-name {{
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 5px;
        }}
        .company-address {{
            font-size: 12px;
            color: #666;
        }}
        .payslip-title {{
            font-size: 18px;
            font-weight: bold;
            text-align: center;
            margin: 20px 0;
            color: #34495e;
        }}
        .employee-info {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-bottom: 20px;
            font-size: 13px;
        }}
        .info-row {{
            display: flex;
            padding: 5px 0;
        }}
        .info-label {{
            font-weight: bold;
            min-width: 150px;
            color: #555;
        }}
        .info-value {{
            color: #333;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 13px;
        }}
        th {{
            background-color: #34495e;
            color: white;
            padding: 10px;
            text-align: left;
            font-weight: bold;
        }}
        td {{
            padding: 8px 10px;
            border-bottom: 1px solid #ddd;
        }}
        .amount {{
            text-align: right;
        }}
        .total-row {{
            font-weight: bold;
            background-color: #ecf0f1;
            font-size: 14px;
        }}
        .net-pay {{
            background-color: #2ecc71;
            color: white;
            font-size: 15px;
            font-weight: bold;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 15px;
            border-top: 1px solid #ddd;
            font-size: 11px;
            color: #666;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="payslip">
        <div class="header">
            <div class="company-name">{employee['employer_name']}</div>
            <div class="company-address">{employee['employer_address']}</div>
        </div>
        
        <div class="payslip-title">PAYSLIP FOR THE MONTH OF {employee['pay_date'][:7]}</div>
        
        <div class="employee-info">
            <div class="info-row">
                <span class="info-label">Employee ID:</span>
                <span class="info-value">{employee['employee_id']}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Employee Name:</span>
                <span class="info-value">{employee['employee_name']}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Designation:</span>
                <span class="info-value">{employee['designation']}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Department:</span>
                <span class="info-value">{employee['department']}</span>
            </div>
            <div class="info-row">
                <span class="info-label">PAN:</span>
                <span class="info-value">{employee['pan']}</span>
            </div>
            <div class="info-row">
                <span class="info-label">UAN:</span>
                <span class="info-value">{employee['uan']}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Pay Period:</span>
                <span class="info-value">{employee['pay_period_start']} to {employee['pay_period_end']}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Pay Date:</span>
                <span class="info-value">{employee['pay_date']}</span>
            </div>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>EARNINGS</th>
                    <th class="amount">AMOUNT (INR)</th>
                    <th>DEDUCTIONS</th>
                    <th class="amount">AMOUNT (INR)</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Basic Salary</td>
                    <td class="amount">{employee['earnings']['basic_salary']:,}</td>
                    <td>Provident Fund</td>
                    <td class="amount">{employee['deductions']['provident_fund']:,}</td>
                </tr>
                <tr>
                    <td>House Rent Allowance (HRA)</td>
                    <td class="amount">{employee['earnings']['hra']:,}</td>
                    <td>Professional Tax</td>
                    <td class="amount">{employee['deductions']['professional_tax']:,}</td>
                </tr>
                <tr>
                    <td>Special Allowance</td>
                    <td class="amount">{employee['earnings']['special_allowance']:,}</td>
                    <td>Tax Deducted at Source (TDS)</td>
                    <td class="amount">{employee['deductions']['tds']:,}</td>
                </tr>
                <tr>
                    <td>Transport Allowance</td>
                    <td class="amount">{employee['earnings']['transport_allowance']:,}</td>
                    <td></td>
                    <td class="amount"></td>
                </tr>
                <tr class="total-row">
                    <td>GROSS EARNINGS</td>
                    <td class="amount">{employee['gross_income']:,}</td>
                    <td>TOTAL DEDUCTIONS</td>
                    <td class="amount">{employee['total_deductions']:,}</td>
                </tr>
                <tr class="net-pay">
                    <td colspan="3">NET PAY (Gross Earnings - Total Deductions)</td>
                    <td class="amount">{employee['net_income']:,}</td>
                </tr>
            </tbody>
        </table>
        
        <div class="employee-info">
            <div class="info-row">
                <span class="info-label">Bank Name:</span>
                <span class="info-value">{employee['bank_name']}</span>
            </div>
            <div class="info-row">
                <span class="info-label">Account Number:</span>
                <span class="info-value">{employee['bank_account']}</span>
            </div>
        </div>
        
        <div class="footer">
            This is a computer-generated payslip and does not require a signature.<br>
            For queries, please contact HR Department at hr@company.com
        </div>
    </div>
</body>
</html>"""

# HTML template for US-style payslip
def create_us_payslip_html(employee):
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Payslip - {employee['employee_name']}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f0f4f8;
        }}
        .payslip {{
            max-width: 850px;
            margin: 0 auto;
            background-color: white;
            padding: 35px;
            box-shadow: 0 2px 15px rgba(0,0,0,0.08);
            border-top: 4px solid #0066cc;
        }}
        .header {{
            display: flex;
            justify-content: space-between;
            align-items: start;
            border-bottom: 2px solid #0066cc;
            padding-bottom: 20px;
            margin-bottom: 25px;
        }}
        .company-info {{
            flex: 1;
        }}
        .company-name {{
            font-size: 26px;
            font-weight: bold;
            color: #0066cc;
            margin-bottom: 8px;
        }}
        .company-address {{
            font-size: 13px;
            color: #666;
            line-height: 1.5;
        }}
        .payslip-title {{
            font-size: 20px;
            font-weight: bold;
            color: #333;
            text-align: right;
        }}
        .period-info {{
            text-align: right;
            font-size: 13px;
            color: #666;
            margin-top: 5px;
        }}
        .employee-section {{
            background-color: #f8f9fa;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 5px;
        }}
        .section-title {{
            font-size: 14px;
            font-weight: bold;
            color: #0066cc;
            margin-bottom: 10px;
            text-transform: uppercase;
        }}
        .employee-details {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
            font-size: 13px;
        }}
        .detail-item {{
            display: flex;
        }}
        .detail-label {{
            font-weight: 600;
            min-width: 140px;
            color: #555;
        }}
        .detail-value {{
            color: #333;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 13px;
        }}
        th {{
            background-color: #0066cc;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 12px;
        }}
        td {{
            padding: 10px 12px;
            border-bottom: 1px solid #e0e0e0;
        }}
        .amount {{
            text-align: right;
            font-family: 'Courier New', monospace;
        }}
        .subtotal-row {{
            background-color: #f1f5f9;
            font-weight: 600;
        }}
        .net-pay-row {{
            background-color: #10b981;
            color: white;
            font-size: 15px;
            font-weight: bold;
        }}
        .summary-section {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 15px;
            margin: 25px 0;
        }}
        .summary-box {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
            border-left: 3px solid #0066cc;
        }}
        .summary-label {{
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
            margin-bottom: 8px;
        }}
        .summary-amount {{
            font-size: 20px;
            font-weight: bold;
            color: #333;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 2px solid #e0e0e0;
            font-size: 11px;
            color: #888;
            text-align: center;
            line-height: 1.6;
        }}
    </style>
</head>
<body>
    <div class="payslip">
        <div class="header">
            <div class="company-info">
                <div class="company-name">{employee['employer_name']}</div>
                <div class="company-address">{employee['employer_address']}</div>
            </div>
            <div>
                <div class="payslip-title">EARNINGS STATEMENT</div>
                <div class="period-info">
                    Pay Period: {employee['pay_period_start']} to {employee['pay_period_end']}<br>
                    Pay Date: {employee['pay_date']}
                </div>
            </div>
        </div>
        
        <div class="employee-section">
            <div class="section-title">Employee Information</div>
            <div class="employee-details">
                <div class="detail-item">
                    <span class="detail-label">Employee ID:</span>
                    <span class="detail-value">{employee['employee_id']}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">SSN:</span>
                    <span class="detail-value">{employee['ssn']}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Name:</span>
                    <span class="detail-value">{employee['employee_name']}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Department:</span>
                    <span class="detail-value">{employee['department']}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Position:</span>
                    <span class="detail-value">{employee['designation']}</span>
                </div>
            </div>
        </div>
        
        <div class="summary-section">
            <div class="summary-box">
                <div class="summary-label">Gross Pay</div>
                <div class="summary-amount">${employee['gross_income']:,.2f}</div>
            </div>
            <div class="summary-box">
                <div class="summary-label">Total Deductions</div>
                <div class="summary-amount">${employee['total_deductions']:,.2f}</div>
            </div>
            <div class="summary-box" style="border-left-color: #10b981;">
                <div class="summary-label">Net Pay</div>
                <div class="summary-amount" style="color: #10b981;">${employee['net_income']:,.2f}</div>
            </div>
        </div>
        
        <table>
            <thead>
                <tr>
                    <th>EARNINGS</th>
                    <th class="amount">CURRENT</th>
                    <th>DEDUCTIONS</th>
                    <th class="amount">CURRENT</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Regular Pay</td>
                    <td class="amount">${employee['earnings']['regular_pay']:,.2f}</td>
                    <td>Federal Income Tax</td>
                    <td class="amount">${employee['deductions']['federal_tax']:,.2f}</td>
                </tr>
                <tr>
                    <td></td>
                    <td class="amount"></td>
                    <td>State Income Tax</td>
                    <td class="amount">${employee['deductions']['state_tax']:,.2f}</td>
                </tr>
                <tr>
                    <td></td>
                    <td class="amount"></td>
                    <td>Social Security</td>
                    <td class="amount">${employee['deductions']['social_security']:,.2f}</td>
                </tr>
                <tr>
                    <td></td>
                    <td class="amount"></td>
                    <td>Medicare</td>
                    <td class="amount">${employee['deductions']['medicare']:,.2f}</td>
                </tr>
                <tr>
                    <td></td>
                    <td class="amount"></td>
                    <td>Health Insurance</td>
                    <td class="amount">${employee['deductions']['health_insurance']:,.2f}</td>
                </tr>
                <tr>
                    <td></td>
                    <td class="amount"></td>
                    <td>401(k) Retirement</td>
                    <td class="amount">${employee['deductions']['retirement_401k']:,.2f}</td>
                </tr>
                <tr class="subtotal-row">
                    <td>GROSS EARNINGS</td>
                    <td class="amount">${employee['gross_income']:,.2f}</td>
                    <td>TOTAL DEDUCTIONS</td>
                    <td class="amount">${employee['total_deductions']:,.2f}</td>
                </tr>
                <tr class="net-pay-row">
                    <td colspan="3">NET PAY (Amount Deposited)</td>
                    <td class="amount">${employee['net_income']:,.2f}</td>
                </tr>
            </tbody>
        </table>
        
        <div class="employee-section">
            <div class="section-title">Direct Deposit Information</div>
            <div class="employee-details">
                <div class="detail-item">
                    <span class="detail-label">Routing Number:</span>
                    <span class="detail-value">{employee['routing_number']}</span>
                </div>
                <div class="detail-item">
                    <span class="detail-label">Account Number:</span>
                    <span class="detail-value">{employee['account_number']}</span>
                </div>
            </div>
        </div>
        
        <div class="footer">
            This is a computer-generated earnings statement and does not require a signature.<br>
            Please retain this statement for your records. For questions, contact Payroll at payroll@company.com<br>
            © 2024 {employee['employer_name']}. All rights reserved.
        </div>
    </div>
</body>
</html>"""

# Generate HTML files for each employee
for i, employee in enumerate(employees_data):
    filename = f"payslip_{i+1:02d}_{employee['country']}_{employee['employee_id']}.html"
    
    if employee['country'] == 'India':
        html_content = create_india_payslip_html(employee)
    else:
        html_content = create_us_payslip_html(employee)
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Created: {filename}")

print(f"\n✓ Generated {len(employees_data)} HTML payslips")
print("✓ Ground truth saved in: payslip_ground_truth.json")
print("\nTo convert HTML to PDF, you can:")
print("1. Open each HTML file in a browser and use Print to PDF")
print("2. Use wkhtmltopdf: wkhtmltopdf payslip_01_India_EMP8291.html payslip_01.pdf")
print("3. Use Python libraries like pdfkit or weasyprint")
