from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_talisman import Talisman
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
import config

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
jwt = JWTManager()
cors = CORS(resources={r"/*": {"origins": config.Config.CORS_ALLOWED_ORIGINS}})
talisman = Talisman()
flask_instrumentor = FlaskInstrumentor()
req_instrumentor = RequestsInstrumentor()