from flask import abort
from datetime import datetime, timedelta
from werkzeug.security import gen_salt
from core import db
import bcrypt

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True, nullable=False)
    name = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    hashpw = db.Column(db.String(80), nullable=False)
    phone = db.Column(db.String(15))
    website = db.Column(db.String(20))
    street = db.Column(db.String(20))
    suite = db.Column(db.String(20))
    city = db.Column(db.String(20))
    zipcode = db.Column(db.String(10))
    lat = db.Column(db.String(10))
    lng = db.Column(db.String(10))
    cmpName = db.Column(db.String(20))
    catchPhrase = db.Column(db.String(30))
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
            abort(404)

    @staticmethod
    def save(**kwargs):
        salt = bcrypt.gensalt()
        hash = bcrypt.hashpw(kwargs['password'].encode('utf-8'), salt)
        kwargs['hashpw'] = hash
        kwargs.pop('password', None)
        user = User(**kwargs)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def update(id, **kwargs):
        user = User.query.filter_by(id=id).update(kwargs)
        db.session.commit()
        return User.query.get(id)

    @staticmethod
    def delete(user):
        db.session.delete(user)
        db.session.commit()
        return True

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

    @staticmethod
    def save(user_id, **kwargs):
        post = Post(userId=user_id, **kwargs)
        db.session.add(post)
        db.session.commit()
        return post

    @staticmethod
    def update(id, **kwargs):
        post = Post.query.filter_by(id=id).update(kwargs)
        if post:
            db.session.commit()
        return Post.query.filter_by(id=id).first()

    @staticmethod
    def delete(post):
        db.session.delete(post)
        db.session.commit()
        return True



class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    postId = db.Column(db.Integer, db.ForeignKey('post.id'))
    post = db.relationship('Post', backref='comments')
    name = db.Column(db.String(40), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    body = db.Column(db.Text(), nullable=False)

    @staticmethod
    def save(**kwargs):
        comment = Comment(**kwargs)
        db.session.add(comment)
        db.session.commit()
        return comment

    @staticmethod
    def update(id, **kwargs):
        comment = Comment.query.filter_by(id=id).update(kwargs)
        db.session.commit()
        return Comment.query.get(id)

    @staticmethod
    def delete(comment):
        db.session.delete(comment)
        db.session.commit()
        return True

class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref='albums')
    title = db.Column(db.String(40), nullable=False)

    @staticmethod
    def save(user_id, **kwargs):
        album = Album(userId=user_id, **kwargs)
        db.session.add(album)
        db.session.commit()
        return album

    @staticmethod
    def update(id, **kwargs):
        album = Album.query.filter_by(id=id).update(kwargs)
        db.session.commit()
        return Album.query.get(id)

    @staticmethod
    def delete(album):
        db.session.delete(album)
        db.session.commit()
        return True

class Photo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    albumId = db.Column(db.Integer, db.ForeignKey('album.id'))
    album = db.relationship('Album', backref='photos')
    title = db.Column(db.String(40), nullable=False)
    url = db.Column(db.String(40), nullable=False)
    thumbnailUrl = db.Column(db.String(40), nullable=False)

    @staticmethod
    def save(**kwargs):
        photo = Photo(**kwargs)
        db.session.add(photo)
        db.session.commit()
        return photo

    @staticmethod
    def update(id, **kwargs):
        photo = Photo.query.filter_by(id=id).update(kwargs)
        db.session.commit()
        return Photo.query.get(id)

    @staticmethod
    def delete(photo):
        db.session.delete(photo)
        db.session.commit()
        return True

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userId = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref='todos')
    title = db.Column(db.String(40), nullable=False)
    completed = db.Column(db.Boolean(), default=False)

    @staticmethod
    def save(user_id, **kwargs):
        todo = Todo(userId=user_id, **kwargs)
        db.session.add(todo)
        db.session.commit()
        return todo

    @staticmethod
    def update(id, **kwargs):
        todo = Todo.query.filter_by(id=id).update(kwargs)
        db.session.commit()
        return Todo.query.get(id)
        
    @staticmethod
    def delete(todo):
        db.session.delete(todo)
        db.session.commit()
        return True

