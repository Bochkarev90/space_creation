import urllib3
from default_values import DEFAULT_ADMIN_PASSWORD, DEFAULT_FIRST_ORGANIZATION_TITLE

from authorization import Authorization
from employee import Employee
from erp_organization import Organization
from workspace import Workspace
from dbconnect import DBConnect

urllib3.disable_warnings()

while True:
    env = input("Введите среду (test/dev/demo/prod): ").lower()
    if env not in ['test', 'dev', 'demo', 'prod']:
        continue
    break

new_space = Workspace(env)
new_space_admin = Employee(env)
db = DBConnect(env)

while True:
    space_name = input("Введите Имя Спейса (должно быть уникальным): ")
    if space_name.lower() in db.space_codes_on_server():
        print("Пространство с таким именем уже сущестует. Введите другое имя")
        continue
    break

while True:
    email = input("Введите валидный email (логин должен быть уникальным в рамках всех спейсов): ")
    if new_space_admin.login_exists(email):
        print("Логин занят")
        continue
    break

space_guid = new_space.create_workspace(space_name=space_name, space_code=space_name)
new_space_admin.create_admin_for_new_space(space_guid, email, DEFAULT_ADMIN_PASSWORD)
print(f"\n\nСпейс {space_name} создан. Логин - {email}, Пароль - {DEFAULT_ADMIN_PASSWORD}")

auth = Authorization(env)
headers = auth.create_headers(email, password=DEFAULT_ADMIN_PASSWORD)

new_organization_guid = Organization(env, headers).add_organization(DEFAULT_FIRST_ORGANIZATION_TITLE)
print(f"В спейсе с Guid-кодом - {space_guid} создана организация {DEFAULT_FIRST_ORGANIZATION_TITLE}")
new_space.set_space_owner(new_organization_guid)

new_space_admin.add_admin_to_employees(new_organization_guid, headers)

input("Press any key to exit")
