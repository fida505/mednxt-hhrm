from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings

# Handle postgres:// vs postgresql:// for Railway
DATABASE_URL = settings.DATABASE_URL
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# SQLite needs check_same_thread=False
connect_args = {}
if "sqlite" in DATABASE_URL:
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables."""
    from app.models import department, designation, employee, audit, document  # noqa
    Base.metadata.create_all(bind=engine)

    # Automatic schema upgrade for existing DBs on Railway
    try:
        with engine.connect() as conn:
            # Check if file_size exists, if not, it will throw an exception
            conn.execute(text("SELECT file_size FROM employee_documents LIMIT 1"))
    except Exception:
        # Column doesn't exist, alter the table
        try:
            with engine.connect() as conn:
                if engine.name == "postgresql":
                    conn.execute(text("ALTER TABLE employee_documents ADD COLUMN file_size BIGINT"))
                    conn.execute(text("ALTER TABLE employee_documents ADD COLUMN file_data BYTEA"))
                else:
                    conn.execute(text("ALTER TABLE employee_documents ADD COLUMN file_size BIGINT"))
                    conn.execute(text("ALTER TABLE employee_documents ADD COLUMN file_data BLOB"))
                conn.commit()
        except Exception as e:
            print(f"Schema update error: {e}")
