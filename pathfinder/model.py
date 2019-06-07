from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from pathfinder import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(db.Model, UserMixin):

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(60), index=True, unique=True)
    telephone = db.Column(db.String(60), index=True, unique=True)
    full_names = db.Column(db.String(60), index=True)
    password_hash = db.Column(db.String(128))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    police_id = db.Column(db.Integer, db.ForeignKey('police.id'))
    is_admin = db.Column(db.Boolean, default=False)
    crimescene = db.relationship('CrimeScene', backref='casefiler', lazy=True)

    @property
    def password(self):
        """
        Prevent password from being accessed
        """
        raise AttributeError('password is not a readable format.')

    @password.setter
    def password(self, password):
        """
        set password to a hashed password
        """
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """
        check if hashed password matches the actual password
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Role(db.Model):
    """
    create a Role table
    """
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), unique=True)
    description = db.Column(db.String(200))
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role: {}>'.format(self.name)


class CrimeScene(db.Model):

    __tablename__ = "crimescenes"

    id = db.Column(db.Integer, primary_key=True)
    longitude = db.Column(db.String(128), nullable=False)
    latitude = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_file = db.Column(db.String(50), nullable=True)
    date_posted = db.Column(db.Date, nullable=False,
                            default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    police_id = db.Column(db.Integer, db.ForeignKey(
        'police.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey(
        'categories.id'), nullable=False)
    location = db.Column(db.String(300), nullable=False)
    arrest = db.Column(db.Boolean, default=False)
    domestic = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return '<CrimeScene: {}>'.format(self.description, self.location)


class Category(db.Model):

    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    violet_type = db.Column(db.String(60), nullable=False)
    crimescene = db.relationship('CrimeScene', backref='scene', lazy='dynamic')
    category_color = db.Column(db.String(60), nullable=False)


class Police(db.Model):

    __tablename__ = "police"

    id = db.Column(db.Integer, primary_key=True)
    StationName = db.Column(db.String(100), nullable=False)
    division = db.Column(db.String(60), nullable=False)
    crimescene = db.relationship(
        'CrimeScene', backref='policeonscene', lazy=True)
    user = db.relationship('User', backref='officer', lazy=True)
