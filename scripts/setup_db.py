"""Database setup script.

This script initializes the database, creates tables, and enables
the pgvector extension.
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask
from dotenv import load_dotenv
from sqlalchemy import text

from app import app
from database import db, init_db

load_dotenv()


def setup_database() -> None:
    """Set up database schema and extensions.

    Creates all tables and enables pgvector extension.
    """
    with app.app_context():
        print('🔧 Setting up database...')
        
        # Initialize database (creates tables)
        init_db(app)
        
        # Run migration script if needed
        migration_file = os.path.join(
            os.path.dirname(__file__),
            '..',
            'migrations',
            '001_initial_schema.sql'
        )
        
        if os.path.exists(migration_file):
            print('📄 Running migration script...')
            with open(migration_file, 'r') as f:
                migration_sql = f.read()
            
            # Execute migration SQL
            try:
                db.session.execute(text(migration_sql))
                db.session.commit()
                print('✅ Migration completed successfully')
            except Exception as e:
                print(f'⚠️  Migration warning: {e}')
                db.session.rollback()
        
        print('✨ Database setup complete!')


if __name__ == '__main__':
    setup_database()



