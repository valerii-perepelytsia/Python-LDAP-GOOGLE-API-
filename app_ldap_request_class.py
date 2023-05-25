"""test"""
from utils import create_directory, move_files


class LdapRequest:
    """test"""
    def __init__(self, ldap_service, config, fs):
        self.__fs = fs
        self.__ldap_service = ldap_service
        self.__config = config
        self.__insert_requests = dict()
        self.__update_requests = dict()
        self.__suspend_requests = dict()
        self.__insert_supplier_requests = dict()
        self.__suspend_supplier_requests = dict()
        self.__membership_requests = dict()
        self.__request_ad_structures = list()
        self.__create_insert_request()
        self.__create_insert_supplier_request()
        self.__create_update_request()
        self.__create_suspend_request()
        self.__create_suspend_supplier_request()
        self.__create_membership_request()
        for json_file in self.__fs.get_files_import():
            if len(self.__request_ad_structures) > 0:
                if self.__fs.fetch_data(json_file, cp='utf-8')["source"] in [s["source"] for s in self.__request_ad_structures]:
                    for data in self.__request_ad_structures:
                        if data["source"] == self.__fs.fetch_data(json_file, cp='utf-16')["source"]:
                            data.update(self.__fs.fetch_data(json_file, cp='utf-16'))
                else:
                    self.__request_ad_structures.append(self.__fs.fetch_data(json_file, cp='utf-8'))
            else:
                self.__request_ad_structures.append(self.__fs.fetch_data(json_file, cp='utf-8'))

        move_files(create_directory(["Back_up\/staffing_"], True), '*.json', 'Import')

    @staticmethod
    def __rush_lotus_info(string_name):
        """test"""
        lotus_info = str()
        if len(string_name.split(" ")) > 2:
            lotus_info = "CN=" + \
                     string_name.split(" ")[1] + " " + \
                     string_name.split(" ")[2] + " " + \
                     string_name.split(" ")[0] + "/OU=omega/O=rush"
        elif len(string_name.split(" ")) == 2:
            lotus_info = "CN=" + string_name.split(" ")[1] + " " + string_name.split(" ")[0] + "/OU=omega/O=rush"
        else:
            lotus_info = "None"
        return lotus_info

    def __fetch_email(self, uuid):
        """test"""
        email = str()
        if self.__config.get_result().get(uuid, None) is not None:
            email = self.__config.get_result()[uuid]["primaryEmail"]
        else:
            email = 'None'
        return email

    def __create_insert_request(self):
        for source in self.__fs.get_request_add():
            if self.__ldap_service.get(source, None):
                self.__insert_requests[source] = list()
                for index in range(len(self.__fs.get_request_add()[source]["name"])):
                    account_variant = self.__fs.validation(self.__fs.normalize(
                        self.__fs.get_request_add()[source]["name"][index]),
                        self.__fs.get_request_add()[source]["inn"][index],
                        "ldap",
                        self.__config.get_config()["CREDENTIALS"]["domain"],
                        "ldap",
                        ldap_instance=self.__ldap_service[source])
                    if account_variant:
                        self.__insert_requests[source].append([
                            "cn={0},{1},{2},{3}".format(self.__fs.normalize(self.__fs.get_request_add()[source]["name"][index]),
                            "ou=" + ",ou=".join(self.__fs.get_request_add()[source]["division_id"][index]),
                            self.__config.get_config()[self.__config.get_config()["SOURCES"][source]]["ldap_ou_container"],
                            self.__config.get_config()[self.__config.get_config()["SOURCES"][source]]["ldap_domain_components"]),
                            ['organizationalPerson', 'person', 'top', 'user'],
                            {
                                "givenName": self.__fs.normalize(self.__fs.get_request_add()[source]["name"][index]).split(" ")[1],
                                "sn": self.__fs.normalize(self.__fs.get_request_add()[source]["name"][index]).split(" ")[0],
                                "displayName": self.__fs.normalize(self.__fs.get_request_add()[source]["name"][index]),
                                "physicalDeliveryOfficeName":
                                    self.__config.get_config()[self.__config.get_config()["SOURCES"][source]]["ldap_office_name"],
                                "userPrincipalName": self.__fs.create_account(self.__fs.normalize(
                                    self.__fs.get_request_add()[source]["name"][index]),
                                    account_variant, "ldap"),
                                "sAMAccountName": self.__fs.create_account(self.__fs.normalize(
                                    self.__fs.get_request_add()[source]["name"][index]),
                                    account_variant, "ldap"),
                                "profilePath": self.__config.get_config()[self.__config.get_config()["SOURCES"][source]]["ldap_profile_path"] +
                                               self.__fs.create_account(self.__fs.normalize(
                                                   self.__fs.get_request_add()[source]["name"][index]),
                                                   account_variant, "ldap"),
                                "scriptPath": self.__config.get_config()[self.__config.get_config()["SOURCES"][source]]["ldap_script_path"],
                                "company": self.__config.get_config()[self.__config.get_config()["SOURCES"][source]]["ldap_company"],
                                "title": self.__fs.get_request_add()[source]["position"][index],
                                "department": self.__fs.get_request_add()[source]["parent2"][index],
                                "c": self.__config.get_config()[self.__config.get_config()["SOURCES"][source]]["ldap_country"],
                                "l": self.__config.get_config()[self.__config.get_config()["SOURCES"][source]]["ldap_location"],
                                "mail": self.__fetch_email(self.__fs.get_request_add()[source]["uuid"][index]),
                                "info": self.__rush_lotus_info(self.__fs.normalize(self.__fs.get_request_add()[source]["name"][index])),
                                "description": self.__fs.get_request_add()[source]["inn"][index],
                                "mobile": self.__fs.get_request_add()[source]["phone"][index]},
                            self.__fs.generate_password(4, 4, 4), self.__fs.get_request_add()[source]["uuid"][index]])
                    else:
                        pass

    def __create_insert_supplier_request(self):
        for source in self.__fs.get_request_add_supplier():
            if self.__ldap_service.get(source, None):
                self.__insert_supplier_requests[source] = list()
                for index in range(len(self.__fs.get_request_add_supplier()[source]["name"])):
                    account_variant = self.__fs.validation(
                        self.__fs.normalize(
                            self.__fs.get_request_add_supplier()[source]["name"][index]),
                        self.__fs.get_request_add_supplier()[source]["inn"][index],
                        "ldap",
                        self.__config.get_config()["CREDENTIALS"]["domain"],
                        "ldap",
                        ldap_instance=self.__ldap_service[source])
                    if account_variant:
                        self.__insert_supplier_requests[source].append([
                            "cn={0},{1},{2},{3}".format(self.__fs.normalize(self.__fs.get_request_add_supplier()[source]["name"][index]),
                            "ou=" + ",ou=".join(self.__fs.get_request_add_supplier()[source]["division_id"][index]),
                            self.__config.get_config()[self.__config.get_config()["SOURCES"][source]]["ldap_ou_container"],
                            self.__config.get_config()[self.__config.get_config()["SOURCES"][source]]["ldap_domain_components"]),
                            ['organizationalPerson', 'person', 'top', 'user'],
                            {
                                "givenName": self.__fs.normalize(self.__fs.get_request_add_supplier()[source]["name"][index]).split(" ")[1],
                                "sn": self.__fs.normalize(self.__fs.get_request_add_supplier()[source]["name"][index]).split(" ")[0],
                                "displayName": self.__fs.normalize(self.__fs.get_request_add_supplier()[source]["name"][index]),
                                "physicalDeliveryOfficeName":
                                    self.__config.get_config()[self.__config.get_config()["SOURCES"][source]]["ldap_office_name"],
                                "userPrincipalName": self.__fs.create_account(self.__fs.normalize(
                                    self.__fs.get_request_add_supplier()[source]["name"][index]),
                                    account_variant, "ldap"),
                                "sAMAccountName": self.__fs.create_account(self.__fs.normalize(
                                    self.__fs.get_request_add_supplier()[source]["name"][index]),
                                    account_variant, "ldap"),
                                "profilePath": self.__config.get_config()[self.__config.get_config()["SOURCES"][source]]["ldap_profile_path"] +
                                               self.__fs.create_account(self.__fs.normalize(
                                                   self.__fs.get_request_add_supplier()[source]["name"][index]),
                                                   account_variant, "ldap"),
                                "scriptPath": self.__config.get_config()[self.__config.get_config()["SOURCES"][source]]["ldap_script_path"],
                                "company": self.__config.get_config()[self.__config.get_config()["SOURCES"][source]]["ldap_company"],
                                "title": self.__fs.get_request_add_supplier()[source]["position"][index],
                                "department": self.__fs.get_request_add_supplier()[source]["parent2"][index],
                                "c": self.__config.get_config()[self.__config.get_config()["SOURCES"][source]]["ldap_country"],
                                "l": self.__config.get_config()[self.__config.get_config()["SOURCES"][source]]["ldap_location"],
                                "description": self.__fs.get_request_add_supplier()[source]["inn"][index],
                                "mobile": self.__fs.get_request_add_supplier()[source]["phone"][index]},
                            self.__fs.generate_password(4, 4, 4), self.__fs.get_request_add_supplier()[source]["uuid"][index]])
                    else:
                        pass

    def __create_update_request(self):
        for source in self.__fs.get_request_update():
            if self.__ldap_service.get(source, None):
                self.__update_requests[source] = list()
                for index in range(len(self.__fs.get_request_update()[source]["name"])):
                    self.__update_requests[source].append([
                        "{0},{1},{2}".format("ou=" + ",ou=".join(
                            self.__fs.get_request_update()[source]["division_id"][index]),
                                                self.__config.get_config()[self.__config.get_config()["SOURCES"][source]]["ldap_ou_container"],
                                                self.__config.get_config()[self.__config.get_config()["SOURCES"][source]]["ldap_domain_components"]),
                        {
                            "givenName": self.__fs.normalize(self.__fs.get_request_update()[source]["name"][index]).split(" ")[1],
                            "sn": self.__fs.normalize(self.__fs.get_request_update()[source]["name"][index]).split(" ")[0],
                            "displayName": self.__fs.normalize(self.__fs.get_request_update()[source]["name"][index]),
                            "title": self.__fs.get_request_update()[source]["position"][index],
                            "department": self.__fs.get_request_update()[source]["parent2"][index],
                            "description": self.__fs.get_request_update()[source]["inn"][index]
                        }]
                    )

    def __create_suspend_request(self):
        for source in self.__fs.get_request_suspend():
            if self.__ldap_service.get(source, None):
                self.__suspend_requests[source] = list()
                for index in range(len(self.__fs.get_request_suspend()[source]["name"])):
                    self.__suspend_requests[source].append(
                        {
                            "description": self.__fs.get_request_suspend()[source]["inn"][index]
                        }
                    )

    def __create_suspend_supplier_request(self):
        for source in self.__fs.get_request_del_supplier():
            if self.__ldap_service.get(source, None):
                self.__suspend_supplier_requests[source] = list()
                for index in range(len(self.__fs.get_request_del_supplier()[source]["name"])):
                    self.__suspend_supplier_requests[source].append(
                        {
                            "description": self.__fs.get_request_del_supplier()[source]["inn"][index],
                            "mobile": self.__fs.get_request_del_supplier()[source]["phone"][index]
                        }
                    )

    def __create_membership_request(self):
        for source in self.__fs.get_request_add():
            if self.__ldap_service.get(source, None):
                self.__membership_requests[source] = list()
                for index in range(len(self.__fs.get_request_add()[source]["name"])):
                    self.__membership_requests[source].append([self.__fs.get_request_add()[source]["inn"][index],
                                                               self.__fs.get_request_add()[source]["adgroup"][index]])


    def get_ad_structures(self):
        return self.__request_ad_structures

    def get_insert_requests(self):
        return self.__insert_requests

    def get_insert_supplier_requests(self):
        return self.__insert_supplier_requests

    def get_update_requests(self):
        return self.__update_requests

    def get_suspend_requests(self):
        return self.__suspend_requests

    def get_suspend_supplier_requests(self):
        return self.__suspend_supplier_requests

    def get_membership_requests(self):
        return self.__membership_requests
