from brownie import accounts
from pylib.smart_contracts import VotingPaperSc
from brownie import network


network_selected = 'development'
try:
    network.connect(network_selected)
except:
    network.connect(network_selected, launch_rpc=False)

voting_paper_sc = VotingPaperSc(accounts[0])
c = voting_paper_sc.deploy()
print(voting_paper_sc.add_minter(accounts[1]))
print(voting_paper_sc.add_minter(accounts[1]))