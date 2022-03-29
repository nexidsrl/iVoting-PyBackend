from pylib.sc_mng import SmartContractManager
from brownie import accounts, web3
from brownie.network.account import PublicKeyAccount
from pylib.signer import Signer
import datetime
from terminaltables import AsciiTable
import time

scm = SmartContractManager('development')

scm.set_deployer_account(accounts[0])

ba_sc, vp_sc, de_sc = scm.deploy_platform()

# Creo un account admin senza gas
signer_address = web3.eth.account.create()
admin = Signer(signer_address.privateKey)
# Lo aggiungo come signer nello smart contract
ba_sc.add_signer(admin.account)

# Crea una nuova survey
answers = [admin.keccak("Risposta1"), admin.keccak("Risposta2"), admin.keccak("Risposta3")]
start_time = int(datetime.datetime.now().timestamp() + 15)
end_time = int(datetime.datetime.now().timestamp() + 25)
multiple_answer = 3
uri = "https://ciao"
nonce = admin.gen_nonce()
# Genera l'hash dei dati
hash_request = ba_sc.encode_survey_data(start_time, end_time, answers, multiple_answer, uri, nonce)
sign_hash = admin.signData(hash_request)
# Crea la survey
id_survey, sender = ba_sc.new_survey(start_time, end_time, answers, multiple_answer, uri, nonce, sign_hash)
# Verifica i dati della survey
survey_metadata = ba_sc.get_survey_metadata(id_survey)
data_table = [['Survey id', 'Survey\'s owner', 'Sender', 'Sender Balance', 'Admin', 'Admin Balance'],
              [id_survey, survey_metadata[3], sender,
               "{} ETH".format(web3.fromWei(PublicKeyAccount(sender).balance(), 'ether')),
               admin.account.address,
               "{} ETH".format(web3.fromWei(admin.account.balance(), 'ether'))]]

table = AsciiTable(data_table)
print(table.table)


# Aggiunger partecipanti sino a che è possibile e delega i voti
yet_to_add = True
nonce = admin.gen_nonce()
all_participants = []
all_delegated = []
all_delegated_tkn = {}
while yet_to_add:
    print("La survey apre: {}, Ora: {}".format(survey_metadata[0], int(datetime.datetime.now().timestamp())))
    participants1 = web3.eth.account.create()
    participants2 = web3.eth.account.create()
    delegate = web3.eth.account.create()
    all_participants.append(participants1)
    all_participants.append(participants2)
    to_add = [participants1.address, participants2.address]
    hash_add_participants = ba_sc.encode_participants_data(id_survey, to_add, nonce)
    sign_hash = admin.signData(hash_add_participants)
    added, sender = ba_sc.add_participants(id_survey, to_add, nonce, sign_hash)
    nonce = admin.gen_nonce()
    yet_to_add = added
    # Delega del primo partecipante
    if added:
        part1Signer = Signer(participants1.privateKey)
        for i in range(0, multiple_answer):
            try:
                tkn_id = ba_sc.get_token_id_in_survey(participants1.address, id_survey, i)
                nonce_part = part1Signer.gen_nonce()
                hash_delegate = de_sc.encode_delegate_data(delegate.address, tkn_id, nonce_part)
                sign_hash = part1Signer.signData(hash_delegate)
                de_sc.delegate(delegate.address, tkn_id, nonce_part, sign_hash)
                try:
                    all_delegated_tkn[delegate.address].append(tkn_id)
                except:
                    all_delegated_tkn[delegate.address] = []
                    all_delegated_tkn[delegate.address].append(tkn_id)
            except Exception as e:
                print(e)
        all_delegated.append(delegate)

    time.sleep(2)

print("Votanti")
voterData = [['Indirizzo', 'Numero voti']]
for voter in all_participants:
    voterData.append([voter.address, vp_sc.balance_of(voter.address)])

table_voter_data = AsciiTable(voterData)
print(table_voter_data.table)

print("Delegati")
delegateData = [['Indirizzo', 'Delega da', 'Numero Voti']]
for dele in all_delegated:
    survey_id_tkn, owner_tkn, delegate, selection = vp_sc.get_voting_paper_metadata(all_delegated_tkn[dele.address][0])
    delegateData.append([dele.address, owner_tkn, vp_sc.balance_of(dele.address)])

table_dele_data = AsciiTable(delegateData)
print(table_dele_data.table)
print("Votazione iniziata")