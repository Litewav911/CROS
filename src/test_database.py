from database import DATABASE_PATH, engine


print(f"Database location: {DATABASE_PATH}")

with engine.connect():
    print("Database connection successful!")