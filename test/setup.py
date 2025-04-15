from app.database import Base, engine
from app.models import User, Receipt
from sqlalchemy.exc import SQLAlchemyError

def create_test_db():
    try:
        print("🧹 Dropping existing test tables...")
        Base.metadata.drop_all(bind=engine)
        print("🛠️ Creating test tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ Test database setup complete.")
    except SQLAlchemyError as e:
        print("❌ Error setting up test DB:", e)

if __name__ == "__main__":
    create_test_db()
