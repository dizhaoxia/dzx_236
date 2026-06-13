from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    nickname = db.Column(db.String(50), default='学习者')
    daily_goal = db.Column(db.Integer, default=20)
    study_mode = db.Column(db.String(20), default='card')
    created_at = db.Column(db.DateTime, default=datetime.now)
    user_words = db.relationship('UserWord', backref='user', lazy=True)
    daily_records = db.relationship('DailyRecord', backref='user', lazy=True)

class Word(db.Model):
    __tablename__ = 'words'
    id = db.Column(db.Integer, primary_key=True)
    word = db.Column(db.String(100), nullable=False, index=True)
    phonetic = db.Column(db.String(200))
    meaning = db.Column(db.String(500), nullable=False)
    example = db.Column(db.Text)
    example_trans = db.Column(db.String(500))
    vocab_books = db.relationship('VocabWord', backref='word', lazy=True)

class VocabBook(db.Model):
    __tablename__ = 'vocab_books'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500))
    is_preset = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    words = db.relationship('VocabWord', backref='vocab_book', lazy=True)

class VocabWord(db.Model):
    __tablename__ = 'vocab_words'
    id = db.Column(db.Integer, primary_key=True)
    vocab_book_id = db.Column(db.Integer, db.ForeignKey('vocab_books.id'), nullable=False)
    word_id = db.Column(db.Integer, db.ForeignKey('words.id'), nullable=False)

class UserVocabBook(db.Model):
    __tablename__ = 'user_vocab_books'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    vocab_book_id = db.Column(db.Integer, db.ForeignKey('vocab_books.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    added_at = db.Column(db.DateTime, default=datetime.now)

class UserWord(db.Model):
    __tablename__ = 'user_words'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    word_id = db.Column(db.Integer, db.ForeignKey('words.id'), nullable=False)
    vocab_book_id = db.Column(db.Integer, db.ForeignKey('vocab_books.id'))
    is_custom = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='new')
    ease_factor = db.Column(db.Float, default=2.5)
    interval = db.Column(db.Integer, default=0)
    repetitions = db.Column(db.Integer, default=0)
    next_review = db.Column(db.Date, default=datetime.now().date)
    last_review = db.Column(db.Date)
    total_reviews = db.Column(db.Integer, default=0)
    correct_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now)
    word = db.relationship('Word', backref='user_words')

class DailyRecord(db.Model):
    __tablename__ = 'daily_records'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.now().date)
    new_count = db.Column(db.Integer, default=0)
    review_count = db.Column(db.Integer, default=0)
    total_count = db.Column(db.Integer, default=0)
    mastered_count = db.Column(db.Integer, default=0)
    __table_args__ = (db.UniqueConstraint('user_id', 'date', name='_user_date_uc'),)
