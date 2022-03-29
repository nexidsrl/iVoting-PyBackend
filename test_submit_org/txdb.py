from sqlalchemy import Column
from sqlalchemy.types import DateTime, Integer, Text
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

from db import Base 

class OrgDB(Base):
    __tablename__ = 'organizations'
    id = Column(Integer, primary_key=True) 
    name = Column(Text)
    description= Column(Text)
    vat = Column(Text)
    street_address = Column(Text)
    street_number = Column(Text)
    city = Column(Text)
    pv = Column(Text)
    country = Column(Text)
    phone = Column(Text)
    email = Column(Text)
    site = Column(Text)
    contact = Column(Text)
    active = Column(Integer)

    def __init__(self, id=None, name=None, description=None, vat=None, street_address=None, street_number=None, city=None,
                 pv=None, country=None, phone=None, email=None, site=None, contact=None, active=0):
        self.id = id
        self.name=name 
        self.description=description
        self.vat = vat
        self.street_address=street_address
        self.street_number=street_number
        self.city=city
        self.pv=pv 
        self.country = country
        self.phone=phone
        self.email=email
        self.site=site
        self.contact=contact
        self.active=active

    def __unicode__(self):
        return self.__repr__()

    def __repr__(self):
        return "<{}: {} - {} - {}>".format(self.__tablename__, self.id, self.name, self.description, self.vat, self.street_address, self.street_number, self.city, self.pv, self.country, self.phone, self.email, self.site, self.contact, self.active)

    

class MemberDB(Base):
    __tablename__ = 'members'
    id = Column(Integer, primary_key=True) # auto incrementing
    organization_id = Column(Integer)
    user_id = Column(Integer)
    type = Column(Text)

    def __init__(self, organization_id=None, user_id=None, type='M'):
        self.organization_id=organization_id
        self.user_id = user_id
        self.type=type

    def __unicode__(self):
        return self.__repr__()

    def __repr__(self):
        return "<{}: {} - {} - {}>".format(self.__tablename__, self.id, self.organization_id, self.user_id, self.r, self.type)


class HeaderListDB(Base):
    __tablename__ = 'header_list'
    id = Column(Integer, primary_key=True) # auto incrementing
    label = Column(Text)
    organization_id = Column(Integer)

    def __init__(self, label=None, organization_id=None):
        self.label=label
        self.organization_id = organization_id

    def __unicode__(self):
        return self.__repr__()

    def __repr__(self):
        return "<{}: {} - {} - {}>".format(self.__tablename__, self.id, self.label, self.organization_id)


class ListDB(Base):
    __tablename__ = 'lists'
    id = Column(Integer, primary_key=True) # auto incrementing
    email = Column(Text)
    user_id = Column(Integer)
    header_list_id = Column(Integer)

    def __init__(self, email=None, user_id=None, header_list_id=None):
        self.email=email
        self.user_id = user_id
        self.header_list_id = header_list_id

    def __unicode__(self):
        return self.__repr__()

    def __repr__(self):
        return "<{}: {} - {} - {}>".format(self.__tablename__, self.id, self.email, self.user_id, self.header_list_id)

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

