from flask import jsonify
from flask_restx import Resource, Namespace, reqparse, fields, marshal_with, abort
from models.employees import Employees

emp_ns = Namespace('employees', description='Employee operations')

employee_post_args = reqparse.RequestParser()
employee_post_args.add_argument("name", type=str, help="Provide name of employee", required=True)
employee_post_args.add_argument("active", type=bool, help="Provide boolean for whether employee is active", required=True)

employee_put_args = reqparse.RequestParser()
employee_put_args.add_argument("name", type=str, help="Provide name of employee to deactivate", required=True)

employee_fields = emp_ns.model('Employee',{
    'name':fields.String,
    'active':fields.Boolean
})

@emp_ns.route('/add')
class AddEmployees(Resource):
    @emp_ns.marshal_with(employee_fields, code=201)
    @emp_ns.expect(employee_post_args)
    @emp_ns.doc('add employees')
    def post(self):
        '''Add an employee'''
        args = employee_post_args.parse_args()
        employee = Employees(name=args['name'], active=args['active'])
        employee.save()
        return employee, 201

@emp_ns.route('/all')
class AllEmployees(Resource):
    @emp_ns.marshal_list_with(employee_fields, code=200)
    @emp_ns.doc('view all employees')
    def get(self):
        '''Get all employees'''
        allemployees = []
        for employee in Employees.objects():
            allemployees.append(employee)
        return allemployees, 200

@emp_ns.route('/deactivate')
class DeactivateEmployee(Resource):
    @emp_ns.marshal_with(employee_fields, code=200)
    @emp_ns.doc('deactivate employee')
    @emp_ns.expect(employee_put_args)
    def put(self):
        '''Deactivate an employee (if they have left the company for example)'''
        args = employee_put_args.parse_args()
        try:
            deactivated_employee = Employees.objects(name=args['name']).get()
        except Employees.DoesNotExist:
            abort(404, message="Could not find employee with that name")
        deactivated_employee.active = False
        deactivated_employee.save()
        return deactivated_employee, 200