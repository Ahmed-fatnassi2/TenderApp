from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Initialize extensions here (without app)
db = SQLAlchemy()
migrate = Migrate()