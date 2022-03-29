from brownie import accounts
from pylib.smart_contracts import SmartContractBase
from brownie import network


network_selected = 'development'
try:
    network.connect(network_selected)
except:
    network.connect(network_selected, launch_rpc=False)
voting_paper_sc = SmartContractBase(accounts[0], './', 'VotingPaper')
voting_paper_sc.load_project()
c = voting_paper_sc.deploy()

