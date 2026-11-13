import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker

# Load environment variables from .env
load_dotenv()


#Build PostgreSQL connection URL
DATABASE_URL = URL.create(
    drivername="postgresql+psycopg",
    username=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
    host=os.environ["DB_HOST"],
    port=int(os.environ["DB_PORT"]),
    database=os.environ["DB_NAME"]

)

# Create SQLAlchemy engine and session
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


# Test PostgreSQL connection
def test_connection():
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT current_database();")
        )
        print("Connected to:", result.scalar())


if __name__ == "__main__":
    test_connection()