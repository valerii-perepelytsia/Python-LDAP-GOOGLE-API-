"""test"""
import base64
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from os import path, getcwd
from utils import extra


class GoogleService:
    """test"""
    def __init__(self, service_account_file,
                 google_scopes,
                 credential_delegation_login,
                 google_service_name,
                 google_service_version):
        credentials = service_account.Credentials.from_service_account_file(
            path.join(getcwd(),
                      'Cert',
                      service_account_file),
            scopes=google_scopes,
            subject=credential_delegation_login)
        self.__service = build(google_service_name,
                               google_service_version,
                               credentials=credentials)


class DirectoryAPI(GoogleService):
    """test"""
    def __init__(self, service_account_file,
                 google_scopes,
                 credential_delegation_login,
                 google_service_name,
                 google_service_version,
                 logger):
        GoogleService.__init__(self, service_account_file,
                               google_scopes,
                               credential_delegation_login,
                               google_service_name,
                               google_service_version)
        self.__logger = logger
        self.__accounts = list()
        self.__suspended_accounts = list()
        self.__groups = list()
        self.__fetch_suspended_accounts()
        self.__fetch_groups()

    def __fetch_suspended_accounts(self):
        """test"""
        execution_result = self._GoogleService__service.users().list(customer="my_customer",
                                                                     projection="full",
                                                                     maxResults=500).execute()
        page_token = execution_result.get('nextPageToken', None)

        for user in execution_result['users']:
            if user.get("customSchemas", None) is not None:
                if user['suspended'] is True and user["customSchemas"]["customSchema"]["deleteMark"] == "active":
                    self.__suspended_accounts.append([user['id'],
                                                      user['name']['fullName']])
                else:
                    continue

        while page_token is not None:
            execution_result = self._GoogleService__service.users().list(customer="my_customer",
                                                                         projection="full",
                                                                         maxResults=500,
                                                                         pageToken=page_token).execute()
            for user in execution_result['users']:
                if user.get("customSchemas", None) is not None:
                    if user['suspended'] is True and user["customSchemas"]["customSchema"]["deleteMark"] == "active":
                        self.__suspended_accounts.append([user['id'],
                                                          user['name']['fullName']])
                    else:
                        continue
            page_token = execution_result.get('nextPageToken', None)

    def __fetch_groups(self):
        """test"""
        execution_result = self._GoogleService__service.groups().list(customer='my_customer',
                                                                      maxResults=500).execute()
        page_token = execution_result.get('nextPageToken', None)
        for group in execution_result['groups']:
            self.__groups.append([group.get('name', ''), group.get('email', '')])

        while page_token is not None:
            execution_result = self._GoogleService__service.groups().list(customer='my_customer',
                                                                          pageToken=page_token,
                                                                          maxResults=500).execute()
            for group in execution_result['groups']:
                self.__groups.append([group.get('name', ''), group.get('email', '')])
            page_token = execution_result.get('nextPageToken', None)

    def insert_accounts(self, insert_account_list, config):
        """test"""
        for account in insert_account_list:
            try:
                self._GoogleService__service.users().insert(body=account[0]).execute()
            except HttpError as Error:
                if Error.resp.status in [409]:
                    self.__logger.warning("Entity " + account[0]["primaryEmail"] + " already exist.")
                else:
                    self.__logger.error("app_google_class.py users().insert")
                    self.__logger.error(Error)
            else:
                config.insert_result(account[1], "primaryEmail", account[0]["primaryEmail"])
                config.insert_result(account[1], "emailPassword", account[0]["password"])
                config.insert_result(account[1], "mobile", account[2])
                config.insert_result(account[1], "externalId", account[0]["externalIds"][0]["value"])
                if extra(account[0]['organizations'][0]['department'], config):
                    config.insert_result(account[1],
                                         "extra",
                                         extra(account[0]['organizations'][0]['department'],
                                               config))
                if extra(account[3], config):
                    config.insert_result(account[1],
                                         "extra",
                                         extra(account[3],
                                               config))
                self.__logger.info(account[0]["primaryEmail"] + " created")

    def insert_alias(self, insert_alias_list):
        """test"""
        for account in insert_alias_list:
            old_owner = self.get_email_by_account_id(account[1]['alias'])
            if old_owner is not None:
                try:
                    self._GoogleService__service.users().aliases().delete(userKey=old_owner, alias=account[1]['alias']).execute()
                except Exception as Error:
                    self.__logger.error("app_google_class.py users().aliases().delete ")
                    self.__logger.error(Error)
                else:
                    self.__logger.info("Alias " + account[1]['alias'] + " own by " + old_owner + " deleted.")
                    try:
                        self._GoogleService__service.users().aliases().insert(userKey=account[0],
                                                                              body=account[1]).execute()
                    except Exception as Error:
                        self.__logger.error("app_google_class.py users().aliases().insert")
                        self.__logger.error(Error)
                    else:
                        self.__logger.info("Alias " + account[1]['alias'] + " add to " + account[0])
            else:
                try:
                    self._GoogleService__service.users().aliases().insert(userKey=account[0],
                                                                          body=account[1]).execute()
                except Exception as Error:
                    self.__logger.error("app_google_class.py users().aliases().insert")
                    self.__logger.error(Error)
                else:
                    self.__logger.info("Alias " + account[1]['alias'] + " add to " + account[0])

    def update_accounts(self, update_account_list):
        """test"""
        for account in update_account_list:
            try:
                self._GoogleService__service.users().update(userKey=account[0], body=account[1]).execute()
            except Exception as Error:
                self.__logger.error("app_google_class.py users().update")
                self.__logger.error(Error)
            else:
                if account[1].get('suspended', None):
                    self.__logger.info(account[0] + " suspended")
                else:
                    self.__logger.info(account[0] + " updated")

    def delete_accounts(self, released_accounts):
        """test"""
        for account in released_accounts:
            try:
                email = self.get_email_by_account_id(account)
                self._GoogleService__service.users().delete(userKey=account).execute()
            except Exception as Error:
                self.__logger.error("app_google_class.py users().delete get_email_by_account_id")
                self.__logger.error(Error)
            else:
                self.__logger.info(email + " deleted")

    def create_group(self, create_group_request):
        """test"""
        for template in create_group_request:
            try:
                self._GoogleService__service.groups().insert(body=template).execute()
            except HttpError as Error:
                if Error.resp.status in [409]:
                    self.__logger.warning("Entity " + template["name"] + " already exist.")
                else:
                    self.__logger.error("app_google_class.py groups().insert")
                    self.__logger.error(Error)
            else:
                self.__logger.info("create " + template["name"] + " group")

    def insert_group_member(self, insert_member_request):
        """test"""
        for template in insert_member_request:
            try:
                self._GoogleService__service.members().insert(groupKey=template[0], body=template[1]).execute()
            except HttpError as Error:
                if Error.resp.status in [409]:
                    self.__logger.warning("Member " + template[1]["email"] + " already exist in " + template[0])
                else:
                    self.__logger.error("app_google_class.py members().insert")
                    self.__logger.error(Error)
            else:
                self.__logger.info(template[1]["email"] + " added to group " + template[0])

    def remove_group_member(self, account_list):
        """test"""
        for account in account_list:
            if isinstance(account[0], dict):
                member_key = account[0]["primaryEmail"]
            else:
                member_key = account[0]
            account_groups = self.get_group_query('memberKey='+member_key, 500)
            if len(account_groups) > 0:
                for group in account_groups:
                    try:
                        self._GoogleService__service.members().delete(groupKey=group,
                                                                      memberKey=member_key).execute()
                    except Exception as Error:
                        self.__logger.error("app_google_class.py members().delete")
                        self.__logger.error(Error)
                    else:
                        self.__logger.info(member_key + " removed from group " + group)

    def get_account_id(self, account):
        try:
            account_id = self._GoogleService__service.users().get(userKey=account).execute().get("id", None)
        except Exception as error:
            self.__logger.error("app_google_class.py get_account_id")
            self.__logger.error(error)
        else:
            return account_id

    def get_email_by_account_id(self, account):
        try:
            email = self._GoogleService__service.users().get(userKey=account).execute().get("primaryEmail", None)
        except Exception as error:
            self.__logger.error("app_google_class.py function get_email_by_account_id")
            self.__logger.error(error)
        else:
            return email

    def get_query(self, query):
        """test"""
        result = dict()
        try:
            execution_result = self._GoogleService__service.users().list(customer="my_customer",
                                                                         query=query,
                                                                         projection="full",
                                                                         maxResults=1).execute()
        except Exception as Error:
            self.__logger.error("app_google_class.py users().list query")
            self.__logger.error(Error)
        else:
            if execution_result.get('users', None) is not None:
                result = execution_result['users'][0]

        return result

    def get_group_query(self, query, max_results):
        """test"""
        result = list()
        try:
            execution_result = self._GoogleService__service.groups().list(customer="my_customer",
                                                                          query=query,
                                                                          maxResults=max_results).execute()
        except Exception as Error:
            self.__logger.error("app_google_class.py groups().list")
            self.__logger.error(Error)
        else:
            if execution_result.get('groups', None):
                for group in execution_result['groups']:
                    result.append(group['email'])

        return result

    def get_suspended_accounts(self):
        """test"""
        return self.__suspended_accounts

    def get_groups(self):
        """test"""
        return self.__groups


