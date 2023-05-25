"""test"""
from ldap3 import Connection as LdapConnection, Server as LdapServer, ALL, SUBTREE
from datetime import datetime


class LdapService:
    """test"""
    def __init__(self, config, source, logger):
        self.__config = config
        self.__source = source
        self.__logger = logger
        self.status = False
        try:
            self.__connection = LdapConnection(LdapServer(self.__config.get_config()[self.__source]["ldap_server"],
                                                          get_info=ALL,
                                                          use_ssl=bool(self.__config.get_config()[self.__source]["ldap_ssl"])),
                                               self.__config.get_config()[self.__source]["ldap_login"],
                                               self.__config.get_config()[self.__source]["ldap_password"],
                                               auto_bind=True)
        except Exception as Error:
            self.__logger.error("app_ldap_class.py class LdapService")
            self.__logger.error(Error)
            self.status = False
        else:
            self.status = True
            self.__accounts = list()
            self.__fetch_accounts()

    def __fetch_accounts(self):
        """test"""
        try:
            self.__connection.search(search_base=self.__config.get_config()[self.__source]["ldap_search_base"],
                                     search_filter='(objectClass=person)',
                                     search_scope=SUBTREE,
                                     attributes=['sAMAccountName',
                                                 'description',
                                                 'mobile',
                                                 'mail',
                                                 'distinguishedname'])
        except Exception as Error:
            self.__logger.error("app_ldap_class.py def __fetch_accounts")
            self.__logger.error(Error)
        else:
            self.__accounts = [[entry.sAMAccountName.value,
                                entry.description.value,
                                entry.mobile.value,
                                entry.mail.value,
                                entry.distinguishedname.value] for entry in self.__connection.entries]

    def insert_organizational_units(self, organizational_units):
        """test"""
        for ldap_node in organizational_units["nodes"]:
            ou = "ou=" + \
                 ldap_node["id"] + \
                 ("," + ",".join(["ou=" + i for i in ldap_node["ancestors"]])) \
                if len(ldap_node["ancestors"]) > 0 else "ou=" + ldap_node["id"]
            try:
                status = self.__connection.add(ou + "," +
                                               self.__config.get_config()[self.__source]["ldap_ou_container"] + "," +
                                               self.__config.get_config()[self.__source]["ldap_domain_components"],
                                               'organizationalUnit', {'description': ldap_node["description"]})
            except Exception as Error:
                self.__logger.error("app_ldap_class.py def insert_organizational_units")
                self.__logger.error(Error)
            else:
                if status is True:
                    self.__logger.info(str(self.__source).upper() +
                                       " Organizational unit (" +
                                       ldap_node["description"] +
                                       ") added")

    def get_accounts(self):
        return self.__accounts

    def get_query(self, query, attribute):
        """test"""
        result = None
        try:
            self.__connection.search(search_base=self.__config.get_config()[self.__source]["ldap_search_base"],
                                     search_filter=query,
                                     search_scope=SUBTREE,
                                     attributes=attribute)
        except Exception as Error:
            self.__logger.error("app_ldap_class.py def get_query")
            self.__logger.error(Error)
        else:
            if len(self.__connection.entries) != 0:
                result = self.__connection.entries[0][attribute[0]].value

        return result

    def insert_ldap_users(self, ldap_users, mode="user"):
        """test"""
        for user in ldap_users:
            try:
                user_status = self.__connection.add(user[0], user[1], user[2])
            except Exception as Error:
                self.__logger.error("app_ldap_class.py self.__connection.add")
                self.__logger.error(Error)
            else:
                if user_status:
                    self.__logger.info("LDAP user " + str(user[0]) + " added to " + str(self.__source).upper())
                    try:
                        password_status = self.__connection.extend.microsoft.modify_password(user[0], user[3])
                    except Exception as Error:
                        self.__logger.error("app_ldap_class.py self.__connection.extend.microsoft.modify_password")
                        self.__logger.error(Error)
                    else:
                        if password_status:
                            self.__logger.info(
                                "LDAP user " + str(user[0]) + " password set " + str(self.__source).upper())
                    try:
                        enable_status = self.__connection.modify(user[0],
                                                                 {'userAccountControl': [('MODIFY_REPLACE', 512)]})
                    except Exception as Error:
                        self.__logger.error("app_ldap_class.py self.__connection.modify")
                        self.__logger.error(Error)
                    else:
                        if enable_status:
                            self.__logger.info("LDAP user " + str(user[0]) + " enabled " + str(self.__source).upper())
                    try:
                        self.__connection.modify(user[0], {'pwdLastSet': ('MODIFY_REPLACE', [-1])})
                    except Exception as Error:
                        self.__logger.error("app_ldap_class.py self.__connection.modify pwdLastSet")
                        self.__logger.error(Error)

                if mode == "user":
                    if user_status:
                        self.__config.insert_result(user[4], "ldapLogin", user[2]["userPrincipalName"])
                        self.__config.insert_result(user[4], "ldapPassword", user[3])
                        self.__config.insert_result(user[4], "mobile", user[2]['mobile'])
                elif mode == "supplier":
                    if user_status:
                        message = "xx " \
                                  "xx " + \
                                  user[2]["userPrincipalName"] + "@netomega" + \
                                  "xx " + user[3] + \
                                  "xx " \
                                  "xx xx@xx.xx."
                        self.__config.post_client_message(user[2]['mobile'], message, message)
                        self.__config.pg_insert_suppliers(user[2]["userPrincipalName"],
                                                          user[3],
                                                          user[2]["description"],
                                                          user[2]['mobile'])

    def suspend_ldap_users(self, ldap_users):
        """test"""
        for user in ldap_users:
            distinguished_name = self.get_query('(description={0})'.format(user['description']), ['distinguishedName'])
            if distinguished_name is not None:
                try:
                    self.__connection.modify(distinguished_name, {'userAccountControl': [('MODIFY_REPLACE', 2)]})
                except Exception as Error:
                    self.__logger.error("app_ldap_class.py def suspend_ldap_users")
                    self.__logger.error(Error)
                else:
                    self.__logger.info("LDAP user " + str(distinguished_name) + " suspended " + str(self.__source).upper())
                try:
                    self.__connection.modify(distinguished_name,
                                             {'physicalDeliveryOfficeName': [('MODIFY_REPLACE',
                                                                              ['suspended by script at ' +
                                                                               datetime.now().strftime('%H:%M:%S %d-%m-%Y')])]})
                except Exception as Error:
                    self.__logger.error("app_ldap_class.py def suspend_ldap_users")
                    self.__logger.error(Error)

    def suspend_ldap_supplier(self, ldap_users):
        for user in ldap_users:
            distinguished_name = self.get_query('(&(description={0})(mobile={1}))'.format(user['description'],
                                                                                          user['mobile']),
                                                ['distinguishedName'])
            if distinguished_name is not None:
                try:
                    self.__connection.modify(distinguished_name, {'userAccountControl': [('MODIFY_REPLACE', 2)]})
                except Exception as Error:
                    self.__logger.error("app_ldap_class.py")
                    self.__logger.error(Error)
                else:
                    message = "xx " \
                              "xx"
                    self.__config.post_client_message(user['mobile'], message, message)
                    self.__logger.info("LDAP user " + str(distinguished_name) + " suspended " + str(self.__source).upper())
                try:
                    self.__connection.modify(distinguished_name,
                                             {'physicalDeliveryOfficeName': [('MODIFY_REPLACE',
                                                                              ['suspended by script at ' +
                                                                               datetime.now().strftime('%H:%M:%S %d-%m-%Y')])]})
                except Exception as Error:
                    self.__logger.error("app_ldap_class.py")
                    self.__logger.error(Error)

    def update_ldap_users(self, ldap_users):
        """test"""
        for user in ldap_users:
            distinguished_name = self.get_query('(description={0})'.format(user[1]['description']), ['distinguishedName'])
            if distinguished_name is not None:
                try:
                    self.__connection.modify(distinguished_name, {'givenName': [('MODIFY_REPLACE', user[1]['givenName'])]})
                except Exception as Error:
                    self.__logger.error("app_ldap_class.py")
                    self.__logger.error(Error)
                else:
                    self.__logger.info("LDAP user " + str(distinguished_name) + " given name updated to " +
                                       str(user[1]['givenName']) + " " + str(self.__source).upper())
                try:
                    self.__connection.modify(distinguished_name, {'sn': [('MODIFY_REPLACE', user[1]['sn'])]})
                except Exception as Error:
                    self.__logger.error("app_ldap_class.py")
                    self.__logger.error(Error)
                else:
                    self.__logger.info("LDAP user " + str(distinguished_name) + " surname updated to " +
                                       str(user[1]['sn']) + " " + str(self.__source).upper())
                try:
                    self.__connection.modify(distinguished_name, {'displayName': [('MODIFY_REPLACE', user[1]['displayName'])]})
                except Exception as Error:
                    self.__logger.error("app_ldap_class.py")
                    self.__logger.error(Error)
                else:
                    self.__logger.info("LDAP user " + str(distinguished_name) + " display name updated to " +
                                       str(user[1]['displayName']) + " " + str(self.__source).upper())
                try:
                    self.__connection.modify(distinguished_name, {'title': [('MODIFY_REPLACE', user[1]['title'])]})
                except Exception as Error:
                    self.__logger.error("app_ldap_class.py")
                    self.__logger.error(Error)
                else:
                    self.__logger.info("LDAP user " + str(distinguished_name) + " title updated to " +
                                       str(user[1]['title']) + " " + str(self.__source).upper())
                try:
                    self.__connection.modify(distinguished_name, {'department': [('MODIFY_REPLACE', user[1]['department'])]})
                except Exception as Error:
                    self.__logger.error("app_ldap_class.py")
                    self.__logger.error(Error)
                else:
                    self.__logger.info("LDAP user " + str(distinguished_name) + " department updated to " +
                                       str(user[1]['department']) + " " + str(self.__source).upper())
                try:
                    self.__connection.modify_dn(distinguished_name, distinguished_name.split(",")[0],
                                                new_superior=user[0])
                except Exception as Error:
                    self.__logger.error("app_ldap_class.py")
                    self.__logger.error(Error)
                else:
                    self.__logger.info("LDAP user " + str(distinguished_name) + " set new superior " +
                                       str(user[0]) + " " + str(self.__source).upper())
            else:
                self.__logger.warning(user[1]['displayName'] + " not found!")

    def insert_members_to_group(self, ldap_users):
        for user in ldap_users:
            distinguished_name = self.get_query('(description={0})'.format(user[0]), ['distinguishedName'])
            for group in user[1]:
                try:
                    self.__connection.extend.microsoft.add_members_to_groups(distinguished_name, group)
                except Exception as Error:
                    self.__logger.error("app_ldap_class.py  def insert_members_to_group")
                    self.__logger.error(Error)
                else:
                    self.__logger.info("LDAP user " + str(distinguished_name) + " added to group " +
                                       str(group) + " " + str(self.__source).upper())

    def set_password(self, dn, password, pwdls):
        result = False
        try:
            self.__connection.extend.microsoft.modify_password(dn, password)
        except Exception as Error:
            self.__logger.error("app_ldap_class.py")
            self.__logger.error(Error)
        else:
            print("LDAP user " + str(dn) + " password change to " + str(password))
            self.__logger.info("LDAP user " + str(dn) + " password change to " + str(password))
            try:
                self.__connection.modify(dn, {'pwdLastSet': ('MODIFY_REPLACE', [pwdls])})
            except Exception as Error:
                self.__logger.error("app_ldap_class.py")
                self.__logger.error(Error)
            else:
                print("User must change password set to " + str(pwdls))
                result = True

        return result

