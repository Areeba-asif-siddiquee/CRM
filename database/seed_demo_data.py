
from datetime import date, timedelta
from database.connection import db

# ---------------------------------
# GET EXISTING DEMO CUSTOMERS
# ---------------------------------

customers = list(db.customers.find({"status": "Active"}))

if len(customers) < 5:
    print("Please add demo customers first.")
    raise SystemExit

customer_map = {
    customer["email"]: customer["_id"]
    for customer in customers
}

demo_emails = [
    "rahul.sharma@example.com",
    "priya.verma@example.com",
    "arjun.singh@example.com",
    "neha.gupta@example.com",
    "aman.khan@example.com",
    "sneha.patel@example.com",
    "rohit.mishra@example.com",
    "ananya.das@example.com",
    "vikram.yadav@example.com",
    "aisha.ali@example.com",
    "karan.mehta@example.com",
    "pooja.jain@example.com",
    "imran.siddiqui@example.com",
    "riya.kapoor@example.com"
]

available_emails = [
    email for email in demo_emails if email in customer_map
]

if len(available_emails) < 5:
    print("Could not find enough matching demo customers.")
    print("Run the customer seed script first.")
    raise SystemExit

today = date.today()

# ---------------------------------
# 1. DEMO LEADS
# ---------------------------------

demo_leads = [
    {
        "lead_name": "Rohan Malhotra",
        "email": "rohan.malhotra@example.com",
        "phone": "9000000101",
        "company_name": "Malhotra Technologies",
        "source": "Website",
        "status": "New",
        "expected_value": 75000,
        "notes": "Interested in CRM software."
    },
    {
        "lead_name": "Simran Kaur",
        "email": "simran.kaur@example.com",
        "phone": "9000000102",
        "company_name": "Kaur Enterprises",
        "source": "Social Media",
        "status": "Contacted",
        "expected_value": 95000,
        "notes": "Initial discussion completed."
    },
    {
        "lead_name": "Aditya Rao",
        "email": "aditya.rao@example.com",
        "phone": "9000000103",
        "company_name": "Rao Industries",
        "source": "Referral",
        "status": "Qualified",
        "expected_value": 150000,
        "notes": "Interested in a business package."
    },
    {
        "lead_name": "Meera Nair",
        "email": "meera.nair@example.com",
        "phone": "9000000104",
        "company_name": "Nair Solutions",
        "source": "Website",
        "status": "New",
        "expected_value": 60000,
        "notes": "Requested product details."
    },
    {
        "lead_name": "Kabir Ahmed",
        "email": "kabir.ahmed@example.com",
        "phone": "9000000105",
        "company_name": "Ahmed Digital",
        "source": "Social Media",
        "status": "Contacted",
        "expected_value": 110000,
        "notes": "Follow-up discussion required."
    },
    {
        "lead_name": "Ishita Roy",
        "email": "ishita.roy@example.com",
        "phone": "9000000106",
        "company_name": "Roy Consulting",
        "source": "Referral",
        "status": "Qualified",
        "expected_value": 125000,
        "notes": "Potential long-term customer."
    },
    {
        "lead_name": "Dev Malhotra",
        "email": "dev.malhotra@example.com",
        "phone": "9000000107",
        "company_name": "Malhotra Retail",
        "source": "Cold Call",
        "status": "New",
        "expected_value": 50000,
        "notes": "Needs an introductory meeting."
    },
    {
        "lead_name": "Tanya Bose",
        "email": "tanya.bose@example.com",
        "phone": "9000000108",
        "company_name": "Bose Enterprises",
        "source": "Website",
        "status": "Contacted",
        "expected_value": 85000,
        "notes": "Product presentation shared."
    },
    {
        "lead_name": "Nikhil Sethi",
        "email": "nikhil.sethi@example.com",
        "phone": "9000000109",
        "company_name": "Sethi Technologies",
        "source": "Referral",
        "status": "Qualified",
        "expected_value": 175000,
        "notes": "High-value sales opportunity."
    },
    {
        "lead_name": "Fatima Noor",
        "email": "fatima.noor@example.com",
        "phone": "9000000110",
        "company_name": "Noor Enterprises",
        "source": "Social Media",
        "status": "New",
        "expected_value": 70000,
        "notes": "Interested in a product demonstration."
    }
]

lead_inserted = 0

for lead in demo_leads:
    if db.leads.find_one({"email": lead["email"]}):
        print("Skipped lead:", lead["lead_name"])
        continue

    lead["assigned_to"] = "admin"
    lead["created_at"] = today.isoformat()

    db.leads.insert_one(lead)
    lead_inserted += 1
    print("Added lead:", lead["lead_name"])


