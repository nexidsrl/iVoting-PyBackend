from brownie import Contract, project


class SmartContractBase:

    def __init__(self, deployer_account, project_path, project_name):
        """

        :param deployer_account: LocalAccount - Oggetto LocalAccount web3
        :param project_path: string - Percorso del progetto
        :param project_name: string - Nome dello Smart Contract
        """
        self.deployer_account = deployer_account
        self.project_path = project_path
        self.project_name = project_name

    def load_project(self):
        self.project = project.load(self.project_path, name=self.project_name)
        self.project.load_config()

    def deploy(self, init_parameters=[]):
        self.deployed_contract = self.deployer_account.deploy(getattr(self.project, self.project_name), *init_parameters)
        return self.deployed_contract.address

    def load_smart_contract(self, address):
        self.deployed_contract = getattr(self.project, self.project_name).at(address, owner=self.deployer_account)
        return self.deployed_contract

    def get_sc_address(self):
        return self.deployed_contract.address


class VotingPaperSc(SmartContractBase):

    name = "VotingPaper"
    project_path = "./"

    def __init__(self, deployer_account):
        super().__init__(deployer_account, self.project_path, self.name)
        self.load_project()

    def add_minter(self, account):
        """

        :param account: LocalAccount -
        :return:
        """
        if not self.deployed_contract.isMinter(account):
            try:
                receipt = self.deployed_contract.addMinter(account)
            except Exception as e:
                print("Unable to add {} as Minter. Error: {}".format(account, e))
                return False
            if receipt.status == 0:
                print("Unable to add {} as Minter. Error: {}".format(account, receipt.rever_msg))
                return False
        return True

    def add_transferer(self, account):
        """

        :param account: LocalAccount -
        :return:
        """
        if not self.deployed_contract.isTransferer(account):
            try:
                receipt = self.deployed_contract.addTransferer(account)
            except Exception as e:
                print("Unable to add {} as Transferer. Error: {}".format(account, e))
                return False
            if receipt.status == 0:
                print("Unable to add {} as Transferer. Error: {}".format(account, receipt.rever_msg))
                return False
        return True

    def add_voter(self, account):
        """

        :param account: LocalAccount -
        :return:
        """
        if not self.deployed_contract.isVoter(account):
            try:
                receipt = self.deployed_contract.addVoter(account)
            except Exception as e:
                print("Unable to add {} as Voter. Error: {}".format(account, e))
                return False
            if receipt.status == 0:
                print("Unable to add {} as Voter. Error: {}".format(account, receipt.rever_msg))
                return False
        return True

    def get_voting_paper_metadata(self, id):
        return self.deployed_contract.getVotingPaperStructMetadata(id)

    def balance_of(self, address):
        return self.deployed_contract.balanceOf(address)


