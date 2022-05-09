from . import db
from sqlalchemy import func
from flask_login import UserMixin


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    tracker = db.relationship('Tracker', cascade='all, delete-orphan', backref='user')


class Tracker(db.Model):
    __tablename__ = 'tracker'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    description = db.Column(db.String, nullable=False)
    type = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    options = db.relationship('Options', cascade='all, delete-orphan', backref='tracker')
    logs = db.relationship('Log', cascade='all, delete-orphan', backref='tracker')


class Options(db.Model):
    __tablename__ = 'options'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    tracker_id = db.Column(db.Integer, db.ForeignKey("tracker.id"), nullable=False)
    name = db.Column(db.String, nullable=False, unique=True)


class Log(db.Model):
    __tablename__ = 'log'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    time_stamp = db.Column(db.DateTime(timezone=True))
    value_num = db.Column(db.Float, nullable=True)
    value_time = db.Column(db.Integer, nullable=True)
    value_bool = db.Column(db.Boolean, nullable=True)
    value_mcq = db.Column(db.String, nullable=True)
    note = db.Column(db.String, nullable=True)
    last = db.Column(db.DateTime(timezone=True), default=func.now())
    tracker_id = db.Column(db.Integer, db.ForeignKey("tracker.id"), nullable=False)
