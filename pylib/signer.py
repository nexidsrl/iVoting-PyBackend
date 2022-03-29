from brownie.network.account import LocalAccount
from brownie import web3



class Signer:

    """
    Classe che gestisce l'indirizzo che firma le transazioni per inoltrarle

    """

    def __init__(self, private_key):
        """
        :param private_key: - string - Chiave privata

        """
        self.signer = web3.eth.account.from_key(private_key)
        self.account = LocalAccount(self.signer.address, self.signer, self.signer.privateKey)
        self.nonce = 0

    def signData(self, hash):
        """
        Firma l'hash
        :param hash: string - Hash
        :return: dict - hash firmato
        """
        return self.signer.signHash(hash)

    def keccak(self, text):
        """

        :param text: string - testo di cui fare l'hash
        :return:
        """
        return web3.keccak(text=text)

    def set_nonce(self, nonce):
        """

        :param nonce: int - nonce da cui ripartire
        :return:
        """
        self.nonce = nonce

    def get_nonce(self):
        """
        Funzione che restituisce l'ultimo nonce utilizzato
        :return: int
        return self.nonce
        """

    def gen_nonce(self):
        """
        Utilizza nonce
        :return: int - nonce generato
        """
        self.nonce += 1
        return self.nonce
