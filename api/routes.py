from api.employee import emp_ns
from api.point import point_ns
from api.periodwinner import period_winner_ns
from api.application import applications_ns

def create_routes(api):
    #emp_ns = api.namespace('employees', description='Employee operations')
    #api.add_resource(EmployeesApi, '/employees/')
    api.add_namespace(emp_ns)
    api.add_namespace(point_ns)
    api.add_namespace(period_winner_ns)
    api.add_namespace(applications_ns)

