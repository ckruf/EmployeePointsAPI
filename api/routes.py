from api.employee import EmployeesApi

def create_routes(api):
    api.add_resource(EmployeesApi, '/employees/')

