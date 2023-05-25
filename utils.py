"""test"""
from fnmatch import filter as fnmfilter
from re import findall
from time import strftime
from os import path, getcwd, makedirs, remove, listdir
from shutil import copy
from json import dump
from app_auxiliary import generate_password
import requests


def create_directory(directory_to_create, datestamp=False):
    """test"""
    if not datestamp:
        if not path.exists(path.join(getcwd(), *directory_to_create)):
            makedirs(path.join(getcwd(), *directory_to_create))
            directory_path = path.join(getcwd(), *directory_to_create)
        else:
            directory_path = path.join(getcwd(), *directory_to_create)
    else:
        if not path.exists(path.join(getcwd(),
                                     *directory_to_create) + strftime('%d-%m-%Y')):
            makedirs(path.join(getcwd(), *directory_to_create) + strftime('%d-%m-%Y'))
            directory_path = path.join(getcwd(), *directory_to_create) + strftime('%d-%m-%Y')
        else:
            directory_path = path.join(getcwd(), *directory_to_create) + strftime('%d-%m-%Y')

    return directory_path


def create_file(file_to_create):
    """test"""
    if not path.exists(path.join(getcwd(), *file_to_create)):
        open(path.join(getcwd(), *file_to_create), 'a').close()


def move_files(move_to_directory, files_mask, source_directory="", copy_mode=True):
    """test"""
    for path_to_file in \
            [path.join(source_directory, p) for p in fnmfilter(listdir(path.join(getcwd(), source_directory)),
                                                               files_mask)]:
        if copy_mode:
            copy(path_to_file, move_to_directory)
            remove(path_to_file)
        else:
            remove(path_to_file)


def merge_dictionary(dict_1, dict_2):
    dict_3 = {**dict_1, **dict_2}
    for key, value in dict_3.items():
        if key in dict_1 and key in dict_2:
            if key == 'operation' or key == 'source':
                pass
            else:
                dict_3[key] = value + dict_1[key]
    return dict_3


def send_credentials(config):
    if isinstance(config.fetch_varus_bot_response(), requests.models.Response):
        if len(config.get_result()) > 0:
            for uuid in config.get_result():
                if 'primaryEmail' in config.get_result()[uuid] \
                        and 'ldapLogin' in config.get_result()[uuid]:
                    message = "xx " \
                              "xx" \
                              "xx " + \
                              config.get_result()[uuid]['ldapLogin'] + \
                              "xx " + \
                              config.get_result()[uuid]['ldapPassword'] + \
                              "xx " + \
                              config.get_result()[uuid]['primaryEmail'] + \
                              "xx " + config.get_result()[uuid]['emailPassword'] + \
                              "xx" \
                              "xx" \
                              "xx"
                    config.post_client_message(config.get_result()[uuid]['mobile'], message, message)
                elif 'primaryEmail' in config.get_result()[uuid] \
                        and 'ldapLogin' not in config.get_result()[uuid]:
                    message = "xx" \
                              "xx" \
                              "xx" + \
                              config.get_result()[uuid]['primaryEmail'] + \
                              "xx " + config.get_result()[uuid]['emailPassword'] + \
                              "xx" \
                              "xx" \
                              "xx"
                    config.post_client_message(config.get_result()[uuid]['mobile'], message, message)
                elif 'primaryEmail' not in config.get_result()[uuid] \
                        and 'ldapLogin' in config.get_result()[uuid]:
                    message = "xx" \
                              "xx" \
                              "xx" + \
                              config.get_result()[uuid]['ldapLogin'] + \
                              "xx" + \
                              config.get_result()[uuid]['ldapPassword'] + \
                              "xx" \
                              "xx" \
                              "xx"
                    config.post_client_message(config.get_result()[uuid]['mobile'], message, message)


def extra(values, config):
    result = None
    for value in values:
        for condition in config.get_extra():
            if findall(condition[1], value):
                result = condition[0]
                break
    return result


