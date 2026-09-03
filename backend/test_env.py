from dotenv import load_dotenv
import os

load_dotenv()
print(f"OPENRAG_URL={os.getenv('OPENRAG_URL')}")
print(f"DATABASE_URL={os.getenv('DATABASE_URL')}")
