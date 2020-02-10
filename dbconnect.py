import psycopg2
from config import DB_PASSWORD, DB_USER


class DBConnect:
    def __init__(self, env):
        if env == 'test':
            host = 'dmdockertest1.dm.dm-matrix.com'
        elif env == 'dev':
            host = 'dmdockerdev.dm.dm-matrix.com'
        elif env == 'demo':
            host = '10.5.10.15'
        elif env == 'prod':
            host = '10.5.10.20'
        else:
            raise Exception('Не выбрана среда для подключения к базе')
        self.conn = psycopg2.connect(user=DB_USER, database='dmx-crf',
                                     password=DB_PASSWORD, host=host, port='35474')
        self.cursor = self.conn.cursor()

    def execute(self, command):
        self.cursor.execute(command)
        return self.cursor

    def space_codes_on_server(self):
        with self.conn, self.conn.cursor() as cursor:
            cursor.execute("SELECT space_code FROM sh_ctms.cw_space")
            spaces = cursor.fetchall()
        return [space[0].lower() for space in spaces]


if __name__ == '__main__':
    print(DBConnect('test').space_codes_on_server())
    print(DBConnect('dev').space_codes_on_server())
    print(DBConnect('demo').space_codes_on_server())
    print(DBConnect('prod').space_codes_on_server())
    print(DBConnect('dev').execute("SELECT space_code FROM sh_ctms.cw_space").fetchall())
    print(DBConnect('test').execute("SELECT space_code FROM sh_ctms.cw_space").fetchall())
    print(DBConnect('demo').execute("SELECT space_code FROM sh_ctms.cw_space").fetchall())
    print(DBConnect('prod').execute("SELECT space_code FROM sh_ctms.cw_space").fetchall())
