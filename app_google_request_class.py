"""test"""
from re import findall


class GoogleRequest:
    """test"""
    def __init__(self, org_unit_path, operation_type, config, directory_api_instance, datatransfer_api_instance, fs):
        self.__fs = fs
        self.__config = config
        self.__org_unit_path = org_unit_path
        self.__operation_type = operation_type
        self.__domain = self.__config.get_config()["CREDENTIALS"]["domain"]
        self.__directory_api_instance = directory_api_instance
        self.__datatransfer_api_instance = datatransfer_api_instance
        self.__insert_requests = list()
        self.__update_requests = list()
        self.__batch_update_request = list()
        self.__suspend_requests = list()
        self.__group_member_requests = list()
        self.__group_member_fired_requests = list()
        self.__create_group_requests = list()
        self.__create_alias_requests = list()
        self.__create_insert_request()
        self.__create_update_request()
        # self.__create_batch_update_request()
        self.__create_suspend_request()
        self.__create_group_member_request()
        self.__create_group_request()
        self.__create_alias_request()
        self.__filter(self.__insert_requests)

    def __filter(self, data):
        remove_list = list()
        for index, item_data in enumerate(data):
            for condition in self.__config.get_gsuite_filter():
                if "|" in item_data[0]['organizations'][0][condition[0]]:
                    if condition[1] in item_data[0]['organizations'][0][condition[0]].split(" | "):
                        remove_list.append(index)
                elif item_data[0]['organizations'][0][condition[0]] == condition[1]:
                    remove_list.append(index)
        indices_list = sorted(remove_list, reverse=True)
        for index in indices_list:
            data.pop(index)

    def __create_insert_request(self):
        for source in self.__fs.get_request_add():
            for index in range(len(self.__fs.get_request_add()[source]["name"])):
                account_variant = self.__fs.validation(self.__fs.normalize(
                    self.__fs.get_request_add()[source]["name"][index]),
                    self.__fs.get_request_add()[source]["inn"][index],
                    "email",
                    self.__domain,
                    "gsuite",
                    directory_api_instance=self.__directory_api_instance)
                if account_variant:
                    self.__insert_requests.append([{
                        "orgUnitPath": self.__org_unit_path,
                        "name": {"givenName":
                                     self.__fs.normalize(self.__fs.get_request_add()[source]["name"][index]).split(" ")[1],
                                 "familyName":
                                     self.__fs.normalize(self.__fs.get_request_add()[source]["name"][index]).split(" ")[0]},
                        "primaryEmail":
                            self.__fs.create_account(self.__fs.normalize(self.__fs.get_request_add()[source]["name"][index]),
                                                     account_variant,
                                                     "email",
                                                     self.__domain),
                        "password": self.__fs.generate_password(4, 4, 4),
                        "organizations": [{"title": self.__fs.get_request_add()[source]["position"][index],
                                           "department": self.__fs.get_request_add()[source]["parent2"][index] +
                                                         " | " +
                                                         self.__fs.get_request_add()[source]["parent1"][index] +
                                                         " | " +
                                                         self.__fs.get_request_add()[source]["subdivision"][index]
                                           }],
                        "externalIds": [{"value": self.__fs.get_request_add()[source]["inn"][index],
                                         "type": self.__operation_type}],
                        "customSchemas": {"customSchema": {"deleteMark": "inactive"}}},
                        self.__fs.get_request_add()[source]["uuid"][index],
                        self.__fs.get_request_add()[source]["phone"][index],
                        self.__fs.get_request_add()[source]["division_id"][index]])
                else:
                    pass

    def __create_update_request(self):
        for source in self.__fs.get_request_update():
            for index in range(len(self.__fs.get_request_update()[source]["name"])):
                account = self.__directory_api_instance.get_query('externalId=' +
                                                                  self.__fs.get_request_update()[source]["inn"][index]).get('primaryEmail', None)
                if account:
                    self.__update_requests.append(
                        [account,
                         {"name":
                              {"givenName": self.__fs.normalize(self.__fs.get_request_update()[source]["name"][index]).split(" ")[1],
                               "familyName": self.__fs.normalize(self.__fs.get_request_update()[source]["name"][index]).split(" ")[0]},
                          "organizations": [{"title": self.__fs.get_request_update()[source]["position"][index],
                                             "department": self.__fs.get_request_update()[source]["parent2"][index] + " | " +
                                                           self.__fs.get_request_update()[source]["parent1"][index] + " | " +
                                                           self.__fs.get_request_update()[source]["subdivision"][index]}]},
                         self.__fs.get_request_update()[source]["division_id"][index]])

    def __create_suspend_request(self):
        for source in self.__fs.get_request_suspend():
            for index in range(len(self.__fs.get_request_suspend()[source]["name"])):
                account = self.__directory_api_instance.get_query('externalId=' +
                                                                  self.__fs.get_request_suspend()[source]["inn"][index]).get('primaryEmail', None)
                if account:
                    self.__suspend_requests.append([
                        account,
                        {"suspended": True,
                         "customSchemas": {"customSchema": {"deleteMark": "active"}}}])

    def __create_group_member_request(self):
        update_request = list()
        for request in self.__update_requests:
            update_request.append([{"primaryEmail": request[0], **request[1]}, None, None, request[2]])
        for request in self.__insert_requests + update_request:
            for group in self.__config.get_condition_groups():
                for condition in self.__config.get_condition_groups()[group]:
                    for search_item in request[0]["organizations"][0]["department"].split(" | "):
                        if findall(r'{0}'.format(condition), search_item) or \
                                findall(r'{0}'.format(condition), request[0]["organizations"][0]["title"]) or \
                                condition == 'default':
                            self.__group_member_requests.append([group, {
                                "role": "MEMBER",
                                "type": "USER",
                                "email":  request[0]["primaryEmail"]
                            }])
                            break
                    for search_item in request[3]:
                        if findall(r'{0}'.format(condition), search_item):
                            self.__group_member_requests.append([group, {
                                "role": "MEMBER",
                                "type": "USER",
                                "email": request[0]["primaryEmail"]
                            }])
                            break

    def __create_group_request(self):
        update_request = list()
        for request in self.__update_requests:
            update_request.append([{"primaryEmail": request[0], **request[1]}])
        for request in self.__insert_requests + update_request:
            for condition in self.__config.get_dynamic_groups():
                for search_item in request[0]["organizations"][0]["department"].split(" | "):
                    if findall(condition[2], search_item) and \
                            findall(condition[3], request[0]["organizations"][0]["title"]):
                        if condition[0] == "sub":
                            self.__create_group_requests.append({
                                "name": "{0}".format(condition[1].format(findall(condition[2], search_item)[0])),
                                "email": "{0}".format(condition[1].format(findall(condition[2], search_item)[0]) +
                                                      "@" +
                                                      self.__domain)
                            })
                            self.__group_member_requests.append([condition[1].format(findall(condition[2],
                                                                                             search_item)[0]) +
                                                                 "@" +
                                                                 self.__domain,
                                                                 {
                                                                     "role": "MEMBER",
                                                                     "type": "USER",
                                                                     "email": request[0]["primaryEmail"]
                                                                 }])
                            break

    def __create_alias_request(self):
        update_request = list()
        for request in self.__update_requests:
            update_request.append([{"primaryEmail": request[0], **request[1]}])
        for request in self.__insert_requests + update_request:
            for condition in self.__config.get_alias_rules():
                for search_item in request[0]["organizations"][0]["department"].split(" | "):
                    if findall(condition[2], search_item) and \
                            findall(condition[3], request[0]["organizations"][0]["title"]):
                        if condition[0] == "sub":
                            self.__create_alias_requests.append([request[0]["primaryEmail"], {
                                "alias": "{0}".format(condition[1].format(findall(condition[2], search_item)[0]) +
                                                      "@" +
                                                      self.__domain)
                            }])
                            break

    def get_insert_requests(self):
        return self.__insert_requests

    def get_update_requests(self):
        return self.__update_requests

    def get_suspend_requests(self):
        return self.__suspend_requests

    def get_group_member_requests(self):
        return self.__group_member_requests

    def get_group_member_fired_requests(self):
        for account in self.__datatransfer_api_instance.get_released_accounts():
            self.__group_member_fired_requests.append(["fired-group@varus.ua", {
                "role": "MEMBER",
                "type": "USER",
                "email": self.__directory_api_instance.get_email_by_account_id(account)
            }])
        return self.__group_member_fired_requests

    def get_group_create_request(self):
        return self.__create_group_requests

    def get_alias_request(self):
        return self.__create_alias_requests
