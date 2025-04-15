from app.database import Base, engine
from app.models import User, Receipt  # tous les modèles nécessaires

def create_test_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("✅ Test DB initialized.")

if __name__ == "__main__":
    create_test_db()