def send_extra(gmail_instance, config):
    email_list = list()
    if len(config.get_result()) > 0:
        for uuid in config.get_result():
            if 'extra' in config.get_result()[uuid]:
                email_list.append(config.get_result()[uuid]['primaryEmail'])
        if len(email_list):
            gmail_instance.send_client_message('me',
                                               config.get_config()['CREDENTIALS']['greetings_account'],
                                               ", ".join(email_list),
                                               config.get_config()['CREDENTIALS']['greetings_subject'],
                                               config.get_html_templates()[0][1])


def export_results(config, fs, directory_api_instance):
    if len(config.get_result()) > 0:
        for index, uuid in enumerate(config.get_result()):
            if 'primaryEmail' in config.get_result()[uuid]:
                with open(path.join(getcwd(), 'Export', "gsuit_email_" + uuid + ".json"), 'w') as jsonExportFile:
                    dump({"email": config.get_result()[uuid]["primaryEmail"],
                          "inn": config.get_result()[uuid]["externalId"]}, jsonExportFile)
    else:
        for division in fs.get_request_add():
            for index, inn in enumerate(fs.get_request_add()[division]['inn']):
                if directory_api_instance.get_query(f'externalId={inn}').get('primaryEmail', None) is not None:
                    with open(path.join(getcwd(),
                                        'Export',
                                        "gsuit_email_"
                                        + fs.get_request_add()[division]['uuid'][index]
                                        + ".json"), 'w') as jsonExportFile:
                        dump({"email": directory_api_instance.get_query(f'externalId={inn}')['primaryEmail'],
                              "inn": inn}, jsonExportFile)


def set_ldap_password(ldap_instance, gmail_instance, args, config, logger):
    message = ""
    result = False
    if args.password is None and args.generate == [0, 0, 0]:
        result = ldap_instance.set_password(ldap_instance.get_query('(sAMAccountName={0})'.format(args.login),
                                                                    'distinguishedName'),
                                            config.get_config()[args.source.upper()]['ldap_default_password'],
                                            args.umcp)
        message = "xx " + ldap_instance.get_query('(sAMAccountName={0})'.format(args.login),
                                                            'displayname') + \
                  "xx" + \
                  "xx " + args.login + \
                  "xx " + config.get_config()[args.source.upper()]['ldap_default_password'] + \
                  "xx " \
                  "xx " \
                  "xx"
    elif (args.password is not None and args.generate == [0, 0, 0]) and \
            (args.password is not None and args.generate != [0, 0, 0]):
        result = ldap_instance.set_password(ldap_instance.get_query('(sAMAccountName={0})'.format(args.login),
                                                                    'distinguishedName'),
                                            args.password,
                                            args.umcp)
        message = "Шановний(на) " + ldap_instance.get_query('(sAMAccountName={0})'.format(args.login),
                                                            'displayname') + \
                  "xx" + \
                  "xx " + args.login + \
                  "xx " + args.password + \
                  "xx " \
                  "xx " \
                  "xx"
    elif args.password is None and args.generate != [0, 0, 0]:
        generated_password = generate_password(args.generate[0], args.generate[1], args.generate[2])
        result = ldap_instance.set_password(ldap_instance.get_query('(sAMAccountName={0})'.format(args.login),
                                                                    'distinguishedName'),
                                            generated_password,
                                            args.umcp)
        message = "xx " + ldap_instance.get_query('(sAMAccountName={0})'.format(args.login),
                                                            'displayname') + \
                  "xx" + \
                  "xx " + args.login + \
                  "xx " + generated_password + \
                  "xx " \
                  "xx " \
                  "xx"
    if result:
        if args.send == 'bot':
            config.post_client_message(ldap_instance.get_query('(sAMAccountName={0})'.format(args.login),
                                                               'mobile'),
                                       message,
                                       message)
        elif args.send == 'email':
            gmail_instance.send_client_message('me',
                                               config.get_config()['CREDENTIALS']['greetings_account'],
                                               ldap_instance.get_query('(sAMAccountName={0})'.format(args.login),
                                                                       'mail'),
                                               "xx",
                                               message,
                                               logger)
