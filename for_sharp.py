import urllib3
import sys
from authorization import Authorization
from employee import Employee
from erp_organization import Organization
from workspace import Workspace
from dbconnect import DBConnect
urllib3.disable_warnings()

env = sys.argv[1]
space_name = sys.argv[2]
email = sys.argv[3]

new_space = Workspace(env)
new_space_admin = Employee(env)
db = DBConnect(env)

space_guid = new_space.create_workspace(space_name=space_name, space_code=space_name)
new_space_admin.create_admin_for_new_space(space_guid, email)

auth = Authorization(env)
headers = auth.create_headers(email)
new_organization_guid = Organization(env, headers).add_organization('Owner')
new_space.set_space_owner(new_organization_guid)

new_space_admin.add_admin_to_employees(new_organization_guid, headers)
print(space_guid, space_name, email)
