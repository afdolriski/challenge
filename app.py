from flask import Flask, g, jsonify

from api import myapi
from core import db, oauth
from mixer.backend.flask import mixer
from resources.albums import albums_api
from resources.comments import comments_api
from resources.photos import photos_api
from resources.posts import posts_api
from resources.todos import todos_api
from resources.users import users_api

from validator import RequestValidator
import config

url_prefix = '/api/v1'

def create_app():
    app = Flask(__name__)

    app.config.from_object('config')

    db.init_app(app)    
    oauth.init_app(app)
    oauth._validator = RequestValidator()

    app.register_blueprint(myapi, url_prefix=url_prefix)
    app.register_blueprint(todos_api, url_prefix=url_prefix)
    app.register_blueprint(users_api, url_prefix=url_prefix)
    app.register_blueprint(posts_api, url_prefix=url_prefix)
    app.register_blueprint(photos_api, url_prefix=url_prefix)
    app.register_blueprint(comments_api, url_prefix=url_prefix)
    app.register_blueprint(albums_api, url_prefix=url_prefix)

    return app

if __name__ == '__main__':
    import logging
    logger = logging.getLogger('flask_oauthlib')
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.DEBUG)

    app = create_app()
    db.create_all(app=app)

    app.run(debug=config.DEBUG, host=config.HOST, port=config.PORT)