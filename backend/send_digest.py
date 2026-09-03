import os
from pathlib import Path

# Load .env manually
env_path = Path('.env')
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                os.environ[key] = value

from services.daily_tender_service import DailyTenderService
import logging
logging.basicConfig(level=logging.INFO)

print("📧 Sending daily digest...")
service = DailyTenderService()

# Send the email
result = service.send_daily_digest()
print(f"\n✅ Email sent: {result}")
