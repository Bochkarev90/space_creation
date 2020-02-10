from dbconnect import DBConnect
import requests


class WorkspaceError(Exception):
    def __init__(self, text):
        self.txt = text


class Workspace:
    def __init__(self, env):
        self._space_code = ''
        self._space_name = ''
        self._space_guid = ''
        self._domain = ''
        self._dbconn = DBConnect(env)

    def _create_space_db(self):
        """
        Создает строку в БД sh_ctms.cw_space
        Возвращает GUID созданного пространства
        """
        with self._dbconn.conn, self._dbconn.conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO sh_ctms.cw_space "
                "(space_code, space_name, created_by, status_guid) "
                "VALUES "
                f"('{self._space_code}', '{self._space_name}', "
                "'03a5ba28-18ec-471d-abf6-5c210a7c82ba', "
                "'13f00584-fc02-4b13-9904-ea4b62de842f') "
                "RETURNING space_guid;"
            )
            self._space_guid = cursor.fetchone()[0]

    def _domain_create_api(self):
        """
        Создает authforze domain, используя ранее созданный GUID пространства
        """
        url = 'http://dmdockerdev.dm.dm-matrix.com:35464/api/v1.0/domain'
        data = {
            'description': 'TestDescription',
            'externalId': self._space_guid
        }
        response = requests.post(url=url, json=data, verify=False)
        self._domain = str(response.text)

    def _set_domain(self):
        """
        Присваивает полученный ранее домен ранее созданному пространству
        """
        with self._dbconn.conn, self._dbconn.conn.cursor() as cursor:
            cursor.execute(
                "UPDATE sh_ctms.cw_space "
                f"SET authzforce_domain_id = '{self._domain}' "
                f"WHERE space_guid = '{self._space_guid}';"
            )

    def create_workspace(self, space_code, space_name):
        """
        Принимает на вход значения:
            space_code - Код пространства
            space_name - Имя пространства
        Создает запись о пространстве в БД
        Возвращает GUID созданного спейса
        """
        self._space_code = space_code
        self._space_name = space_name

        self._create_space_db()
        self._domain_create_api()
        self._set_domain()
        return self._space_guid

    def set_space_owner(self, organization_guid):
        """
        Принимает на вход Guid Организации-владельца пространства и устанавливает ее Владельцем Пространства
        """
        with self._dbconn.conn, self._dbconn.conn.cursor() as cursor:
            cursor.execute(
                "UPDATE sh_ctms.cw_space "
                f"SET owner = '{organization_guid}' "
                f"WHERE space_guid = '{self._space_guid}';"
            )

    def space_created(self):
        """
        Только для тестирования класса
        """
        with self._dbconn.conn, self._dbconn.conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM sh_ctms.cw_space "                
                "WHERE space_guid = '%s' AND authzforce_domain_id = '%s';" % (self._space_guid, self._domain)
            )
            return cursor.fetchone()

    def delete_space(self):
        """
        Только для тестирования класса
        """
        with self._dbconn.conn, self._dbconn.conn.cursor() as cursor:
            cursor.execute(
                "DELETE FROM sh_ctms.cw_space "                
                "WHERE space_guid = '%s' AND authzforce_domain_id = '%s';" % (self._space_guid, self._domain)
            )


if __name__ == '__main__':
    # new_space_on_test = Workspace('test')
    # new_space_on_test.create_workspace()
    # assert new_space_on_test.space_created()
    # new_space_on_test.delete_space()

    new_space_on_dev = Workspace('dev')
    new_space_on_dev.create_workspace('saasdsskopd', 'asdka')
    assert new_space_on_dev.space_created()
    # new_space_on_dev.delete_space()

    # new_space_on_demo = Workspace('demo')
    # new_space_on_demo.create_workspace()
    # assert new_space_on_demo.space_created()
    # new_space_on_demo.delete_space()
