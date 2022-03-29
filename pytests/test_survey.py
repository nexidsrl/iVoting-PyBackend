from pylib.sc_mng import SmartContractManager
from brownie import accounts, web3
from brownie.network.account import PublicKeyAccount
from pylib.signer import Signer
import datetime
from terminaltables import AsciiTable
import time

scm = SmartContractManager('nexid')
#accounts.add("95e198dde9e4e8570b055018f8926a1b427ff2fc252a069be6f56a9ad5818d88")
accounts.add("52fc13b7d90ed064e5e955ecd072119f91a21bfac6017988de0599d812af582f")
print(accounts)
scm.set_deployer_account(accounts.at('0xb1d69C5208E629884aAA1FD0931C7dfAd24d5592'))

ba_sc, vp_sc, de_sc = scm.deploy_platform()

# Creo un account admin senza gas
signer_address = web3.eth.account.create()
admin = Signer(signer_address.privateKey)
# Lo aggiungo come signer nello smart contract
ba_sc.add_signer(admin.account)

# Crea una nuova survey
answers = [admin.keccak("Risposta1"), admin.keccak("Risposta2"), admin.keccak("Risposta3")]
start_time = int(datetime.datetime.now().timestamp() + 10)
end_time = int(datetime.datetime.now().timestamp() + 20)
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
# Verifica che non possa più usare quella firma
id_survey_fake, sender = ba_sc.new_survey(start_time, end_time, answers, multiple_answer, uri, nonce, sign_hash)

# Aggiunger partecipanti sino a che è possibile
yet_to_add = True
nonce = admin.gen_nonce()
all_participants = []
while yet_to_add:
    print("La survey apre: {}, Ora: {}".format(survey_metadata[0], int(datetime.datetime.now().timestamp())))
    participants1 = web3.eth.account.create()
    participants2 = web3.eth.account.create()
    all_participants.append(participants1)
    all_participants.append(participants2)
    to_add = [participants1.address, participants2.address]
    hash_add_participants = ba_sc.encode_participants_data(id_survey, to_add, nonce)
    sign_hash = admin.signData(hash_add_participants)
    added, sender = ba_sc.add_participants(id_survey, to_add, nonce, sign_hash)
    nonce = admin.gen_nonce()
    # Delega

    yet_to_add = added
    time.sleep(2)

print("Votazione iniziata")
for voter in all_participants:
    print(voter.address, vp_sc.balance_of(voter.address))


# Lascia votare solo i primi account
for voter in all_participants:
    print("La survey chiude: {}, Ora: {}".format(survey_metadata[0], int(datetime.datetime.now().timestamp())))
    print("Ora vota: {}. Ether Balance: {} ETH".format(voter.address,
                                                web3.fromWei(PublicKeyAccount(voter.address).balance(), 'ether')))
    voterSigner = Signer(voter.privateKey)
    nonce = voterSigner.gen_nonce()
    hash = ba_sc.encode_vote_data(id_survey, [1,2,3], nonce)
    sign_hash = voterSigner.signData(hash)
    ba_sc.vote(id_survey, [1, 2, 3], nonce, sign_hash)
    # Prova a votare due volte con lo stesso nonce
    ba_sc.vote(id_survey, [1, 2, 3], nonce, sign_hash)
    # Prova a votare due volte con nonce diversi
    nonce = voterSigner.gen_nonce()
    hash = ba_sc.encode_vote_data(id_survey, [4, 5, 6], nonce)
    sign_hash = voterSigner.signData(hash)
    ba_sc.vote(id_survey, [4, 5, 6], nonce, sign_hash)

    # Faccio votare un utente che non è abilitato a votare
    fake_user = web3.eth.account.create()
    print("Ora vota un utente non abilitato: {}. Ether Balance: {} ETH".format(fake_user.address,
                                                web3.fromWei(PublicKeyAccount(fake_user.address).balance(), 'ether')))

    fakeVoterSigner = Signer(fake_user.privateKey)
    nonce = fakeVoterSigner.gen_nonce()
    hash = ba_sc.encode_vote_data(id_survey, [1, 2, 3], nonce)
    sign_hash = fakeVoterSigner.signData(hash)
    ba_sc.vote(id_survey, [1, 2, 3], nonce, sign_hash)
    time.sleep(5)

print("Votazione finita")
# Recupero i risultati della survey
header = ['User', 'Balance', 'Votes']
for i in range(0, multiple_answer):
    header.append('Risposta {}'.format(i+1))

table_result = [header]
for voter in all_participants:
    answers = [voter.address,
               "{} ETH".format(web3.fromWei(PublicKeyAccount(voter.address).balance(), 'ether')),
               vp_sc.balance_of(voter.address)]
    for i in range(0, multiple_answer):
        try:
            tkn_id = ba_sc.get_token_id_in_survey(voter.address, id_survey, i)
            answers.append(vp_sc.get_voting_paper_metadata(tkn_id)[3])
        except Exception as e:
            print(e)
            answers.append("-")
    table_result.append(answers)
table2 = AsciiTable(table_result)
print(table2.table)
