import sys
import os
import json
import time
import ast
import functools
from brownie import network, accounts, web3, config,  Contract
from brownie.convert.datatypes import HexString
from brownie.convert import to_string
from brownie.network.account import PublicKeyAccount
from pylib.smart_contracts import Ballot
from pylib.signer import Signer
from aiohttp import web
from contextlib import contextmanager
from dotenv import load_dotenv, find_dotenv
from db_controller import TransactionDBController, UserDBController
from logger import Logger
import logging
from logger.logger_conf import LogBaseModel
from pathlib import Path

# Carica costanti di configurazione da .env file
load_dotenv(find_dotenv())

# Classe che implementa funzioni principali
# Connection manager assicura di essere connessi ad un nodo attivo
# Le logiche nelle funzioni di exec permetto il reinoltro automatico
# della transazione nel caso di crash e mancata presenza nei log events
# exec_encode: si occupa di multiplexare le funzioni di encode
# exec_sign: si occupa di multiplexare le funzioni di sign


class BlockchainWrapper:

    def __init__(self):
        self.NODES = ["abele", "caino"]
        self.MAX_RETIRES = 5
        self.BALLOT_ADDRESS = os.getenv('BALLOT_ADDRESS')
        self.ballot_sc = None
        self.ballot_contract_logs = None
        self.db_controller = TransactionDBController()
        self.user_db_controller = UserDBController()
        self.count = 0
        with open('build/contracts/Ballot.json') as f:
            self.abi = json.load(f)['abi']
        self.logger = Logger(log_to_shell=True, level_shell=logging.INFO, path=Path("./log.log"))
        self.logger.info(f'\nBallot address: {self.BALLOT_ADDRESS}')

    def connectionManager(self):
        retry = 0
        while not network.is_connected() and retry <= self.MAX_RETIRES:
            for node in self.NODES:
                try:
                    print("Connecting to node {}".format(node))
                    network.connect(node)
                    web3.connect(os.getenv("{}_RPC".format(node.upper())))
                    accounts.add(os.getenv('REPLYER1'))
                    accounts.add(os.getenv('REPLYER2'))
                    accounts.add(os.getenv('REPLYER3'))
                    self.replyer_accounts = []
                    self.replyer_accounts.append(accounts.at(os.getenv('REPLYER1_ADDRESS')))
                    self.replyer_accounts.append(accounts.at(os.getenv('REPLYER2_ADDRESS')))
                    self.replyer_accounts.append(accounts.at(os.getenv('REPLYER3_ADDRESS')))
                    self.logger.info(f'\nReplyer accounts: { " ".join(o.address for o in self.replyer_accounts)}')
                    self.ballot_sc = Contract.from_abi("Ballot", self.BALLOT_ADDRESS, abi=self.abi)
                    self.ballot_contract_logs = web3.eth.contract(address=self.BALLOT_ADDRESS, abi=self.abi)
                    if network.is_connected():
                        self.logger.info("\nSuccessfully connected to node {}".format(node))
                        print("Latest Block: {}".format(self.getBlockNumber()))
                        time.sleep(1)
                        break
                    self.logger.info("\nNode {} is down, trying next".format(node))
                except Exception as e:
                    self.logger.warning(f'\nEception in connectionManager: {str(e)}')
            if not network.is_connected():
                self.logger.critical("\nAll nodes down, retry number {}".format(retry))
            retry += 1
            time.sleep(2)

    def string2keccak(self, str):
        return web3.keccak(text=str)

    def get_nonce(self, address):
        return web3.eth.getTransactionCount(web3.toChecksumAddress(address))

    def getBlockNumber(self):
        return web3.eth.getBlock('latest').number

    def searchLog(self, function, form):
        # DA RIVEDERE CON INDIRIZZO
        try:
            if function == 'addSigner':
                filtro = self.ballot_contract_logs.events.SignerAdded.createFilter(
                    fromBlock=0, argument_filters={"account": form['address']})
                return {"status": True} if len(filtro.get_all_entries()) > 0 else False
            elif function == 'signVote':
                votes = ast.literal_eval(form['votes'])
                filtro = self.ballot_contract_logs.events.voted.createFilter(
                    fromBlock=0, argument_filters={"_surveyId": int(form['sc_id']), "_address": form['address']})
                return {"status": filtro.get_all_entries()[0]['transactionHash'].hex()} if len(filtro.get_all_entries()) > 0 else False
            elif function == 'hasVoted':
                filtro = self.ballot_contract_logs.events.voted.createFilter(
                    fromBlock=0, argument_filters={"_surveyId": int(form['sc_id']), "_address": form['address']})
                return {"status": True if len(filtro.get_all_entries()) > 0 else False}
            elif function == 'signSurvey':
                filtro = self.ballot_contract_logs.events.newSurvey.createFilter(
                    fromBlock=0, argument_filters={"creator": form['address']})
                return {"id": filtro.get_all_entries()[0]['args']['_surveyId']} if len(filtro.get_all_entries()) > 0 else False
            elif function == 'signAddParticipants':
                filtro = self.ballot_contract_logs.events.newParticipants.createFilter(
                    fromBlock=0, argument_filters={"_surveyId": int(form['sc_id'])})
                return {"status": True} if len(filtro.get_all_entries()) > 0 else False
        except Exception as e:
            self.logger.warning(f"\nException searchLog {function}: {str(e)}")
            return False

    def exec_encode(self, function, form):
        self.logger.info(f'\nAPICALL {function} {self.count}')
        result = False
        retry = 0
        while retry <= self.MAX_RETIRES:
            try:
                self.connectionManager()
                if function == 'createSurvey':
                    answers = [self.string2keccak(x) for x in ast.literal_eval(form['choices'])]

                    result = self.ballot_sc.encodeSurveyData(
                        form['start_time'], form['end_time'], answers, form['num_choices'], form['uri'], form['nonce'])
                elif function == 'addParticipants':
                    result = self.ballot_sc.encodeAddParticipantsData(form['sc_id'], [str(address) for address in list(
                        filter(None, ast.literal_eval(form['participants'])))], form['nonce'])
                elif function == 'vote':
                    result = self.ballot_sc.encodeVoteData(
                        form['sc_id'], ast.literal_eval(form['votes']), form['nonce'])
                if result:
                    return {"hash_request": str(result)}
            except Exception as e:
                self.logger.warning("\nException encode in {} {} call {}:    {}".format(
                    function, network.show_active(), self.count, str(e)))
            retry += 1
            self.logger.warning(f'\nRetry {retry} with {self.replyer_accounts[self.count%len(self.replyer_accounts)]}')
        return {"hash_request": False}

    def exect_sign(self, function, form):
        self.count += 1
        self.logger.info(f'\nAPICALL {function} {self.count}')
        retry = 0
        while retry <= self.MAX_RETIRES:
            try:
                self.connectionManager()
                replyer = self.replyer_accounts[self.count % len(self.replyer_accounts)]
                self.logger.info("\nSend {} {}: to {} form {}".format(
                    function, self.count, network.show_active(), replyer))

                if function == 'signSurvey':
                    answers = [self.string2keccak(x) for x in ast.literal_eval(form['choices'])]
                    tx = self.ballot_sc.createSurvey(int(form['start_time']), int(form['end_time']), answers, int(form['multiple_answer']), str(
                        form['uri']), int(form['nonce']), int(form['v']), form['r'], form['s'], {'from': replyer, 'gasPrice': web3.eth.gasPrice + (retry*10)})
                    #self.db_controller.insertCreateSurvey(form['start_time'], form['end_time'], form['multiple_answer'], form['uri'], form['v'], form['r'], form['s'], form['nonce'], self.getBlockNumber(), time.time())
                    # Se non esiste entra in except
                    result = {"id": tx.events['newSurvey']['_surveyId']}

                elif function == 'signAddParticipants':
                    tx = self.ballot_sc.addParticipants(int(form['sc_id']), [str(address) for address in list(filter(None, ast.literal_eval(
                        form['participants'])))], form['nonce'], int(form['v']), form['r'], form['s'], {'from': replyer, 'gasPrice': web3.eth.gasPrice + (retry*10)})
                    # try:
                    #db_controller.insertAddParticipants(form['sc_id'], form['participants'], form['v'], form['r'], form['s'], form['nonce'], self.getBlockNumber(), time.time())
                    # except Exception as e:
                    # print(str(e))
                    # Se non esiste entra in except
                    if len(tx.events["newParticipants"]["_participants"]) > 0:
                        result = {"status": True}
                    else:
                        raise Exception

                elif function == 'signVote':
                    votes = ast.literal_eval(form['votes'])
                    tx = self.ballot_sc.vote(form['sc_id'], votes, form['nonce'], form['v'], form['r'], form['s'], {
                                             'from': replyer, 'gasPrice': web3.eth.gasPrice + (retry*10)})
                    #self.db_controller.insertVote(form['sc_id'], form['votes'], form['v'], form['r'], form['s'], self.getBlockNumber(), form['nonce'], time.time())
                    # Se non esiste entra in except
                    result = {"status": str(tx.events["voted"]["_hash"])}

                elif function == 'addSigner':
                    if not self.ballot_sc.isSigner(form['address']):
                        tx = self.ballot_sc.addSigner(
                            form['address'], {'from': replyer, 'gasPrice': web3.eth.gasPrice + (retry*10)})
                        if tx.events["SignerAdded"]["account"] == form['address'] or self.ballot_sc.isSigner(form['address']):
                            result = {"status": True}
                        else:
                            raise Exception
                    else:
                        result = {"status": True}
                elif function == 'isSigner':
                    if self.ballot_sc.isSigner(form['address']):
                        result = {"status": True}

                    else:
                        result = {"status": False}
                elif function == 'removeSigner':
                    if not self.ballot_sc.isSigner(form['address']):
                        tx = self.ballot_sc.removeSigner(
                            form['address'], {'from': replyer, 'gasPrice': web3.eth.gasPrice + (retry*10)})
                        if tx.events["SignerRemoved"]["account"] == form['address'] or not self.ballot_sc.isSigner(form['address']):
                            result = {"status": True}
                        else:
                            raise Exception
                    else:
                        result = {"status": True}

                self.logger.info("\nResult {} {}: {}".format(function, self.count, result))
                return result

            except Exception as e:
                self.logger.warning("\nException in {} {} call {}:    {}".format(
                    function, network.show_active(), self.count, str(e)))
            receipt = self.searchLog(function, form)
            if receipt:
                self.logger.info("\nTransaction {} {} {} found in logs!".format(function, self.count, receipt))
                return receipt
            else:
                self.logger.warning("\nTransaction {} {} NOT found in logs!".format(function, self.count))
                self.count += 1
                retry += 1
                self.logger.error(
                    f'\nRetry {retry} with {self.replyer_accounts[self.count%len(self.replyer_accounts)]}')
                time.sleep(2)
        return {"status": False}


