
import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME", "AcxiomCRM")

if not MONGODB_URI:
    raise ValueError("MONGODB_URI is missing from the .env file")

# Connect to MongoDB Atlas
client = MongoClient(
    MONGODB_URI,
    serverSelectionTimeoutMS=5000
)

# Select AcxiomCRM database
db = client[DATABASE_NAME]

def test_connection():
    try:
        client.admin.command("ping")
        print("MongoDB Atlas connected successfully!")
        return True
    except Exception as error:
        print("MongoDB connection failed:", error)
        return False
