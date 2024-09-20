import os

import urllib3
from flask_restx import Api


def create_api(app, version, title, description, iam_server):
    authorizations = {
        'apikey': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            "description": "Enter: **'Bearer &lt;JWT&gt;'**, where JWT is the access token"
        },
        'oauth2': {
            'type': 'oauth2',
            'flow': 'password',  # implicit, accesCode
            'authorizationUrl': f"{iam_server}/oauth2/authorize",
            'tokenUrl': f'{iam_server}/oauth2/login',
            'scopes': {
                'read': 'Read access',
                'write': 'Write access'
            },
            'clientId': 'client',  # Your client ID
            'clientSecret': 'secret',  # Your client secret
            'realm': 'local',
            'username': 'admin',  # User's username
            'password': 'admin'  # User's password
        }
    }
    api = Api(
        app=app,
        # doc=False,
        version=version,
        title=title,
        description=description,
        security=[
            'apikey', {'oauth2': ['read', 'write']}  # , {"bearer": []}
        ],
        authorizations=authorizations
    )
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    return api


def create_app(app):
    app.config['JWT_ALGORITHM'] = 'RS256'

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    app.config.from_object('config.Config')

    app.debug = False
    app.testing = False
    try:
        if not app.config['SECRET_KEY']:
            raise ValueError("No SECRET_KEY set for Flask application")
        if not app.config['TOKEN_URL']:
            raise ValueError("No TOKEN_URL set for Flask application")
    except KeyError:
        pass

    # create instances
    # if dbInstance:
    #     db = SQLAlchemy()
    #     db.init_app(app)
    #     migrate = Migrate()
    #     migrate.init_app(app, db)
    #
    # bcrypt = Bcrypt()
    # jwt = JWTManager()
    # cors = CORS(resources={r"/*": {"origins": "*"}})
    # talisman = Talisman()
    #
    # cors.init_app(app)
    # bcrypt.init_app(app)
    # jwt.init_app(app)
    # talisman.init_app(app, content_security_policy=None, force_https=True)
    #
    # if dbInstance:
    #     with app.app_context():
    #         db.create_all()

    return app
