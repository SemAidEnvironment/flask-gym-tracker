from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Create the SQLAlchemy object
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Configure the app
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gym_tracker.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize extensions
    db.init_app(app)

    # Register custom filter for strftime
    @app.template_filter('strftime')
    def format_datetime(value, format='%Y-%m-%d'):
        """Custom filter for strftime in Jinja2."""
        if isinstance(value, datetime):
            return value.strftime(format)
        return value

    app.jinja_env.filters['strftime'] = format_datetime
    # Register context processor for the current date
    @app.context_processor
    def inject_now():
        return {'now': datetime.utcnow()}

    # Create database tables
    with app.app_context():
        db.create_all()

        from .models import User
        if not User.query.first():
            users = [User(name="Sem"), User(name="Zina")]
            db.session.add_all(users)
            db.session.commit()
    # Register blueprints
    from .routes import main
    app.register_blueprint(main)

    return app