class Ballot(SmartContractBase):

    name = "Ballot"
    project_path = "./"

    def __init__(self, deployer_account):
        super().__init__(deployer_account, self.project_path, self.name)
        self.load_project()

    def add_maintainer(self, account):
        """

        :param account: LocalAccount -
        :return:
        """
        if not self.deployed_contract.isMaintainer(account):
            try:
                receipt = self.deployed_contract.addMaintainer(account)
            except Exception as e:
                print("Unable to add {} as Maintainer. Error: {}".format(account, e))
                return False
            if receipt.status == 0:
                print("Unable to add {} as Maintainer. Error: {}".format(account, receipt.rever_msg))
                return False
        return True

    def add_signer(self, account):
        """

        :param account: LocalAccount -
        :return:
        """
        if not self.deployed_contract.isSigner(account):
            try:
                receipt = self.deployed_contract.addSigner(account)
            except Exception as e:
                print("Unable to add {} as Signer. Error: {}".format(account, e))
                return False
            if receipt.status == 0:
                print("Unable to add {} as Signer. Error: {}".format(account, receipt.rever_msg))
                return False
        return True

    def set_voting_paper_address(self, sc_address):
        if not self.deployed_contract.checkVotingPaperAddr(sc_address):
            try:
                receipt = self.deployed_contract.setVotingPaperAddr(sc_address)
            except Exception as e:
                print("Unable to add {} as Signer. Error: {}".format(sc_address, e))
                return False
            if receipt.status == 0:
                print("Unable to add {} as Signer. Error: {}".format(sc_address, receipt.rever_msg))
                return False
        return True

    def set_grace_time(self, id_survey, new_grace_time):
        try:
            receipt = self.deployed_contract.setSurveyGraceTime(id_survey, new_grace_time)
        except Exception as e:
            print("Unable to change grace time. Error: {}".format(e))
            return False
        if receipt.status == 0:
            print("Unable to change grace time. Error: {}".format(receipt.rever_msg))
            return False
        return True

    def get_grace_time(self, id_survey):
        return self.deployed_contract.surveyGraceTime(id_survey)


    def encode_survey_data(self, start_survey, end_survey, hash_answer, multiple_answer, uri, nonce):
        """

        :param start_survey:
        :param end_survey:
        :param hash_answer:
        :param multiple_answer:
        :param uri:
        :param nonce:
        :return:
        """
        return self.deployed_contract.encodeSurveyData(start_survey, end_survey, hash_answer, multiple_answer, uri,
                                                       nonce)

    def new_survey(self, start_survey, end_survey, hash_answer, multiple_answer, uri, nonce, v, r, s):
        try:
            receipt = self.deployed_contract.createSurvey(start_survey, end_survey, hash_answer, multiple_answer, uri,
                                                          nonce, v, r, s)
        except Exception as e:
            print("Unable to start a new survey. Error: {}".format(e))
            return False, None
        if receipt.status == 0:
            print("Unable to start a new survey. Error: {}".format(receipt.rever_msg))
            return False, None
        return receipt.events['newSurvey']['_surveyId']

    def get_survey_metadata(self, id):
        return self.deployed_contract.getSurveyMetadata(id)

    def encode_participants_data(self, survey_id, participants, nonce):
        """

        :param survey_id:
        :param participants:
        :param nonce:
        :return:
        """
        return self.deployed_contract.encodeAddParticipantsData(survey_id, participants, nonce)

    def add_participants(self, survey_id, participants, nonce, v, r, s):
        try:
            receipt = self.deployed_contract.addParticipants(survey_id, participants, nonce,
                                                             v, r, s)
        except Exception as e:
            print("Unable to add participants. Error: {}".format(e))
            return False, None
        if receipt.status == 0:
            print("Unable to add participants. Error: {}".format(receipt.rever_msg))
            return False, None
        return receipt.return_value, receipt.sender

    def encode_vote_data(self, survey_id, response, nonce):
        """

        :param survey_id:
        :param response:
        :param nonce:
        :return:
        """
        return self.deployed_contract.encodeVoteData(survey_id, response, nonce)

    def vote(self, survey_id, response, nonce, v, r, s):
        try:
            receipt = self.deployed_contract.vote(survey_id, response, nonce,
                                                             v, r, s)
        except Exception as e:
            print("Unable to vote. Error: {}".format(e))
            return False, None
        if receipt.status == 0:
            print("Unable to vote. Error: {}".format(receipt.rever_msg))
            return False, None
        return receipt.return_value, receipt.sender

    def get_token_id_in_survey(self, address, survey_id, id):
        return self.deployed_contract.addressToSurveyTknId(address, survey_id, id)


class Delegate(SmartContractBase):

    name = "Delegate"
    project_path = "./"

    def __init__(self, deployer_account):
        super().__init__(deployer_account, self.project_path, self.name)
        self.load_project()

    def add_maintainer(self, account):
        """

        :param account: LocalAccount -
        :return:
        """
        if not self.deployed_contract.isMaintainer(account):
            try:
                receipt = self.deployed_contract.addMaintainer(account)
            except Exception as e:
                print("Unable to add {} as Maintainer. Error: {}".format(account, e))
                return False
            if receipt.status == 0:
                print("Unable to add {} as Maintainer. Error: {}".format(account, receipt.rever_msg))
                return False
        return True

    def set_voting_paper_address(self, sc_address):
        if not self.deployed_contract.checkVotingPaperAddr(sc_address):
            try:
                receipt = self.deployed_contract.setVotingPaperAddr(sc_address)
            except Exception as e:
                print("Unable to add {} as Signer. Error: {}".format(sc_address, e))
                return False
            if receipt.status == 0:
                print("Unable to add {} as Signer. Error: {}".format(sc_address, receipt.rever_msg))
                return False
        return True

    def set_ballot_address(self, sc_address):
        if not self.deployed_contract.checkBallotAddr(sc_address):
            try:
                receipt = self.deployed_contract.setBallotAddr(sc_address)
            except Exception as e:
                print("Unable to add {} as Signer. Error: {}".format(sc_address, e))
                return False
            if receipt.status == 0:
                print("Unable to add {} as Signer. Error: {}".format(sc_address, receipt.rever_msg))
                return False
        return True

    def encode_delegate_data(self, to, token_id, nonce):
        """

        :param to:
        :param token_id:
        :param nonce:
        :return:
        """
        return self.deployed_contract.encodeDelegateData(to, token_id, nonce)

    def delegate(self, to, token_id, nonce, signature):
        try:
            receipt = self.deployed_contract.delegateDelegated(to, token_id, nonce, signature['v'], signature['r'],
                                                               signature['s'])
        except Exception as e:
            print("Unable to delegate. Error: {}".format(e))
            return False, None
        if receipt.status == 0:
            print("Unable to delegate. Error: {}".format(receipt.rever_msg))
            return False, None
        return receipt.return_value, receipt.sender