# Istanza classe
blockchain = BlockchainWrapper()
blockchain.connectionManager()
# Istanza API server
app = web.Application()

# Dichiarazioni funzioni API che utilizzano blockchainWrapper


async def createSurvey(request):
    data_form = await request.post()
    return web.json_response(blockchain.exec_encode('createSurvey', data_form))


async def addParticipants(request):
    data_form = await request.post()
    return web.json_response(blockchain.exec_encode('addParticipants', data_form))


async def vote(request):
    data_form = await request.post()
    return web.json_response(blockchain.exec_encode('vote', data_form))


async def signSurvey(request):
    data_form = await request.post()
    return web.json_response(blockchain.exect_sign('signSurvey', data_form))


async def signAddParticipants(request):
    data_form = await request.post()
    return web.json_response(blockchain.exect_sign('signAddParticipants', data_form))


async def signVote(request):
    data_form = await request.post()
    return web.json_response(blockchain.exect_sign('signVote', data_form))


async def isSigner(request):
    data_form = await request.post()
    return web.json_response(blockchain.exect_sign('isSigner', data_form))


async def getNonce(request):
    data_form = await request.post()
    try:
        result = blockchain.get_nonce(data_form['address'])
        result = int(result) + 1
        return web.json_response({'nonce': result})
    except Exception as e:
        return web.json_response({'nonce': str(e)})