class DataTransferAPI(GoogleService):
    """test"""
    def __init__(self, service_account_file,
                 google_scopes,
                 credential_delegation_login,
                 google_service_name,
                 google_service_version,
                 directory_api,
                 config,
                 logger):
        GoogleService.__init__(self, service_account_file,
                               google_scopes,
                               credential_delegation_login,
                               google_service_name,
                               google_service_version)
        self.__directory_api = directory_api
        self.__config = config
        self.__logger = logger
        self.__transfers = list()
        self.__completed_transfers = list()
        self.__released_accounts = list()
        self.__fetch_completed_transfers()

    def __fetch_completed_transfers(self):
        """test"""
        for transfer in self._GoogleService__service.transfers().list().execute()["dataTransfers"]:
            self.__transfers.append([transfer['oldOwnerUserId'], transfer['applicationDataTransfers']])

        for transfer in self.__transfers:
            if len(transfer[1]) >= 1:
                for item in transfer[1]:
                    if item['applicationId'] == self.__config["GOOGLEAPI"]["google_api_datatransfer_gdrive_app_id"] and \
                            item['applicationTransferStatus'] == 'completed':
                        self.__completed_transfers.append(transfer[0])

    def insert_transfers(self, suspended_accounts):
        """test"""
        if len(suspended_accounts) > 0:
            for suspended_account in suspended_accounts:
                if suspended_account[0] not in self.__completed_transfers:
                    transfer_template = {
                        "applicationDataTransfers": [
                            {
                                "applicationTransferParams": [
                                    {
                                        "key": "PRIVACY_LEVEL",
                                        "value": ["shared", "private"],
                                    },
                                ],
                                "applicationId": self.__config["GOOGLEAPI"]["google_api_datatransfer_gdrive_app_id"],
                            },
                        ],
                        "newOwnerUserId": "{0}".format(self.__directory_api.get_account_id(
                            self.__config["BACK UP"]["google_back_up_account"])),
                        "oldOwnerUserId": "{0}".format(suspended_account[0]),
                    }
                    try:
                        self._GoogleService__service.transfers().insert(body=transfer_template).execute()
                    except Exception as Error:
                        self.__logger.error("app_google_class.py transfers().insert")
                        self.__logger.error(Error)
                    else:
                        self.__logger.info(self.__directory_api.get_email_by_account_id(transfer_template["oldOwnerUserId"]) +
                                           " transferred to " +
                                           self.__directory_api.get_email_by_account_id(transfer_template["newOwnerUserId"]))
                else:
                    self.__released_accounts.append(suspended_account[0])

    def get_released_accounts(self):
        """test"""
        return self.__released_accounts


class GmailAPI(GoogleService):
    """test"""
    def __init__(self, service_account_file,
                 google_scopes,
                 credential_delegation_login,
                 google_service_name,
                 google_service_version,
                 logger):
        GoogleService.__init__(self, service_account_file,
                               google_scopes,
                               credential_delegation_login,
                               google_service_name,
                               google_service_version)
        self.__logger = logger
        self.__message = MIMEMultipart()

    def send_client_message(self, user, sender, to, subject, message_text):
        """test"""
        self.__message['to'] = to
        self.__message['from'] = sender
        self.__message['subject'] = subject
        html_mime = MIMEText(message_text, 'html')
        self.__message.attach(html_mime)
        base64_message = {'raw': base64.urlsafe_b64encode(self.__message.as_string().encode('UTF-8')).decode('ascii'),
                          'payload': {'mimeType': 'text/html'}}
        try:
            self._GoogleService__service.users().messages().send(userId=user, body=base64_message).execute()
        except Exception as Error:
            self.__logger.error("app_google_class.py users().messages().send")
            self.__logger.error(Error)
