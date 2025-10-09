from supabase import create_client, Client
from dotenv import load_dotenv
import os
load_dotenv()

def connection():
     url: str = os.getenv("SUPABASE_URL")
     key: str = os.getenv("SUPABASE_KEY")
     try:
          supabase: Client = create_client(url, key)
          return supabase
     except Exception as e:
          print(e)