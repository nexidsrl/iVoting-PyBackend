from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import DateTime, Integer, Text
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

from db import Base 

class CreateSurveyTxDB(Base):
    __tablename__ = 'create_survey_tx'
    id = Column(Integer, primary_key=True) 
    start_time = Column(Integer)
    end_time = Column(Integer)
    multiple_answer = Column(Integer)
    uri = Column(Text)
    v = Column(Integer)
    r = Column(Text)
    s = Column(Text)
    nonce = Column(Integer)
    block = Column(Integer)
    timestamp = Column(Integer)

    def __init__(self, start_time=None, end_time=None, multiple_answer=None, uri=None, v=None, r=None, s=None,
                 nonce=None, block=None, timestamp=None):
        self.start_time = start_time
        self.end_time=end_time 
        self.multiple_answer=multiple_answer
        self.uri = uri
        self.v=v
        self.r=r
        self.s=s
        self.nonce=nonce 
        self.block = block
        self.timestamp=timestamp
        #aggiungere tempo

    def __unicode__(self):
        return self.__repr__()

    def __repr__(self):
        return "<{}: {} - {} - {}>".format(self.__tablename__, self.start_time, self.end_time, self.multiple_answer, self.uri, self.r, self.s, self.nonce, self.block, self.timestamp)

    

class AddParticipantsTxDB(Base):
    __tablename__ = 'add_participants_tx'
    id = Column(Integer, primary_key=True) # auto incrementing
    sc_id = Column(Integer)
    participants = Column(Text)
    v = Column(Integer)
    r = Column(Text)
    s = Column(Text)
    nonce = Column(Integer)
    block = Column(Integer)
    timestamp = Column(Integer)

    def __init__(self, sc_id=None, participants=None, v=None, r=None, s=None,
                 nonce=None, block=None, timestamp=None):
        self.sc_id=sc_id
        self.participants = participants
        self.v=v 
        self.r=r
        self.s=s
        self.nonce=nonce 
        self.block = block
        self.timestamp=timestamp
        #aggiungere tempo

    def __unicode__(self):
        return self.__repr__()

    def __repr__(self):
        return "<{}: {} - {} - {}>".format(self.__tablename__, self.id, self.sc_id, self.participants, self.r, self.s, self.nonce, self.block, self.timestamp)


class VoteTxDB(Base):
    __tablename__ = 'vote_tx'
    id = Column(Integer, primary_key=True) # auto incrementing
    sc_id = Column(Integer)
    votes = Column(Text)
    v = Column(Integer)
    r = Column(Text)
    s = Column(Text)
    nonce = Column(Integer)
    block = Column(Integer)
    timestamp = Column(Integer)

    def __init__(self, sc_id=None, votes=None, v=None, r=None, s=None,
                 nonce=None, block=None, timestamp=None):
        self.sc_id=sc_id
        self.votes = votes
        self.v=v 
        self.r=r
        self.s=s
        self.nonce=nonce 
        self.block = block
        self.timestamp=timestamp
        #aggiungere tempo

    def __unicode__(self):
        return self.__repr__()

    def __repr__(self):
        return "<{}: {} - {} - {}>".format(self.__tablename__, self.id, self.sc_id, self.votes, self.r, self.s, self.nonce, self.block, self.timestamp)

    

class MemberDB(Base):
    __tablename__ = 'members'
    id = Column(Integer, primary_key=True) # auto incrementing
    organization_id = Column(Integer)
    user_id = Column(Integer,  ForeignKey("users.id"))
    type = Column(Text)

    def __init__(self, organization_id=None, user_id=None, type='M'):
        self.organization_id=organization_id
        self.user_id = user_id
        self.type=type

    def __unicode__(self):
        return self.__repr__()

    def __repr__(self):
        return "<{}: {} - {} - {}>".format(self.__tablename__, self.id, self.organization_id, self.user_id, self.r, self.type)

class UserDB(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True) # auto incrementing
    type = Column(Text)
    codice_fiscale = Column(Text)
    first_name = Column(Text)
    last_name = Column(Text)
    email = Column(Text)
    password = Column(Text)
    api_token = Column(Text)
    blockchainAddress = Column(Text)
    avatar = Column(Text)
    remember_token =Column(Text)
    codice_spid = Column(Text)
    nonce = Column(Integer)

    def __init__(self, type='M', codice_fiscale=None, first_name=None, last_name=None, email=None, password=None, api_token=None, blockchainAddress=None, avatar=None, remember_token=None, codice_spid=None, nonce=None):
        self.type=type
        self.email=email
        self.first_name = first_name
        self.last_name = last_name
        self.password = password
        self.api_token = api_token
        self.blockchainAddress = blockchainAddress
        self.avatar = avatar
        self.remember_token = remember_token
        self.codice_spid = codice_spid
        self.nonce = nonce

    def __unicode__(self):
        return self.__repr__()

    def __repr__(self):
        return "<{}: {} - {} - {}>".format(self.__tablename__, self.id, self.first_name, self.last_name, self.password, self.api_token, self.blockchainAddress, self.avatar, self.remember_token, self.codice_spid, self.nonce)

