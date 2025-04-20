import os
import logging
from app import db, app

def init_database():
    """
    Initialize the database and create all tables.
    """
    try:
        with app.app_context():
            db.create_all()
            logging.info("Database tables created successfully")
    except Exception as e:
        logging.error(f"Error initializing database: {str(e)}")
        raise

if __name__ == "__main__":
    init_database()
