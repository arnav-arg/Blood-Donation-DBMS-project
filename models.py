from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import CheckConstraint
import pytz

ist = pytz.timezone('Asia/Kolkata')
db = SQLAlchemy()

class Person(db.Model):
    __tablename__ = 'person'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), unique=True, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    blood_group = db.Column(db.String(5), nullable=False)
    address = db.Column(db.Text, nullable=True)
    med_issues = db.Column(db.Text, default=None)
    dob = db.Column(db.Date, nullable=False)
    last_donated = db.Column(db.DateTime, nullable=True)
    
    donations = db.relationship('Donation', back_populates='person', cascade='all, delete-orphan')
    receives = db.relationship('Receive', back_populates='person', cascade='all, delete-orphan')
    
    __table_args__ = (
        # Ensure phone is 10 digits and numeric in SQLite
        CheckConstraint("length(phone) = 10 AND phone NOT LIKE '%[^0-9]%'",
                        name='check_phone_format'),
    )

class Donation(db.Model):
    __tablename__ = 'donation'
    
    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id', ondelete='CASCADE'), nullable=False)
    datetime = db.Column(db.DateTime, default=lambda: datetime.now(ist))
    quantity = db.Column(db.Float, nullable=False)
    
    person = db.relationship('Person', back_populates='donations')

class Receive(db.Model):
    __tablename__ = 'receive'
    
    id = db.Column(db.Integer, primary_key=True)
    person_id = db.Column(db.Integer, db.ForeignKey('person.id', ondelete='CASCADE'), nullable=False)
    datetime = db.Column(db.DateTime, default=lambda: datetime.now(ist))
    quantity = db.Column(db.Float, nullable=False)
    
    person = db.relationship('Person', back_populates='receives')

class Stock(db.Model):
    __tablename__ = 'stock'
    
    blood_group = db.Column(db.String(5), primary_key=True)
    quantity = db.Column(db.Float, nullable=False, default=0)
    
    __table_args__ = (
        CheckConstraint('quantity >= 0', name='check_non_negative_quantity'),
    )