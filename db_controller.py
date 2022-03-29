from db import DBManagerBasic, DB_MYSQL
from txdb import CreateSurveyTxDB, AddParticipantsTxDB, VoteTxDB, UserDB, MemberDB


class DBManager(DBManagerBasic):
	def __init__(self, db_name):
		super().__init__(DB_MYSQL, mysql_user_name="ivoting", mysql_password="##MY_PASSWORD##", mysql_db_host="127.0.0.1", mysql_db_port="3306", mysql_db_name=db_name)

	def config_show_tables(self):
		self.show_tables_params = [
			{'db_class': CreateSurveyTxDB,
	 		'add_columns': []
	 		}]


class TransactionDBController():
	def __init__(self):
		self.dbm = DBManager("blockchain")
	
	def insertCreateSurvey(self, start_time, end_time, multiple_answer, uri, v, r, s, nonce, block, timestamp):
		with self.dbm.session_scope() as session:
			session.add(CreateSurveyTxDB(start_time=start_time, end_time=end_time, multiple_answer=multiple_answer, uri=uri, v=v, r=r, s=s, nonce=nonce, block=block, timestamp=timestamp))
	def insertAddParticipants(self, sc_id, participants, v, r, s, nonce, block, timestamp):
		with self.dbm.session_scope() as session:
			session.add(AddParticipantsTxDB(sc_id=sc_id, participants=participants, v=v, r=r, s=s, nonce=nonce, block=block, timestamp=timestamp))
	def insertVote(self, sc_id, votes, v, r, s, nonce, block, timestamp):
		with self.dbm.session_scope() as session:
			session.add(VoteTxDB(sc_id=sc_id, votes=votes, v=v, r=r, s=s, nonce=nonce, block=block, timestamp=timestamp))

class UserDBController():
	def __init__(self):
		self.dbm = DBManager("dev")
	
	def getSignersAddress(self):
		with self.dbm.session_scope() as session:
			return session.query(UserDB.blockchainAddress).join(MemberDB).filter(MemberDB.type == "CA").all()