from datetime import datetime, timedelta
from werkzeug.security import gen_salt
from core import db
import bcrypt

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True)
    name = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    hashpw = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    website = db.Column(db.String(20), nullable=False)
    street = db.Column(db.String(20))
    suite = db.Column(db.String(20))
    city = db.Column(db.String(20))
    zipcode = db.Column(db.String(10))
    lat = db.Column(db.String(10))
    lng = db.Column(db.String(10))
    cmpName = db.Column(db.String(20))
    catchPrase = db.Column(db.String(30))
    bs = db.Column(db.String(30))


    @staticmethod
    def find_with_password(username, password, *args, **kwargs):
        user = User.query.filter_by(username=username).first()
        if user and password:
            encodedpw = password.encode('utf-8')
            userhash = user.hashpw.encode('utf-8')
            return User.query.filter(
                User.username == username,
                User.hashpw == bcrypt.hashpw(encodedpw, userhash)
            ).first()
        else:
            return user

    @staticmethod
    def save(**kwargs):
        """ Create a new User record with the supplied username and password.

        :param username: Username of the user.
        :param password: Password of the user.
        """
        print(kwargs)
        salt = bcrypt.gensalt()
        hash = bcrypt.hashpw(kwargs['password'].encode('utf-8'), salt)
        kwargs['hashpw'] = hash
        kwargs.pop('password', None)
        user = User(**kwargs)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def all():
        return User.query.all()


class Client(db.Model):
    client_id = db.Column(db.String(40), primary_key=True)
    client_type = db.Column(db.String(40))

    @property
    def allowed_grant_types(self):
        return ['password']

    @property
    def default_scopes(self):
        return []

    @staticmethod
    def find(id):
        return Client.query.filter_by(client_id=id).first()

    @staticmethod
    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self

    @staticmethod
    def generate():
        client = Client(client_id=gen_salt(40), client_type='public')
        db.session.add(client)
        db.session.commit()

    @staticmethod
    def all():
        return Client.query.all()

    def default_redirect_uri():
        return ''


class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.String(40), db.ForeignKey('client.client_id'),
                          nullable=False)
    client = db.relationship('Client')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User')
    token_type = db.Column(db.String(40))
    access_token = db.Column(db.String(255), unique=True)
    refresh_token = db.Column(db.String(255), unique=True)
    expires = db.Column(db.DateTime)
    scopes = ['']

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def find(access_token=None, refresh_token=None):
        if access_token:
            return Token.query.filter_by(access_token=access_token).first()
        elif refresh_token:
            return Token.query.filter_by(refresh_token=refresh_token).first()

    @staticmethod
    def save(token, request, *args, **kwargs):
        toks = Token.query.filter_by(
            client_id=request.client.client_id,
            user_id=request.user.id)

        [db.session.delete(t) for t in toks]

        expires_in = token.pop('expires_in')
        expires = datetime.utcnow() + timedelta(seconds=expires_in)

        tok = Token(
            access_token=token['access_token'],
            refresh_token=token['refresh_token'],
            token_type=token['token_type'],
            expires=expires,
            client_id=request.client.client_id,
            user_id=request.user.id,
        )
        db.session.add(tok)
        db.session.commit()

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref='posts')
    title = db.Column(db.String(40), nullable=False)
    body = db.Column(db.Text(), nullable=False)

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    postId = db.Column(db.Integer, db.ForeignKey('post.id'))
    post = db.relationship('Post', backref='comments')
    name = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    body = db.Column(db.Text(), nullable=False)

class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref='albums')
    title = db.Column(db.String(40), nullable=False)

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    albumId = db.Column(db.Integer, db.ForeignKey('album.id'))
    album = db.relationship('Album', backref='photos')
    title = db.Column(db.String(40), nullable=False)
    url = db.Column(db.String(40), nullable=False)
    thumbnailUrl = db.Column(db.String(40), nullable=False)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref='todos')
    title = db.Column(db.String(40), nullable=False)
    compledted = db.Column(db.Boolean(), default=False)

