
from datetime import datetime
from database.connection import db

demo_customers = [
    {
        "customer_name": "Rahul Sharma",
        "email": "rahul.sharma@example.com",
        "phone": "9000000001",
        "company_name": "Sharma Enterprises",
        "city": "Aligarh",
        "state": "Uttar Pradesh",
        "address": "Civil Lines",
    },
    {
        "customer_name": "Priya Verma",
        "email": "priya.verma@example.com",
        "phone": "9000000002",
        "company_name": "Verma Technologies",
        "city": "Delhi",
        "state": "Delhi",
        "address": "Connaught Place",
    },
    {
        "customer_name": "Arjun Singh",
        "email": "arjun.singh@example.com",
        "phone": "9000000003",
        "company_name": "Singh Traders",
        "city": "Lucknow",
        "state": "Uttar Pradesh",
        "address": "Hazratganj",
    },
    {
        "customer_name": "Neha Gupta",
        "email": "neha.gupta@example.com",
        "phone": "9000000004",
        "company_name": "Gupta Solutions",
        "city": "Noida",
        "state": "Uttar Pradesh",
        "address": "Sector 18",
    },
    {
        "customer_name": "Aman Khan",
        "email": "aman.khan@example.com",
        "phone": "9000000005",
        "company_name": "Khan Industries",
        "city": "Aligarh",
        "state": "Uttar Pradesh",
        "address": "Medical Road",
    },
    {
        "customer_name": "Sneha Patel",
        "email": "sneha.patel@example.com",
        "phone": "9000000006",
        "company_name": "Patel Enterprises",
        "city": "Jaipur",
        "state": "Rajasthan",
        "address": "Malviya Nagar",
    },
    {
        "customer_name": "Rohit Mishra",
        "email": "rohit.mishra@example.com",
        "phone": "9000000007",
        "company_name": "Mishra Consulting",
        "city": "Kanpur",
        "state": "Uttar Pradesh",
        "address": "Swaroop Nagar",
    },
    {
        "customer_name": "Ananya Das",
        "email": "ananya.das@example.com",
        "phone": "9000000008",
        "company_name": "Das Innovations",
        "city": "Kolkata",
        "state": "West Bengal",
        "address": "Salt Lake",
    },
    {
        "customer_name": "Vikram Yadav",
        "email": "vikram.yadav@example.com",
        "phone": "9000000009",
        "company_name": "Yadav Corporation",
        "city": "Agra",
        "state": "Uttar Pradesh",
        "address": "Sanjay Place",
    },
    {
        "customer_name": "Aisha Ali",
        "email": "aisha.ali@example.com",
        "phone": "9000000010",
        "company_name": "Ali Solutions",
        "city": "Lucknow",
        "state": "Uttar Pradesh",
        "address": "Gomti Nagar",
    },
    {
        "customer_name": "Karan Mehta",
        "email": "karan.mehta@example.com",
        "phone": "9000000011",
        "company_name": "Mehta Digital",
        "city": "Mumbai",
        "state": "Maharashtra",
        "address": "Andheri",
    },
    {
        "customer_name": "Pooja Jain",
        "email": "pooja.jain@example.com",
        "phone": "9000000012",
        "company_name": "Jain Associates",
        "city": "Bhopal",
        "state": "Madhya Pradesh",
        "address": "MP Nagar",
    },
    {
        "customer_name": "Imran Siddiqui",
        "email": "imran.siddiqui@example.com",
        "phone": "9000000013",
        "company_name": "Siddiqui Enterprises",
        "city": "Aligarh",
        "state": "Uttar Pradesh",
        "address": "Dodpur",
    },
    {
        "customer_name": "Riya Kapoor",
        "email": "riya.kapoor@example.com",
        "phone": "9000000014",
        "company_name": "Kapoor Technologies",
        "city": "Gurugram",
        "state": "Haryana",
        "address": "Sector 29",
    },
]

inserted = 0
skipped = 0

for customer in demo_customers:
    existing = db.customers.find_one({
        "$or": [
            {"email": customer["email"]},
            {"phone": customer["phone"]}
        ]
    })

    if existing:
        print(f"Skipped: {customer['customer_name']} (already exists)")
        skipped += 1
        continue

    customer["status"] = "Active"
    customer["assigned_to"] = "admin"
    customer["created_at"] = datetime.now()

    db.customers.insert_one(customer)

    print(f"Added: {customer['customer_name']}")
    inserted += 1

print("\n========== IMPORT SUMMARY ==========")
print(f"Inserted: {inserted}")
print(f"Skipped: {skipped}")
print(f"Total processed: {inserted + skipped}")
