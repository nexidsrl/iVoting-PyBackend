import requests
import math
import time
from brownie import web3
from pylib.signer import Signer
import threading


class ThreadedTest:
    def __init__(self, api):
        self.num_accounts = 10
        self.participants = []
        self.addresses = []
        self.num_choices = 1
        self.choices = "[\"prova1\", \"prova2\",\"prova1\", \"prova2\",\"prova1\", \"prova2\",\"prova1\", \"prova2\",\"prova1\", \"prova2\"]"
        self.uri = 'PROVA'
        self.threads = []
        self.api = api

    def generateVoterAppend(self, index):
        user = web3.eth.account.create()
        self.participants.append(user)
        self.addresses.append(user.address)
        print("Generating account {}/{} {}".format(index, self.num_accounts, user.address))

    """ def doVote(self, id, index, votes, nonce, account):
		signer = Signer(account.privateKey)
		hash_request = self.api.vote(id, votes, nonce)
		print("Voter {} Encode Vote: {}".format(
			index, hash_request['hash_request']))
		signed = signer.signData(hash_request['hash_request'])
		status = self.api.sign_vote(id, votes, signed['v'], hex(
			signed['r']), hex(signed['s']), nonce)
		print("Voter {} Signed Vote: {}".format(index, status['status'])) """

    def test(self):
        account = web3.eth.account.create()
        admin = Signer(account.privateKey)
        print("Generate Wallet Admin {}".format(admin.account))
        for i in range(self.num_accounts):
            t = threading.Thread(target=self.generateVoterAppend, args=(i,))
            t.start()
            self.threads.append(t)
        for thread in self.threads:
            thread.join()
        self.threads = []
        self.api.add_signer(admin.account)
        nonce = 1
        start = math.trunc(time.time()) + 60
        end = math.trunc(time.time()) + 12000
        hash_request = self.api.create_survey(
            start, end, self.num_choices, self.choices, self.uri, nonce)
        print("Encode Survey hash: {}".format(hash_request['hash_request']))
        signed = admin.signData(hash_request['hash_request'])
        id = self.api.sign_survey(nonce, start, end, self.num_choices, self.choices,
                                  self.uri, signed['v'], hex(signed['r']), hex(signed['s']), account.address)
        id = id['id']
        print("Signed Survey ID: {}".format(id))
        nonce += 1
        hash_request = self.api.add_participants(id, str(self.addresses), nonce)
        signed = admin.signData(hash_request['hash_request'])
        print("Encode Add Participants: {}".format(
            hash_request['hash_request']))
        try:
            status = self.api.sign_add_participants(
                id, str(self.addresses), signed['v'], hex(signed['r']), hex(signed['s']), nonce, account.address)
        except:
            pass
        print("Signed Add Participants: {}".format(status['status']))
        print("Check survey start")
        while(start > math.trunc(time.time())):
            print("Wait start survey")
            time.sleep(30)
        """ for index, voter_account in enumerate(self.participants):
			t = threading.Thread(target=self.doVote, args=(id, index, [1], 1, voter_account))
			t.start()
			self.threads.append(t)
		for thread in self.threads:
			thread.join()
		self.threads = [] """
        for index, voter_account in enumerate(self.participants):
            try:
                nonce = 1
                votes = [index % 9+1]
                signer = Signer(voter_account.privateKey)
                hash_request = self.api.vote(id, votes, nonce)
                print("Voter {} Encode Vote: {} Address: {}".format(
                    index, hash_request['hash_request'], voter_account.address))
                signed = signer.signData(hash_request['hash_request'])
                status = self.api.sign_vote(id, votes, signed['v'], hex(signed['r']),
                                            hex(signed['s']), nonce, voter_account.address)
                print("Voter {} Signed Vote: {} Address: {}".format(index, status['status'], voter_account.address))
            except Exception as e:
                print(f"Voto non inviato: {str(e)}")


class BallotTestAPI:
    def __init__(self):
        self.url = "http://127.0.0.1:5000"
        self.headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    def create_survey(self, start_time, end_time, num_choices, choices, uri, nonce):
        params = {'nonce': nonce, 'start_time': start_time, 'end_time': end_time,
                  'num_choices': num_choices, 'choices': choices, 'uri': uri}
        result = requests.post(self.url+"/createSurvey",
                               headers=self.headers, data=params)
        return result.json()

    def add_participants(self, sc_id, participants, nonce):
        params = {'nonce': nonce, 'sc_id': sc_id,
                  'participants': participants}
        result = requests.post(self.url+"/AddParticipants",
                               headers=self.headers, data=params)
        return result.json()

    def sign_add_participants(self, sc_id, participants, v, r, s, nonce, address):
        params = {'nonce': nonce, 'sc_id': sc_id, 'participants':
                  participants, 'v': v, 'r': r, 's': s, 'address': address}
        result = requests.post(self.url+"/SignAddparticipants",
                               headers=self.headers, data=params)
        return result.json()

    def vote(self, sc_id, votes, nonce):
        params = {'nonce': nonce, 'sc_id': sc_id, 'votes': str(votes)}
        result = requests.post(
            self.url+"/Vote", headers=self.headers, data=params)
        return result.json()

    def sign_survey(self, nonce, start_time, end_time, multiple_answer, hash_answer, uri, v, r, s, address):
        params = {'nonce': nonce, 'start_time': start_time, 'end_time': end_time,
                  'multiple_answer': multiple_answer, 'choices': hash_answer, 'uri': uri, 'v': v, 'r': r, 's': s, 'address': address}
        result = requests.post(self.url+"/signSurvey",
                               headers=self.headers, data=params)
        return result.json()

    def sign_vote(self, sc_id, votes, v, r, s, nonce, address):
        params = {'nonce': nonce, 'sc_id': sc_id,
                  'votes': str(votes), 'v': v, 'r': r, 's': s, 'address': address}
        result = requests.post(self.url+"/SignVote",
                               headers=self.headers, data=params)
        return result.json()

    def add_signer(self, address):
        params = {'address': address}
        result = requests.post(self.url+"/AddSigner",
                               headers=self.headers, data=params)
        return result.json()

    def get_nonce(self, address):
        params = {'address': address}
        result = requests.post(self.url+"/getNonce",
                               headers=self.headers, data=params)
        return result.json()

    def has_voted(self, sc_id, address):
        params = {'address': address, 'sc_id': sc_id}
        result = requests.post(self.url+"/HasVoted",
                               headers=self.headers, data=params)
        return result.json()


api = BallotTestAPI()
test = ThreadedTest(api)
test.test()
#print(api.has_voted(53, "0x0dbb3ca0bfea9eb133effdc2d191833f0009b2b5"))
# print(survey.create_survey())
# print(survey.get_nonce("0x34d46be6ed06181e677e8d5520489d572e96ee30"))
# print(survey.add_signer("0x62bba083418ae72a796ba061cc5ff8aae6960d76"))
# print(survey.sign_survey("0", survey.start_time, survey.end_time, survey.num_choices, survey.choices, survey.uri, "28","108501791486135508117510092835783783052441164841397895819593614892629209784325","8855806311303056471929188631799333066042272531174698729375566254477452671796"))
# print(survey.add_participants())
# print(survey.sign_add_participants("27", "345678909876543456789", "4567890987654567890"))
# print(survey.vote())
# print(survey.sign_vote([1,2,3], "27", "2345678765432","23456789098765432"))
# print(survey.has_voted(376, "0x62bba083418ae72a796ba061cc5ff8aae6960d76"))
