from flask import Flask, g, jsonify

from api import myapi
from core import db, oauth
from mixer.backend.flask import mixer
from resources.users import users_api
from resources.todos import todos_api
from validator import RequestValidator

import config
from resources.todos import todos_api

def create_app():
    app = Flask(__name__)

    app.config.from_object('config')

    db.init_app(app)
    
    oauth.init_app(app)
    oauth._validator = RequestValidator()

    app.register_blueprint(myapi)
    app.register_blueprint(todos_api)

    return app

if __name__ == '__main__':
    # Enable Flask-OAuthlib logging for this application.
    import logging
    logger = logging.getLogger('flask_oauthlib')
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.DEBUG)

    app = create_app()
    db.create_all(app=app)

    app.run(debug=config.DEBUG, host=config.HOST, port=config.PORT)