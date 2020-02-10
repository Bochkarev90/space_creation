import requests
from helpers import base_url_from_env


class Organization:
    def __init__(self, env, headers):
        self._base_url = base_url_from_env(env)
        self._headers = headers
        self._spaceGuid = headers['SpaceGuid']

    def add_organization(self, organization_title):
        url = self._base_url + 'ctms/api/v1/organizations/create'
        data = {
            'statusGuid': '655aa6f2-434a-4b8d-8254-722d160e611e',  # Active
            'categoryGuid': 'b6b010d3-2a9b-4e93-8db8-01cd6056b713',  # CRO
            'countryGuid': '2876aae7-b8f5-4a35-bf61-9ad69f12ccc0',  # Russia
            'spaceGuid': self._spaceGuid,
            'name': organization_title,
            'addresses': [],
            'createdByGuid': '1d99e18d-a366-4b91-956e-1388463ba09f'
        }
        response = requests.post(url, headers=self._headers, json=data, verify=False)
        if response.status_code != 200:
            print(response.status_code, response.text)
            raise Exception('Не удалось создать организацию')
        else:
            organization_guid = response.json()['GuidCode']
        return organization_guid


if __name__ == '__main__':
    from authorization import Authorization
    headers_for_test = Authorization('test').create_headers('space_for_test@dm-matrix.com', 'somepwd')
    new_organization_guid = Organization('test', headers_for_test).add_organization('test_4111')
    print(new_organization_guid)
