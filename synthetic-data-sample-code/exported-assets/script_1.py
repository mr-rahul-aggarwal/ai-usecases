
import json
import random
from datetime import datetime, timedelta

# Generate synthetic employee data without external dependencies
def generate_employee_data(count=10):
    employees = []
    
    first_names = ["Rajesh", "Priya", "Amit", "Sarah", "Michael", "Jennifer", "Vikram", "Anita", "David", "Emily"]
    last_names = ["Kumar", "Sharma", "Patel", "Johnson", "Smith", "Williams", "Singh", "Brown", "Davis", "Wilson"]
    
    companies_us = [
        {"name": "TechCorp Solutions Inc.", "address": "1234 Silicon Valley Blvd, San Jose, CA 95110"},
        {"name": "DataVision Analytics LLC", "address": "5678 Innovation Drive, Austin, TX 78701"},
        {"name": "CloudStream Technologies", "address": "9012 Enterprise Way, Seattle, WA 98101"},
    ]
    
    companies_india = [
        {"name": "InfoTech Solutions Pvt Ltd", "address": "Block A, Cyber Towers, HITEC City, Hyderabad 500081"},
        {"name": "Digital Innovations India Pvt Ltd", "address": "Prestige Tech Park, Marathahalli, Bengaluru 560037"},
        {"name": "Global Systems India Ltd", "address": "DLF Cyber City, Gurgaon, Haryana 122002"},
    ]
    
    for i in range(count):
        is_india = i % 2 == 0
        
        company = random.choice(companies_india if is_india else companies_us)
        employee_name = f"{random.choice(first_names)} {random.choice(last_names)}"
        
        pay_date = datetime(2024, random.randint(1, 12), random.choice([15, 28]))
        pay_period_start = pay_date - timedelta(days=30)
        pay_period_end = pay_date - timedelta(days=1)
        
        if is_india:
            basic_salary = random.randint(40000, 120000)
            hra = int(basic_salary * 0.4)
            special_allowance = int(basic_salary * 0.3)
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
                "designation": random.choice(["Software Engineer", "Senior Software Engineer", "Data Scientist", "ML Engineer", "DevOps Engineer"]),
                "department": random.choice(["Engineering", "Data Science", "Operations", "Product"]),
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
                "designation": random.choice(["Software Engineer", "Senior Software Engineer", "Data Scientist", "ML Engineer", "Product Manager"]),
                "department": random.choice(["Engineering", "Data Science", "Operations", "Product"]),
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

employees_data = generate_employee_data(10)

with open('payslip_ground_truth.json', 'w') as f:
    json.dump(employees_data, f, indent=2)

print(f"Generated {len(employees_data)} synthetic employee records")
print(f"\nDistribution: {sum(1 for e in employees_data if e['country'] == 'India')} India-style, {sum(1 for e in employees_data if e['country'] == 'USA')} USA-style")
print("\nSample India-style record:")
india_sample = next(e for e in employees_data if e['country'] == 'India')
print(json.dumps(india_sample, indent=2))