async def hasVoted(request):
    data_form = await request.post()
    return web.json_response(blockchain.searchLog('hasVoted', data_form))


async def addSigner(request):
    print(f'APICALL ADD SIGNER {blockchain.count}')
    data_form = await request.post()
    return web.json_response(blockchain.exect_sign('addSigner', data_form))


async def removeSigner(request):
    print(f'APICALL REMOVE SIGNER {blockchain.count}')
    data_form = await request.post()
    # return web.json_response(blockchain.exect_sign('removeSigner', data_form))
    return web.json_response({"status": True})  # ATTENZIONE NON RIMUOVE NIENTE, FINTO


async def initSigners(request):
    print(f'APICALL INIT SIGNERS {blockchain.count}')
    try:
        for address in blockchain.user_db_controller.getSignersAddress():
            data_form = {'address': address[0]}
            blockchain.exect_sign('addSigner', data_form)
        return web.json_response({"status": True})
    except Exception as e:
        return web.json_response({"status": str(e)})

app.add_routes([
    web.post('/createSurvey', createSurvey),
    web.post('/AddParticipants', addParticipants),
    web.post('/SignAddparticipants', signAddParticipants),
    web.post('/signSurvey', signSurvey),
    web.post('/AddSigner', addSigner),
    web.post('/RemoveSigner', removeSigner),
    web.post('/InitSigners', initSigners),
    web.post('/GetNonce', getNonce),
    web.post('/Vote', vote),
    web.post('/HasVoted', hasVoted),
    web.post('/SignVote', signVote),
    web.post('/isSigner', isSigner)
])

if __name__ == "__main__":
    web.run_app(app)
