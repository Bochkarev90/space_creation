import requests
from helpers import base_url_from_env


class AuthorizationError(Exception):
    def __init__(self, text):
        self.txt = text


class Authorization:
    def __init__(self, env):
        self._base_url = base_url_from_env(env)
        self._login = ''
        self._password = ''
        self._access_token = ''
        self._refresh_token = ''
        self._space_guid = ''
        self._headers = None
        self._projects_in_space = {}

    def _get_token_api(self):
        url = self._base_url + 'identity/api/token/connect'
        data = {
            'username': self._login,
            'password': self._password
        }
        response = requests.post(url=url, json=data, verify=False)
        if response.status_code != 200:
            raise AuthorizationError('Не удалось авторизоваться')
        response = response.json()
        self._access_token = 'Bearer ' + response['access_token']
        self._refresh_token = response['refresh_token']

    def _session_info_api(self):
        url = self._base_url + 'identity/api/SessionInfo'
        headers = {
            'Authorization': self._access_token
        }
        response = requests.post(url=url, headers=headers, verify=False).json()
        for project in response:
            self._projects_in_space[project['ProjectName']] = project['ProjectGuidCode']
            # print(project['ProjectName'], project['ProjectGuidCode'])
        self._space_guid = response[0]['SpaceGuidCode']

    def create_headers(self, login, password='Somepwd123'):
        """
        Принимает на вход логин и пароль, возвращает словарь с элементами:
        ['Authorization']: - access_token в формате 'Bearer eyJhbG...'
        ['RefreshToken']: - refresh_token
        ['SpaceGuid']: - Guid пространства, в который был осуществлен вход
        Можно передавать словарем в последующие api запросы
        """
        self._login = login
        self._password = password
        self._get_token_api()
        self._session_info_api()
        self._headers = {
            'Authorization': self._access_token,
            'RefreshToken': self._refresh_token,
            'SpaceGuid': self._space_guid
        }
        return self._headers

    def add_project_guid_to_headers(self, project_guid='', project_code=''):
        project_guid = project_guid or self._projects_in_space[project_code] or \
                       print("Нужно передавать либо код, либо Guid проекта")
        self._headers['ProjectGuid'] = project_guid
        return self._headers


if __name__ == '__main__':
    auth = Authorization('test')
    auth_info = auth.create_headers('space_for_test@dm-matrix.com', 'somepwd')
    print(auth_info['Authorization'])
    print(auth_info['RefreshToken'])
    print(auth_info['SpaceGuid'])

    auth = Authorization('dev')
    auth_info = auth.create_headers('testtwo@dm-matrix.com', 'somepwd')
    print(auth_info['Authorization'])
    print(auth_info['RefreshToken'])
    print(auth_info['SpaceGuid'])

    auth = Authorization('demo')
    auth_info = auth.create_headers('bigdemoboss@testing.dm-matrix.com', 'Somepwd123')
    print(auth_info['Authorization'])
    print(auth_info['RefreshToken'])
    print(auth_info['SpaceGuid'])

    auth = Authorization('prod')
    auth_info = auth.create_headers('testtwo@dm-matrix.com', 'Somepwd123')
    print(auth_info['Authorization'])
    print(auth_info['RefreshToken'])
    print(auth_info['SpaceGuid'])
