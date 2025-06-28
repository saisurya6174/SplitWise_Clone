from datetime import datetime
from app import db
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean

class User(db.Model):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    groups = relationship('GroupMembership', back_populates='user')
    expenses = relationship('Expense', back_populates='payer')
    settlements = relationship('Settlement', back_populates='from_user')

class Group(db.Model):
    __tablename__ = 'groups'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    members = relationship('GroupMembership', back_populates='group')
    expenses = relationship('Expense', back_populates='group')

class GroupMembership(db.Model):
    __tablename__ = 'group_memberships'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=False)
    
    user = relationship('User', back_populates='groups')
    group = relationship('Group', back_populates='members')

class Expense(db.Model):
    __tablename__ = 'expenses'
    
    id = Column(Integer, primary_key=True)
    description = Column(String(255), nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    
    payer_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=False)
    
    payer = relationship('User', back_populates='expenses')
    group = relationship('Group', back_populates='expenses')
    splits = relationship('ExpenseSplit', back_populates='expense')

class ExpenseSplit(db.Model):
    __tablename__ = 'expense_splits'
    
    id = Column(Integer, primary_key=True)
    expense_id = Column(Integer, ForeignKey('expenses.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    amount = Column(Float, nullable=False)
    is_settled = Column(Boolean, default=False)
    
    expense = relationship('Expense', back_populates='splits')
    user = relationship('User')

class Settlement(db.Model):
    __tablename__ = 'settlements'
    
    id = Column(Integer, primary_key=True)
    from_user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    to_user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    amount = Column(Float, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    group_id = Column(Integer, ForeignKey('groups.id'), nullable=False)
    
    from_user = relationship('User', foreign_keys=[from_user_id])
    to_user = relationship('User', foreign_keys=[to_user_id])
    group = relationship('Group')
