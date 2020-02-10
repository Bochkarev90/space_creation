from dbconnect import DBConnect
import requests
from helpers import base_url_from_env
from default_values import DEFAULT_ADMIN_FIRST_NAME, DEFAULT_ADMIN_LAST_NAME, DEFAULT_ADMIN_JOB_TITLE_AND_DEPARTMENT


class Employee:
    def __init__(self, env):
        self._base_url = base_url_from_env(env)
        self._first_name = ''
        self._last_name = ''
        self._job_title = ''
        self._email = ''
        self._password = ''
        self._space_guid = ''
        self._organization_guid = ''
        self._role = ''
        self._person_guid = ''
        self._employee_guid = ''
        self._user_guid = ''
        self._invite_code_guid = ''
        self._headers = {}
        self._dbconn = DBConnect(env)
        self._is_admin = False

    def login_exists(self, email):
        with self._dbconn.conn, self._dbconn.conn.cursor() as cursor:
            cursor.execute(
                "SELECT sh_auth.func_check_login_uniq('%s');" % email
            )
            return False if cursor.fetchone()[0] else True

    def _send_invite_api(self):
        url = self._base_url + 'registration/api/v1/invite/new-user'
        headers = {
            'SpaceGuid': self._space_guid
        }
        data = {
            'userGuid': self._person_guid if self._person_guid else None,
            "sender": "sender",
            "payload": {
                "target": self._email,
                "reason": "reason",
            }
        }
        response = requests.post(url, json=data, verify=False, headers=headers)
        if response.status_code != 201:
            raise Exception(f'Не удалось отправить инвайт. Ошмибка {response.status_code} \n {response.text}')
        self._inviteCodeGuid = response.json()['payload']['inviteCode']

        if not self._person_guid:
            with self._dbconn.conn, self._dbconn.conn.cursor() as cursor:
                cursor.execute(
                    "SELECT user_guid FROM sh_auth.invites WHERE code = '%s';" % self._inviteCodeGuid
                )
                self._user_guid = cursor.fetchone()[0]

    def _accept_invite_api(self):
        url = self._base_url + 'registration/api/v1/invite/acceptance'
        data = {
            'sender': 'sender',
            'payload': {
                'inviteCode': self._inviteCodeGuid
            }
        }
        requests.post(url, json=data, verify=False)

    def _set_password_api(self):
        url = self._base_url + 'registration/api/v1/password'
        data = {
            "sender": "sender",
            "payload": {
                "inviteCode": self._inviteCodeGuid,
                "password": self._password,
                "acceptPersonalDataProcessing": True
            }
        }
        requests.post(url, json=data, verify=False)

    def _create_person_api(self):
        url = self._base_url + 'persons/odata/persons'
        data = {
            "BirthDate": "1990-06-15T06:02:00Z",
            "FirstName": self._first_name,
            "LastName": self._last_name,
            "UserGuid": self._user_guid,
            "SpaceGuid": self._space_guid,
            "Sender": "Sender"
        }
        response = requests.post(url, json=data, verify=False)
        self._person_guid = response.json()['GuidCode']

    def _set_erp_role_api(self, role):
        with self._dbconn.conn, self._dbconn.conn.cursor() as cursor:
            cursor.execute(
                "SELECT dict_type_common_value_guid FROM sh_dict.dict_type_common_value "
                f"WHERE dict_type_guid = 'c550d90f-626c-4fda-810b-df000f7c690d' AND value_name = '{role}';"
            )
            role_guid = cursor.fetchone()[0]

        url = self._base_url + 'registration/api/v1/UserRole'
        headers = {
            'SpaceGuid': self._space_guid
        }
        data = {
            "sender": "sender",
            "payload": {
                "personGuid": self._person_guid,
                "userGuid": self._user_guid,
                "roleGuid": role_guid,
                'spaceGuid': self._space_guid,
                'dateFrom': '2019-07-13T15:39:16.511Z',
                "userRoleStatus": "9514a57b-57de-4c2a-ac49-035bf0f1957e",
            }
        }
        requests.post(url, json=data, headers=headers, verify=False)

        with self._dbconn.conn, self._dbconn.conn.cursor() as cursor:
            cursor.execute(
                "UPDATE sh_auth.user_role "
                "SET status = '9514a57b-57de-4c2a-ac49-035bf0f1957e' "
                f"WHERE person_guid = '{self._person_guid}';"
            )

    def _create_employee_api(self):
        url = self._base_url + 'ctms/api/v1/employees'
        data = {
            "organizationGuid": self._organization_guid,
            "corporateWorkspaceGuid": self._space_guid,
            "firstName": self._first_name,
            "lastName": self._last_name,
            "department": self._job_title or "QA",
            "jobTitle": self._job_title or "QA",
            "email": self._email,
            "personGuid": self._person_guid if self._is_admin else None,
        }
        response = requests.post(url, headers=self._headers, json=data, verify=False)
        if response.status_code != 201:
            raise Exception(f'Не удалось создать сотрудника. Ошибка {response.status_code}')
        response = response.json()
        self._person_guid = response['Data']['PersonGuid']
        self._employee_guid = response['Data']['GuidCode']

    def create_admin_for_new_space(self, space_guid, email, password='Somepwd123'):
        self._space_guid = space_guid
        self._email = email
        self._password = password
        self._first_name = DEFAULT_ADMIN_FIRST_NAME
        self._last_name = DEFAULT_ADMIN_LAST_NAME
        self._job_title = DEFAULT_ADMIN_JOB_TITLE_AND_DEPARTMENT

        self._send_invite_api()
        self._accept_invite_api()
        self._set_password_api()
        self._create_person_api()
        self._set_erp_role_api('SpaceOwner')
        self._set_erp_role_api('ProjectManager')
        self._set_erp_role_api('Investigator')
        self._set_erp_role_api('CrfReviewer')

    def add_admin_to_employees(self, organization_guid, headers):
        self._is_admin = True
        self._organization_guid = organization_guid
        self._headers = headers
        self._create_employee_api()


if __name__ == '__main__':
    Employee('dev').create_admin_for_new_space('49228f5c-b03e-4a50-b89b-087cf2e2c667', '1142р322d35@wrt.qwe')