# ---------------------------------
# 2. DEMO OPPORTUNITIES
# ---------------------------------

opportunity_data = [
    ("CRM Enterprise Package", 150000, "Qualification", 30),
    ("Annual Software Contract", 220000, "Proposal", 60),
    ("Business Automation Project", 180000, "Negotiation", 80),
    ("Digital Transformation Deal", 300000, "Proposal", 50),
    ("Customer Support Platform", 95000, "Qualification", 20),
    ("Retail Management System", 125000, "Negotiation", 70),
    ("Enterprise Analytics Package", 275000, "Proposal", 55),
    ("Small Business CRM", 65000, "Won", 100),
    ("Marketing Automation Deal", 110000, "Lost", 0),
    ("Sales Tracking Solution", 85000, "Qualification", 25)
]

opportunity_inserted = 0

for index, item in enumerate(opportunity_data):
    name, amount, stage, probability = item
    email = available_emails[index % len(available_emails)]
    customer_id = customer_map[email]

    if db.opportunities.find_one({"opportunity_name": name}):
        print("Skipped opportunity:", name)
        continue

    opportunity = {
        "opportunity_name": name,
        "customer_id": str(customer_id),
        "amount": amount,
        "stage": stage,
        "probability": probability,
        "expected_close_date": (
            today + timedelta(days=30 + index * 5)
        ).isoformat(),
        "assigned_to": "admin",
        "notes": "Fictional demonstration opportunity.",
        "weighted_value": amount * probability / 100,
        "created_at": today.isoformat()
    }

    db.opportunities.insert_one(opportunity)
    opportunity_inserted += 1
    print("Added opportunity:", name)


# ---------------------------------
# 3. DEMO FOLLOW-UPS
# ---------------------------------

followup_subjects = [
    "Initial customer discussion",
    "Product demonstration",
    "Pricing discussion",
    "Contract follow-up",
    "Requirement gathering",
    "Project status discussion",
    "Annual subscription discussion",
    "Customer feedback call",
    "Proposal review meeting",
    "Final negotiation"
]

followup_inserted = 0

for index, subject in enumerate(followup_subjects):
    email = available_emails[index % len(available_emails)]
    customer_id = customer_map[email]

    if db.followups.find_one({
        "subject": subject,
        "customer_id": str(customer_id)
    }):
        print("Skipped follow-up:", subject)
        continue

    followup = {
        "customer_id": str(customer_id),
        "subject": subject,
        "followup_date": (
            today + timedelta(days=index + 1)
        ).isoformat(),
        "followup_type": ["Call", "Meeting", "Email", "Task"][index % 4],
        "status": "Planned",
        "remarks": "Demo follow-up activity.",
        "assigned_to": "admin",
        "created_at": today.isoformat()
    }

    db.followups.insert_one(followup)
    followup_inserted += 1
    print("Added follow-up:", subject)


# ---------------------------------
# 4. DEMO ACTIVITIES
# ---------------------------------

activity_subjects = [
    "Introduction call",
    "Product presentation",
    "Pricing email sent",
    "Business meeting",
    "Requirements discussion",
    "Proposal preparation",
    "Customer feedback call",
    "Contract review",
    "Demo session",
    "Sales discussion"
]

activity_inserted = 0

for index, subject in enumerate(activity_subjects):
    email = available_emails[index % len(available_emails)]
    customer_id = customer_map[email]

    if db.activities.find_one({"subject": subject}):
        print("Skipped activity:", subject)
        continue

    activity = {
        "activity_type": ["Call", "Meeting", "Email", "Task"][index % 4],
        "subject": subject,
        "description": "Fictional activity created for CRM demonstration.",
        "activity_date": (
            today + timedelta(days=index + 1)
        ).isoformat(),
        "customer_id": str(customer_id),
        "assigned_to": "admin",
        "created_at": today.isoformat()
    }

    db.activities.insert_one(activity)
    activity_inserted += 1
    print("Added activity:", subject)


# ---------------------------------
# FINAL SUMMARY
# ---------------------------------

print("\n========== DEMO DATA SUMMARY ==========")
print("Leads added:", lead_inserted)
print("Opportunities added:", opportunity_inserted)
print("Follow-ups added:", followup_inserted)
print("Activities added:", activity_inserted)
print("Total new records:", (
    lead_inserted +
    opportunity_inserted +
    followup_inserted +
    activity_inserted
))
print("=======================================")
