from sqlalchemy import Integer, String, Column, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum


Base = declarative_base()


class IssueStatus(Enum):
    """"""
    Close = (0, "closeIssue")
    Open = (1, "openIssue")
    Comment = (10, "commentIssue")

    def __init__(self, status_id, command):
        self.status_id = status_id
        self.command = command


class Users(Base):
    """"""
    __tablename__ = 'users'

    user_id = Column(Integer(), primary_key=True, autoincrement=False)
    first_name = Column(String(2048), nullable=True)
    last_name = Column(String(2048), nullable=True)
    username = Column(String(2048), nullable=True)
    user_dt = Column(DateTime(), default=datetime.now)

    def __init__(self, user_id, first_name, last_name, username, user_dt=datetime.now()):
        self.user_id = user_id
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.user_dt = user_dt

    def __repr__(self):
        return f'Username - {self.username}'


class Messages(Base):
    """"""
    __tablename__ = 'messages'

    message_id = Column(Integer(), primary_key=True, autoincrement=False)
    reply_message_id = Column(Integer(), nullable=True)
    user_id = Column(Integer(), ForeignKey(Users.user_id), nullable=False)
    message = Column(String(4096), nullable=True)
    message_dt = Column(DateTime(), default=datetime.now)

    user = relationship(Users)

    def __init__(self, message_id, reply_message_id, user_id, message, message_dt=datetime.now()):
        self.message_id = message_id
        self.reply_message_id = reply_message_id
        self.user_id = user_id
        self.message = message
        self.message_dt = message_dt

    def __repr__(self):
        return f'Message - {self.message}'


class Issues(Base):
    """"""
    __tablename__ = 'issues'

    issue_id = Column(Integer(), primary_key=True, autoincrement=False)
    issue_dt = Column(DateTime(), default=datetime.now)

    def __init__(self, issue_id, issue_dt=datetime.now()):
        self.issue_id = issue_id
        self.issue_dt = issue_dt

    def __repr__(self):
        return f'Issue - {self.issue_id} open at {self.issue_dt}'


class Statuses(Base):
    """"""
    __tablename__ = 'statuses'

    status_id = Column(Integer(), primary_key=True, autoincrement=False)
    description = Column(String(64))

    def __init__(self, status_id, description=datetime.now()):
        self.status_id = status_id
        self.description = description

    def __repr__(self):
        return f'Status - {self.description}'


class IssueStates(Base):
    """"""
    __tablename__ = 'issue_states'

    issue_state_id = Column(Integer(), primary_key=True)
    issue_number = Column(Integer(), ForeignKey(Issues.issue_id), nullable=False)
    status_id = Column(Integer(), ForeignKey(Statuses.status_id), nullable=False)
    message_id = Column(Integer(), ForeignKey(Messages.message_id), nullable=False)
    status_dt = Column(DateTime(), default=datetime.now)

    def __init__(self, issue_number, status_id, message_id, status_dt=datetime.now()):
        self.issue_number = issue_number
        self.status_id = status_id
        self.message_id = message_id
        self.status_dt = status_dt

    issue = relationship(Issues)
    status = relationship(Statuses)
    message = relationship(Messages)
