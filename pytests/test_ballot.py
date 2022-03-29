from brownie import accounts, web3
from brownie.network.account import PublicKeyAccount
from pylib.smart_contracts import Ballot
from pylib.signer import Signer
from brownie import network
import datetime
from terminaltables import AsciiTable
import time

network_selected = 'development'
try:
    network.connect(network_selected)
except:
    network.connect(network_selected, launch_rpc=False)

ballot_sc = Ballot(accounts[0])
c = ballot_sc.deploy()

# Signer non ha gas nè ether
signer_address = web3.eth.account.create()
admin = Signer(signer_address.privateKey)

answers = [admin.keccak("Risposta1"), admin.keccak("Risposta2"), admin.keccak("Risposta3")]
print(ballot_sc.add_signer(admin.account))
start_time = int(datetime.datetime.now().timestamp()+10)
end_time = int(datetime.datetime.now().timestamp() + 20)
multiple_answer = 3
uri = "https://ciao"
nonce = 1

hash_request = ballot_sc.encode_survey_data(start_time, end_time, answers, multiple_answer, uri, nonce)
sign_hash = admin.signData(hash_request)
id_survey, sender = ballot_sc.new_survey(start_time, end_time, answers, multiple_answer, uri, nonce, sign_hash)
print(id_survey)
survey_metadata = ballot_sc.get_survey_metadata(id_survey)
data_table = [['Survey id', 'Survey\'s owner', 'Sender', 'Sender Balance', 'Admin', 'Admin Balance'],
              [id_survey, survey_metadata[3], sender,
               "{} ETH".format(web3.fromWei(PublicKeyAccount(sender).balance(), 'ether')),
               admin.account.address,
               "{} ETH".format(web3.fromWei(admin.account.balance(), 'ether'))]]

table = AsciiTable(data_table)
print(table.table)
# Non dovrebbe aggiungerla perchè il nonce è stato già usato
id_survey_fake, sender = ballot_sc.new_survey(start_time, end_time, answers, multiple_answer, uri, nonce, sign_hash)
print(id_survey_fake)

