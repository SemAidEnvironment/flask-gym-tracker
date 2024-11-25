from app import create_app
from flask_sqlalchemy import SQLAlchemy

def setup_database():
    # Create the Flask app instance
    app = create_app()

    # Import models inside the app context to ensure proper initialization
    with app.app_context():
        from app.models import db, User  # Import only after app context is set up

        # Create all tables
        print("Creating database tables...")
        db.create_all()

        # Add initial users if they don't already exist
        if not User.query.first():  # Check if any user exists
            print("Adding initial users...")
            users = [User(name="Sem"), User(name="Zina")]
            db.session.add_all(users)
            db.session.commit()
            print("Users 'Sem' and 'Zina' added to the database.")
        else:
            print("Users already exist. Skipping user creation.")

if __name__ == "__main__":
    setup_database()
