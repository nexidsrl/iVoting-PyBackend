from brownie import network, config
from pylib.smart_contracts import Ballot
from pylib.smart_contracts import VotingPaperSc
from pylib.smart_contracts import Delegate
import json
import os

class SmartContractManager():


    def __init__(self, network_selected):
        with open('./brownie-config.json') as json_file:
            bc_json = json.load(json_file)
        config['network']['networks']['nexid'] = bc_json['network']['networks']['nexid']
        try:
            network.connect(network_selected)
        except:
            network.connect(network_selected, launch_rpc=False)

    def set_deployer_account(self, deployer_account):
        self.deployer_account = deployer_account

    def deploy_platform(self):
        self.ballot_sc = Ballot(self.deployer_account)
        self.voting_paper_sc = VotingPaperSc(self.deployer_account)
        self.delegate_sc = Delegate(self.deployer_account)
        self.ballot_sc.deploy()
        self.voting_paper_sc.deploy()
        self.delegate_sc.deploy()
        self.voting_paper_sc.add_minter(self.ballot_sc.deployed_contract)
        self.voting_paper_sc.add_voter(self.ballot_sc.deployed_contract)
        self.voting_paper_sc.add_transferer(self.delegate_sc.deployed_contract)
        self.ballot_sc.set_voting_paper_address(self.voting_paper_sc.deployed_contract.address)
        self.delegate_sc.set_voting_paper_address(self.voting_paper_sc.deployed_contract.address)
        self.delegate_sc.set_ballot_address(self.ballot_sc.deployed_contract.address)
        return self.ballot_sc, self.voting_paper_sc , self.delegate_sc

