"""test"""
from fnmatch import filter as fnmfilter
from os import path, getcwd, listdir
from uuid import uuid4
from json import load
from random import choice, shuffle
from string import ascii_uppercase, ascii_lowercase, digits
from re import sub
from translitua import translit
from utils import merge_dictionary, create_directory, move_files


class Fs:
    """test"""
    def __init__(self, config):
        self.__config = config
        self.__json_files_root = fnmfilter(listdir(path.join(getcwd())), '*.json')
        self.__json_files_import = [path.join(getcwd(), "Import", i)
                                    for i in fnmfilter(listdir(path.join(getcwd(), "Import")), '*.json')]
        self.__request_add = dict()
        self.__request_update = dict()
        self.__request_suspend = dict()
        self.__request_add_supplier = dict()
        self.__request_del_supplier = dict()
        self.__request_batch_update = dict()
        for data in self.__json_files_root:
            if self.fetch_data(data)["operation"] == 'add':
                if self.__request_add.get(self.fetch_data(data)["source"], None) is not None:
                    self.__request_add[self.fetch_data(data)["source"]] = \
                        merge_dictionary(self.__request_add[self.fetch_data(data)["source"]],
                                         self.fetch_data(data, uuid=True))
                else:
                    self.__request_add[self.fetch_data(data)["source"]] = dict()
                    self.__request_add[self.fetch_data(data)["source"]] = \
                        merge_dictionary(self.__request_add[self.fetch_data(data)["source"]],
                                         self.fetch_data(data, uuid=True))
                self.__filter(self.__request_add)
            elif self.fetch_data(data)["operation"] == 'update':
                if self.__request_update.get(self.fetch_data(data)["source"], None) is not None:
                    self.__request_update[self.fetch_data(data)["source"]] = \
                        merge_dictionary(self.__request_update[self.fetch_data(data)["source"]],
                                         self.fetch_data(data, uuid=True))
                else:
                    self.__request_update[self.fetch_data(data)["source"]] = dict()
                    self.__request_update[self.fetch_data(data)["source"]] = \
                        merge_dictionary(self.__request_update[self.fetch_data(data)["source"]],
                                         self.fetch_data(data, uuid=True))
                self.__filter(self.__request_update)
            elif self.fetch_data(data)["operation"] == 'suspend':
                if self.__request_suspend.get(self.fetch_data(data)["source"], None) is not None:
                    self.__request_suspend[self.fetch_data(data)["source"]] = \
                        merge_dictionary(self.__request_suspend[self.fetch_data(data)["source"]],
                                         self.fetch_data(data, uuid=True))
                else:
                    self.__request_suspend[self.fetch_data(data)["source"]] = dict()
                    self.__request_suspend[self.fetch_data(data)["source"]] = \
                        merge_dictionary(self.__request_suspend[self.fetch_data(data)["source"]],
                                         self.fetch_data(data, uuid=True))
                self.__filter(self.__request_suspend)
            elif self.fetch_data(data)["operation"] == 'add_supplier':
                if self.__request_add_supplier.get(self.fetch_data(data)["source"], None) is not None:
                    self.__request_add_supplier[self.fetch_data(data)["source"]] = \
                        merge_dictionary(self.__request_add_supplier[self.fetch_data(data)["source"]],
                                         self.fetch_data(data, uuid=True))
                else:
                    self.__request_add_supplier[self.fetch_data(data)["source"]] = dict()
                    self.__request_add_supplier[self.fetch_data(data)["source"]] = \
                        merge_dictionary(self.__request_add_supplier[self.fetch_data(data)["source"]],
                                         self.fetch_data(data, uuid=True))
                self.__filter(self.__request_add_supplier)
            elif self.fetch_data(data)["operation"] == 'del_supplier':
                if self.__request_del_supplier.get(self.fetch_data(data)["source"], None) is not None:
                    self.__request_del_supplier[self.fetch_data(data)["source"]] = \
                        merge_dictionary(self.__request_del_supplier[self.fetch_data(data)["source"]],
                                         self.fetch_data(data, uuid=True))
                else:
                    self.__request_del_supplier[self.fetch_data(data)["source"]] = dict()
                    self.__request_del_supplier[self.fetch_data(data)["source"]] = \
                        merge_dictionary(self.__request_del_supplier[self.fetch_data(data)["source"]],
                                         self.fetch_data(data, uuid=True))
                self.__filter(self.__request_del_supplier)
            elif self.fetch_data(data)["operation"] == 'batch_update':
                if self.__request_batch_update.get(self.fetch_data(data)["source"], None) is not None:
                    self.__request_batch_update[self.fetch_data(data)["source"]] = \
                        merge_dictionary(self.__request_batch_update[self.fetch_data(data)["source"]],
                                         self.fetch_data(data))
                else:
                    self.__request_batch_update[self.fetch_data(data)["source"]] = dict()
                    self.__request_batch_update[self.fetch_data(data)["source"]] = \
                        merge_dictionary(self.__request_batch_update[self.fetch_data(data)["source"]],
                                         self.fetch_data(data))

        move_files(create_directory(["Back_up\/export_"], True), '*.json', 'Export', False)
        move_files(create_directory(["Back_up\/operations_"], True), '*.json')

    def __filter(self, data):
        remove_sources = list()
        for source in data:
            for condition in self.__config.get_filter():
                try:
                    index = data[source][condition[0]].index(condition[1])
                except ValueError:
                    pass
                else:
                    data[source]["name"].pop(index)
                    data[source]["phone"].pop(index)
                    data[source]["inn"].pop(index)
                    data[source]["position"].pop(index)
                    data[source]["subdivision"].pop(index)
                    data[source]["parent1"].pop(index)
                    data[source]["parent2"].pop(index)
                    data[source]["email"].pop(index)
                    data[source]["adgroup"].pop(index)
                    data[source]["division_id"].pop(index)
                    data[source]["uuid"].pop(index)
            if len(data[source]["name"]) == 0:
                remove_sources.append(source)

        if len(remove_sources) > 0:
            for source in remove_sources:
                data.pop(source, None)

    @staticmethod
    def fetch_data(json_file, cp='utf-8', uuid=False):
        """test"""
        with open(json_file, "r", encoding=cp) as opened_json_file:
            json_loaded_file = load(opened_json_file)
            if uuid is not False:
                json_loaded_file["uuid"] = [str(uuid4()) for u in range(len(json_loaded_file["name"]))]

        return json_loaded_file

    @staticmethod
    def normalize(name, mode=0):
        """test"""
        normalized_name = str()
        if mode == 0:
            sub_maiden_name_string = sub(r'\((\s?|\s+)\w+\W?\w+(\s?|\s+)\)', '', name)
            temp = " ".join([n.capitalize() for n in sub_maiden_name_string.split(" ")])
            normalized_name = " ".join(list(filter((lambda item: item != ''), temp.split(" "))))
        return normalized_name

    @staticmethod
    def generate_password(min_upchar, min_lchar, min_dig):
        """test"""
        characters = []
        i = 1
        while i <= min_upchar:
            characters.append(choice(ascii_uppercase))
            i += 1
        i = 1
        while i <= min_lchar:
            characters.append(choice(ascii_lowercase))
            i += 1
        i = 1
        while i <= min_dig:
            characters.append(choice(digits))
            i += 1
        shuffle(characters)
        return "".join(characters)

    @staticmethod
    def create_account(name, mode, account_type="email", domain=None):
        """test"""
        new_account_name = str()
        # aaa.bbb
        if mode == 1:
            if len(translit(name).split(' ')) >= 2:
                if account_type == "email":
                    new_account_name = translit(name).split(' ')[1].lower() + \
                                       '.' + \
                                       translit(name).split(' ')[0].lower() + \
                                       '@' + \
                                       domain
                elif account_type == "ldap":
                    new_account_name = translit(name).split(' ')[1].lower() + \
                                       '.' + \
                                       translit(name).split(' ')[0].lower()
                    if len(new_account_name) > 20:
                        new_account_name = translit(name).split(' ')[1][0].lower() + \
                                           '.' + \
                                           translit(name).split(' ')[0].lower()
            else:
                new_account_name = None
        # a.bbb
        elif mode == 2:
            if len(translit(name).split(' ')[1]) > 1:
                if account_type == "email":
                    new_account_name = translit(name).split(' ')[1][0].lower() + \
                                       '.' + \
                                       translit(name).split(' ')[0].lower() + \
                                       '@' + \
                                       domain
                elif account_type == "ldap":
                    new_account_name = translit(name).split(' ')[1][0].lower() + \
                                       '.' + \
                                       translit(name).split(' ')[0].lower()
            else:
                new_account_name = None
        # a.d.bbb
        elif mode == 3:
            if ((len(translit(name).split(' ')) > 2) and
                (len(translit(name).split(' ')[2]) > 1)) and \
                    (len(translit(name).split(' ')[1]) > 1):
                if account_type == "email":
                    new_account_name = translit(name).split(' ')[1][0].lower() + \
                                       '.' + \
                                       translit(name).split(' ')[2][0].lower() + \
                                       '.' + \
                                       translit(name).split(' ')[0].lower() + \
                                       '@' + \
                                       domain
                elif account_type == "ldap":
                    new_account_name = translit(name).split(' ')[1][0].lower() + \
                                       '.' + \
                                       translit(name).split(' ')[2][0].lower() + \
                                       '.' + \
                                       translit(name).split(' ')[0].lower()
            else:
                new_account_name = None
        return new_account_name


    @staticmethod
    def account_verification(account, user_id, mode, ldap_instance=None, directory_api_instance=None):
        """Фунцкия проверки уже сущевствующих аккаунтов"""
        verification_result = list()
        if mode == 'ldap' and ldap_instance is not None:
            if account is not None:
                if ldap_instance.get_query('(sAMAccountName='+account+')',
                                           ['distinguishedname']):
                    if ldap_instance.get_query('(&(sAMAccountName='+account+')(description='+user_id+'))',
                                               ['distinguishedname']):
                        verification_result = [1, 1]
                    else:
                        if ldap_instance.get_query('(description='+user_id+')',
                                                   ['distinguishedname']):
                            verification_result = [3]
                        else:
                            verification_result = [1, 0]
                else:
                    if ldap_instance.get_query('(description='+user_id+')',
                                               ['distinguishedname']):
                        verification_result = [0, 1]
                    else:
                        verification_result = [0, 0]
            else:
                verification_result.append(2)
        elif mode == 'gsuite' and directory_api_instance is not None:
            if len(directory_api_instance.get_query('email='+account)) > 0:
                if len(directory_api_instance.get_query('email='+account+' externalId='+user_id)) > 0:
                    verification_result = [1, 1]
                else:
                    if len(directory_api_instance.get_query('externalId='+user_id)) > 0:
                        verification_result = [3]
                    else:
                        verification_result = [1, 0]
            else:
                if len(directory_api_instance.get_query('externalId='+user_id)) > 0:
                    verification_result = [0, 1]
                else:
                    verification_result = [0, 0]
        else:
            verification_result.append(2)
        """Возможные результаты
        [0, 0] - Аккаунт и ИНН не найдены среди сущевствующих. Создаём новый аккаунт
        [1, 0] - Аккаунт найден, ИНН не найден. Однофамилец, выбираем другой шаблон аккаунта
        [1, 1] - Аккаунт и ИНН найден среди сущевствующих, Пропускаем
        [0, 1] - Аккаунт не найден, ИНН совпадает с существующим аккаунтом. Случай отбираем, для последующего разбора ситуации
        [2] - Не удалось сформировать имя аккаунта.
        [3] - Аккаунт и ИНН принадлежат двум разным людям. Случай отбираем, для последующего разбора ситуации
        """
        return verification_result

    def validation(self, name, inn, mode, domain, verification_mode, ldap_instance=None, directory_api_instance=None):
        option = 1
        while option <= 3:
            verification_result = self.account_verification(self.create_account(self.normalize(name),
                                                                                option,
                                                                                mode,
                                                                                domain),
                                                            inn,
                                                            verification_mode,
                                                            ldap_instance,
                                                            directory_api_instance)
            if verification_result == [0, 0]:
                break
            elif verification_result == [0, 1]:
                option = None
                break
            elif verification_result == [1, 1]:
                option = None
                break
            elif verification_result == [1, 0]:
                option += 1
                continue
            elif verification_result == [2]:
                option = None
                break
            elif verification_result == [3]:
                option = None
                break

        return option

    def get_request_add(self):
        return self.__request_add

    def get_request_update(self):
        return self.__request_update

    def get_request_suspend(self):
        return self.__request_suspend

    def get_request_add_supplier(self):
        return self.__request_add_supplier

    def get_request_del_supplier(self):
        return self.__request_del_supplier

    def get_request_batch_update(self):
        return self.__request_batch_update

    def get_files_import(self):
        return self.__json_files_import
