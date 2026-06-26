import ast
from pathlib import Path
import jsonlines
# Resolve project root directory
PROJECT_ROOT = Path(__file__).resolve().parents[2]

print("PROJECT_ROOT:", PROJECT_ROOT)
# Path to the data file
jsonl_path = PROJECT_ROOT / "dev" / "data" / "templates-enriched-data.jsonl"

# Read and parse the templates from the python-literal-structured jsonl file
# with open(jsonl_path, "r", encoding="utf-8") as f:
#     templates = ast.literal_eval(f.read())

with jsonlines.open(jsonl_path, mode="r") as reader:
    templates = list(reader)

print(f"Loaded {len(templates)} templates.")

from dotenv import load_dotenv
from supabase import create_client
import os

# Load environment variables from .env located at the project root
load_dotenv(dotenv_path=PROJECT_ROOT / ".env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "SUPABASE_URL and SUPABASE_KEY must be defined in the .env file."
    )

# Create client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("Connected to Supabase")

print(f"Preparing to insert {len(templates)} templates...")

for template in templates:
    print(f"Inserting {template['id']}...")
    print("Template:", template)
    result = (
        supabase
        .table("templates")
        .upsert(
            template,
            on_conflict="id"
        )
        .execute()
    )

    print(f"✓ {template['id']} inserted")

print("Done.")