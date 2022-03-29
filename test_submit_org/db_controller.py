from db import DBManagerBasic, DB_MYSQL
from txdb import OrgDB, MemberDB, HeaderListDB, ListDB, UserDB


class DBManager(DBManagerBasic):
	def __init__(self):
		super().__init__(DB_MYSQL, mysql_user_name="ivoting", mysql_password="##MY_PASSWORD##", mysql_db_host="127.0.0.1", mysql_db_port="3306", mysql_db_name="dev")

	def config_show_tables(self):
		self.show_tables_params = [
			{'db_class': OrgDB,
	 		'add_columns': []
	 		}]


class DBController():
	def __init__(self):
		self.dbm = DBManager()
	
	def insertOrg(self, name=None, description=None, vat=None, street_address=None, street_number=None, city=None,
                 pv=None, country=None, phone=None, email=None, site=None, contact=None, active=None):
		with self.dbm.session_scope() as session:
			session.add(OrgDB(name=name, description=description, vat=vat, street_address=street_address, street_number=street_number, city=city,
                 pv=pv, country=country, phone=phone, email=email, site=site, contact=contact, active=active))

	def getSignersAddress(self):
		with self.dbm.session_scope() as session:
			return session.query(UserDB.blockchainAddress).join(MemberDB).filter(MemberDB.type == "CA").all()
	
	def getOrgIdByName(self, name):
		with self.dbm.session_scope() as session:
			return session.query(OrgDB.id).filter(OrgDB.name == name).first()[0]

	def insertMember(self, organization_id, user_id, type):
		with self.dbm.session_scope() as session:
			session.add(MemberDB(organization_id=organization_id, user_id=user_id, type=type))

	def insertHeaderList(self, label, organization_id):
		with self.dbm.session_scope() as session:
			session.add(HeaderListDB(label=label, organization_id=organization_id))
	
	def getHeaderListIdByLabel(self, label):
		with self.dbm.session_scope() as session:
			return session.query(HeaderListDB.id).filter(HeaderListDB.label == label).first()[0]

	def insertList(self, email, user_id, header_list_id):
		with self.dbm.session_scope() as session:
			session.add(ListDB(email=email, user_id=user_id, header_list_id=header_list_id))
	
	def insertUserOnlyCodFisType(self, codice_fiscale, type):
		with self.dbm.session_scope() as session:
			session.add(UserDB(codice_fiscale=codice_fiscale, type=type))
	
	def getUserIdByCodFIs(self, codice_fiscale):
		with self.dbm.session_scope() as session:
			return session.query(UserDB.id).filter(UserDB.codice_fiscale== codice_fiscale).first()[0]
	