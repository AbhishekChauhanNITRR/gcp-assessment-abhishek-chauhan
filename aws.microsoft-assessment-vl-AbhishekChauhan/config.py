import os
from dotenv import load_dotenv

load_dotenv()

USE_MOCK = os.getenv("USE_MOCK_SERVICES", "true").lower() == "true"
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "gen-lang-client-0573226548")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
DATA_SET_ID = "gcp_dataset"
TABLE_NAME = "sales_cleaned"
