import os
from dotenv import load_dotenv

# Load env BEFORE importing anything from CartIQ
load_dotenv()

from sqlalchemy import inspect
from database.connection import engine, init_db

def verify():
    print("Checking Database Engine...")
    print(f"Engine URL dialect: {engine.url.drivername}")
    
    if "postgres" not in engine.url.drivername:
        print("FAIL: Engine is not using postgresql!")
        return False
        
    print("Testing init_db()...")
    try:
        init_db()
    except Exception as e:
        print(f"FAIL: init_db threw exception: {e}")
        return False
    
    print("Testing Table Existence...")
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"Tables found: {tables}")
    
    required = ["users", "products", "product_offers"]
    for req in required:
        if req not in tables:
            print(f"FAIL: Missing table {req}")
            return False
            
    print("SUCCESS: All verification passed.")
    return True

if __name__ == "__main__":
    verify()
