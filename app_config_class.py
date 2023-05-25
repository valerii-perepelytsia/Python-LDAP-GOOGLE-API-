from utils import create_directory
from configparser import ConfigParser
from sqlite3 import connect
from psycopg2 import connect as pg_connect, DatabaseError as pg_DatabaseError
from requests import post, exceptions
from ast import literal_eval


class Config:
    """test"""
    def __init__(self, logger):
        create_directory(['config.ini'])
        self.__script_config = ConfigParser()
        self.__script_config.read('config.ini', encoding='utf-8')
        self.__result_data = dict()
        self.__logger = logger
        self.__condition_groups = dict()
        self.__utils = connect("utils.db").cursor()
        self.__fetch_condition_groups()
        self.__alias_rules = self.__utils.execute("SELECT * FROM alias_rules").fetchall()
        self.__dynamic_groups = self.__utils.execute("SELECT * FROM dynamic_groups").fetchall()
        self.__extra = self.__utils.execute("SELECT * FROM extra").fetchall()
        self.__html_templates = self.__utils.execute("SELECT * FROM html_templates").fetchall()
        self.__filter = self.__utils.execute("SELECT * FROM filter").fetchall()
        self.__gsuite_filter = self.__utils.execute("SELECT * FROM gsuite_filter").fetchall()
        self.__location = self.__utils.execute("SELECT * FROM location_rules").fetchall()
        self.__logon = self.__utils.execute("SELECT * FROM logon_rules").fetchall()
        self.__pg_connect = pg_connect(dbname=self.__script_config["DB-CREDENTIALS"]["pg_suppliers_dbname"],
                                       user=self.__script_config["DB-CREDENTIALS"]["pg_suppliers_user"],
                                       password=self.__script_config["DB-CREDENTIALS"]["pg_suppliers_password"],
                                       host=self.__script_config["DB-CREDENTIALS"]["pg_suppliers_host"])
        self.__pg_cursor = self.__pg_connect.cursor()
        self.__varus_bot_response = dict()
        # self.__fetch_varus_bot_response()

    def __fetch_condition_groups(self):
        """test"""
        groups_list = list()
        conditions = self.__utils.execute("SELECT * FROM condition_groups").fetchall()
        for group in self.__utils.execute("SELECT DISTINCT group_name FROM condition_groups"):
            groups_list.append(group[0])
        for group in groups_list:
            self.__condition_groups[group] = list()
            for condition in conditions:
                if condition[0] == group:
                    self.__condition_groups[group].append(condition[1])

    def fetch_varus_bot_response(self):
        """test"""
        try:
            self.__varus_bot_response = post(self.__script_config["VARUS-BOT"]["url-token"],
                                             headers=literal_eval(self.__script_config["VARUS-BOT"]["url-token-headers"]),
                                             data=literal_eval(self.__script_config["VARUS-BOT"]["url-token-data"]))
        except exceptions.RequestException as exception:
            self.__logger.error("app_config_class.py")
            self.__logger.error(exception)

        return self.__varus_bot_response

    def post_client_message(self, phone, viber_text, sms_text):
        """test"""
        if self.__varus_bot_response.ok:
            try:
                post_request = post(self.__script_config["VARUS-BOT"]["url-client-message"],
                                    headers={'Content-Type': 'application/json',
                                             'Authorization': 'Bearer ' +
                                                              self.__varus_bot_response.json()['access_token']},
                                    json={"phone": phone,
                                          "viberText": viber_text,
                                          "smsText": sms_text,
                                          "imgUrl": "null"})
            except exceptions.RequestException as exception:
                self.__logger.error("app_config_class.py")
                self.__logger.error(exception)
            else:
                self.__logger.info(str(post_request.status_code) +
                                   " send message from varus-bot to "
                                   + str(phone))

    def get_config(self):
        return self.__script_config

    def insert_result(self, uuid, key, value):
        if self.__result_data.get(uuid, None) is not None:
            self.__result_data[uuid][key] = value
        else:
            self.__result_data[uuid] = dict()
            self.__result_data[uuid][key] = value

    def pg_insert_suppliers(self, supplier_name, password, inn, phone):
        sql_create_table_suppliers = "CREATE TABLE IF NOT EXISTS suppliers (" \
                                     "supplier_id SERIAL PRIMARY KEY, " \
                                     "supplier_name VARCHAR(255) NOT NULL, " \
                                     "supplier_password VARCHAR(255) NOT NULL, " \
                                     "bic VARCHAR(255) NOT NULL, " \
                                     "phone VARCHAR(255) NOT NULL, " \
                                     "creation_timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP)"
        self.__pg_cursor.execute(sql_create_table_suppliers)
        try:
            self.__pg_cursor.execute('INSERT INTO suppliers(supplier_name, supplier_password, bic, phone) '
                                     'VALUES (%s, %s, %s, %s)', (supplier_name, password, inn, phone))
            self.__pg_cursor.close()
        except (Exception, pg_DatabaseError) as Error:
            self.__logger.error(Error)
        else:
            self.__pg_connect.commit()
            self.__pg_connect.close()

    def get_result(self):
        return self.__result_data

    def get_condition_groups(self):
        return self.__condition_groups

    def get_dynamic_groups(self):
        return self.__dynamic_groups

    def get_alias_rules(self):
        return self.__alias_rules

    def get_extra(self):
        return self.__extra

    def get_html_templates(self):
        return self.__html_templates

    def get_filter(self):
        return self.__filter

    def get_gsuite_filter(self):
        return self.__gsuite_filter

    def get_varus_bot_response(self):
        return self.__varus_bot_response

    def get_greetings_template(self):
        return self.__utils.execute("SELECT * FROM html_templates where use='greetings'").fetchall()
