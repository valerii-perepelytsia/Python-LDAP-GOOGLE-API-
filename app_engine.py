"""test"""
from app_config_class import Config
from utils import create_directory, send_credentials, send_extra, export_results, set_ldap_password
from app_logger import create_logger, logger_level_change
from app_google_class import DirectoryAPI, DataTransferAPI, GmailAPI
from app_ldap_class import LdapService
from app_fs_class import Fs
from app_google_request_class import GoogleRequest
from app_ldap_request_class import LdapRequest
import argparse

if __name__ == '__main__':
    # --- BEGIN Create directories ---
    for directory_name in [['Back_up'], ['Import'], ['Export']]:
        create_directory(directory_name)
    # --- END ---
    # --- BEGIN Create logs ---
    LOGGER = create_logger('script_log_')
    logger_level_change('googleapiclient', 'error')
    # --- END ---
    try:
        # --- BEGIN Create config ---
        SCRIPT_CONFIG = Config(LOGGER)
        # --- END ---
    except Exception as error:
        LOGGER.error("app_engine.py config")
        LOGGER.error(error)
    else:
        try:
            # --- BEGIN Create request FS ---
            FS = Fs(SCRIPT_CONFIG)
            # --- END ---
        except Exception as error:
            LOGGER.error("app_engine.py Fs")
            LOGGER.error(error)
        else:
            # --- BEGIN Create instans GoogleAPI Directory ---
            try:
                DIRECTORY_API_INSTANCE = \
                    DirectoryAPI(SCRIPT_CONFIG.get_config()['CREDENTIALS']['service_account_file'],
                                 SCRIPT_CONFIG.get_config()['GOOGLEAPI']['google_api_directory_scopes'].split(','),
                                 SCRIPT_CONFIG.get_config()['CREDENTIALS']['credential_delegation_login'],
                                 SCRIPT_CONFIG.get_config()['GOOGLEAPI']['google_api_directory_service_name'],
                                 SCRIPT_CONFIG.get_config()['GOOGLEAPI']['google_api_directory_service_version'],
                                 LOGGER)
                # --- END ---
                # --- BEGIN Create instans GoogleAPI Datatransfer ---
                DATATRANSFER_API_INSTANCE = \
                    DataTransferAPI(SCRIPT_CONFIG.get_config()['CREDENTIALS']['service_account_file'],
                                    SCRIPT_CONFIG.get_config()['GOOGLEAPI']['google_api_datatransfer_scopes'].split(','),
                                    SCRIPT_CONFIG.get_config()['CREDENTIALS']['credential_delegation_login'],
                                    SCRIPT_CONFIG.get_config()['GOOGLEAPI']['google_api_datatransfer_service_name'],
                                    SCRIPT_CONFIG.get_config()['GOOGLEAPI']['google_api_datatransfer_service_version'],
                                    DIRECTORY_API_INSTANCE,
                                    SCRIPT_CONFIG.get_config(),
                                    LOGGER)
                # --- END ---
                # --- BEGIN Create instans GoogleAPI GMail ---
                GOOGLEAPI_GMAIL_INSTANCE = \
                    GmailAPI(SCRIPT_CONFIG.get_config()['CREDENTIALS']['service_account_file'],
                             SCRIPT_CONFIG.get_config()['GOOGLEAPI']['google_api_gmail_scopes'].split(','),
                             SCRIPT_CONFIG.get_config()['CREDENTIALS']['credential_delegation_login'],
                             SCRIPT_CONFIG.get_config()['GOOGLEAPI']['google_api_gmail_service_name'],
                             SCRIPT_CONFIG.get_config()['GOOGLEAPI']['google_api_gmail_service_version'],
                             LOGGER)
                # --- END ---
            except Exception as error:
                LOGGER.error("app_engine.py")
                LOGGER.error(error)
            else:
                # --- END ---
                try:
                    # --- BEGIN Create instans LDAP ---
                    LDAP_INSTANCES = dict()
                    for source in SCRIPT_CONFIG.get_config()["SOURCES"]:
                        if LdapService(SCRIPT_CONFIG, SCRIPT_CONFIG.get_config()["SOURCES"][source],
                                       LOGGER).status:
                            LDAP_INSTANCES[source] = \
                                LdapService(SCRIPT_CONFIG, SCRIPT_CONFIG.get_config()["SOURCES"][source], LOGGER)
                    # --- END ---
                except Exception as error:
                    LOGGER.error("app_engine.py ldap")
                    LOGGER.error(error)
                else:
                    argument_parser = argparse.ArgumentParser()
                    subparser = argument_parser.add_subparsers(dest='command')
                    batch_update = subparser.add_parser('batch-update')
                    set_password = subparser.add_parser('set-password')
                    test = subparser.add_parser('test')
                    app_engine = subparser.add_parser('start')
                    app_engine.add_argument('--send', type=str, choices=['bot', 'none'],
                                            default='bot')
                    app_engine.add_argument('--exclude', choices=['gmail', 'ldap', 'none'],
                                            default='none')
                    set_password.add_argument('--login', type=str, required=True)
                    set_password.add_argument('--password', type=str)
                    set_password.add_argument('--generate', type=int, nargs=3, default=[0, 0, 0])
                    set_password.add_argument('--source', type=str, required=True,
                                              choices=SCRIPT_CONFIG.get_config()['SOURCES'].keys())
                    set_password.add_argument('--mode', type=str, required=True, choices=['ldap', 'google'])
                    set_password.add_argument('--umcp', type=int, choices=[0, -1],
                                              default=-1)
                    set_password.add_argument('--send', type=str, choices=['bot', 'email', 'none'],
                                              default='none')

                    args = argument_parser.parse_args()
                    if args.command == 'batch-update':
                        pass
                        # DIRECTORY_API_INSTANCE.update_accounts(GOOGLE_REQUESTS.get_batch_update_requests())
                    elif args.command == 'set-password':
                        if args.mode == 'ldap':
                            set_ldap_password(LDAP_INSTANCES[args.source],
                                              GOOGLEAPI_GMAIL_INSTANCE,
                                              args,
                                              SCRIPT_CONFIG,
                                              LOGGER)
                        elif args.mode == 'google':
                            pass
                    elif args.command == 'test':
                        print("test")
                        SCRIPT_CONFIG.fetch_varus_bot_response()
                        SCRIPT_CONFIG.post_client_message("+380982986053", "test", "test")
                    elif args.command == 'start':
                        if args.exclude != 'gmail':
                            # --- BEGIN Create requests Google ---
                            GOOGLE_REQUESTS = GoogleRequest('/omega',
                                                            'organization',
                                                            SCRIPT_CONFIG,
                                                            DIRECTORY_API_INSTANCE,
                                                            DATATRANSFER_API_INSTANCE,
                                                            FS)
                            # --- END ---
                            # --- BEGIN Create accounts Google ---
                            DIRECTORY_API_INSTANCE.insert_accounts(GOOGLE_REQUESTS.get_insert_requests(),
                                                                   SCRIPT_CONFIG)
                            # --- END ---
                            # --- BEGIN Update accounts Google ---
                            DIRECTORY_API_INSTANCE.update_accounts(GOOGLE_REQUESTS.get_update_requests())
                            # --- END ---
                            # --- BEGIN  Clear membership Google ---
                            DIRECTORY_API_INSTANCE.remove_group_member(GOOGLE_REQUESTS.get_update_requests())
                            # --- END ---
                            # --- BEGIN update aliases Google ---
                            DIRECTORY_API_INSTANCE.insert_alias(GOOGLE_REQUESTS.get_alias_request())
                            # --- END ---
                            # --- BEGIN Create groups Google ---
                            DIRECTORY_API_INSTANCE.create_group(GOOGLE_REQUESTS.get_group_create_request())
                            # --- END ---
                            # --- BEGIN Add members to groups Google ---
                            DIRECTORY_API_INSTANCE.insert_group_member(GOOGLE_REQUESTS.get_group_member_requests())
                            # --- END ---
                            if len(GOOGLE_REQUESTS.get_suspend_requests()) > 0:
                                # --- BEGIN Suspend accounts Google ---
                                DIRECTORY_API_INSTANCE.update_accounts(GOOGLE_REQUESTS.get_suspend_requests())
                                # --- END ---
                                # --- BEGIN Transfer data and delete accounts Google ---
                                DATATRANSFER_API_INSTANCE.insert_transfers(DIRECTORY_API_INSTANCE.get_suspended_accounts())
                                DIRECTORY_API_INSTANCE.insert_group_member(GOOGLE_REQUESTS.get_group_member_fired_requests())
                                DIRECTORY_API_INSTANCE.delete_accounts(DATATRANSFER_API_INSTANCE.get_released_accounts())
                                # --- END ---
                        if args.exclude != 'ldap':
                            if len(LDAP_INSTANCES) > 0:
                                try:
                                    # --- BEGIN Create requests LDAP ---
                                    LDAP_REQUESTS = LdapRequest(LDAP_INSTANCES,
                                                                SCRIPT_CONFIG, FS)
                                    # --- END ---
                                except Exception as error:
                                    LOGGER.error("app_engine.py")
                                    LOGGER.error(error)
                                else:
                                    # --- BEGIN Download structures LDAP ---
                                    for ad_structure in LDAP_REQUESTS.get_ad_structures():
                                        if LDAP_INSTANCES.get(ad_structure["source"], None):
                                            LDAP_INSTANCES[ad_structure["source"]].insert_organizational_units(ad_structure)
                                    # --- END ---
                                    # --- BEGIN Add user LDAP ---
                                    for source in LDAP_REQUESTS.get_insert_requests():
                                        if LDAP_INSTANCES.get(source, None):
                                            LDAP_INSTANCES[source].insert_ldap_users(LDAP_REQUESTS.get_insert_requests()[source])
                                    # --- END ---
                                    # --- BEGIN Add suppliers LDAP ---
                                    for source in LDAP_REQUESTS.get_insert_supplier_requests():
                                        if LDAP_INSTANCES.get(source, None):
                                            LDAP_INSTANCES[source].insert_ldap_users(LDAP_REQUESTS.get_insert_supplier_requests()[source],
                                                                                     mode="supplier")
                                    # --- END ---
                                    # --- BEGIN Add members to groups LDAP ---
                                    for source in LDAP_REQUESTS.get_membership_requests():
                                        if LDAP_INSTANCES.get(source, None):
                                            LDAP_INSTANCES[source].insert_members_to_group(LDAP_REQUESTS.get_membership_requests()[source])
                                    # --- END ---
                                    # --- BEGIN Update users LDAP ---
                                    for source in LDAP_REQUESTS.get_update_requests():
                                        if LDAP_INSTANCES.get(source, None):
                                            LDAP_INSTANCES[source].update_ldap_users(LDAP_REQUESTS.get_update_requests()[source])
                                    # --- END ---
                                    # --- BEGIN Suspend users LDAP ---
                                    for source in LDAP_REQUESTS.get_suspend_requests():
                                        if LDAP_INSTANCES.get(source, None):
                                            LDAP_INSTANCES[source].suspend_ldap_users(LDAP_REQUESTS.get_suspend_requests()[source])
                                    # --- END ---
                                    # --- BEGIN Suspend suppliers LDAP ---
                                    for source in LDAP_REQUESTS.get_suspend_supplier_requests():
                                        if LDAP_INSTANCES.get(source, None):
                                            LDAP_INSTANCES[source].suspend_ldap_supplier(LDAP_REQUESTS.get_suspend_supplier_requests()[source])
                                    # --- END ---
                        # --- BEGIN Send accounts ---
                        if args.send == 'bot':
                            send_credentials(SCRIPT_CONFIG)
                        # --- END ---
                        # --- BEGIN Send extras ---
                        send_extra(GOOGLEAPI_GMAIL_INSTANCE, SCRIPT_CONFIG)
                        # --- END ---
                        # --- BEGIN Export results to 1С ---
                        export_results(SCRIPT_CONFIG, FS, DIRECTORY_API_INSTANCE)
                        # --- END ---
