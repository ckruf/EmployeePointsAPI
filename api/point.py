from flask import jsonify
from flask_restx import Resource, Namespace, reqparse, fields, marshal_with, inputs, abort
from models.points import Points
from models.employees import Employees
from models.applications import Applications
from models.periodwinners import PeriodWinners
import datetime

point_ns = Namespace('points', description='Operations with points')

point_post_args = reqparse.RequestParser()
point_post_args.add_argument("date_earned", type=inputs.datetime_from_iso8601, help="Provide a date when the point was earned in the format 'YYYY-MM-DD'", required=True)
point_post_args.add_argument("description", type=str, help="Provide a desription for what the point was awarded for", required=True)
point_post_args.add_argument("prod_env", type=bool, help="Provide a boolean value for prod_env - whether the bug was fixed in production environment, or not", required=True)
point_post_args.add_argument("employee_name", type=str, help="Provide the name of the employee who earned the point (must be one of the employees in the DB)", required=True)
point_post_args.add_argument("application_name", type=str, help="Provide the name of the application in which employee fixed bug (must be one of the applications in the DB", required=True)

class DerefName(fields.Raw):
    def format(self, dbobject):
        return dbobject.name


point_fields = point_ns.model('Point', {
    "date_added":fields.DateTime,
    "date_earned":fields.DateTime,
    "employee_name":DerefName(attribute="employee"),
    "application_name":DerefName(attribute="application"),
    "description":fields.String,
    "prod_env":fields.Boolean
})

@point_ns.route('/add')
class AddPoint(Resource):
    @point_ns.doc('add point')
    @point_ns.marshal_with(point_fields, code=201)
    @point_ns.expect(point_post_args)
    def post(self):
        '''Add a point'''
        args = point_post_args.parse_args()
        try:
            awarded_employee = Employees.objects(name=args['employee_name']).get()
        except Employees.DoesNotExist:
            abort(404, message="Could not find employee with that name")
        try:
            awarded_application = Applications.objects(name=args['application_name']).get()
        except Applications.DoesNotExist:
            abort(404, message="Could not find application with that name")
        for period in PeriodWinners.objects():
            if args['date_earned']  > period.startdate and args['date_earned'] < period.enddate and period.evaluated:
                abort(403, message="You can not add points to a period that's already been evaluated")
        point = Points(date_earned=args['date_earned'], employee=awarded_employee, application=awarded_application, description=args['description'], prod_env=args['prod_env'])
        point.save()
        return point, 201

point_per_employee_args = reqparse.RequestParser()
point_per_employee_args.add_argument("start_date", type=inputs.date_from_iso8601, help="Provide a date from which you want to count the employee's points (YYYY-MM-DD)")
point_per_employee_args.add_argument("end_date", type=inputs.date_from_iso8601, help="Provide a date until which you want to count the employee's points (YYYY-MM-DD)")
point_per_employee_args.add_argument("employee_name", type=str, help="Provide name of employee whose points you want to count", required=True)

points_per_employee_fields = point_ns.model('Total points per employee', {
    "date_from":fields.DateTime,
    "date_to":fields.DateTime,
    "employee":fields.String,
    "total_points":fields.Integer,
})

@point_ns.route('/employee')
class PointsPerEmployee(Resource):
    @point_ns.doc('get points for specific employee')
    @point_ns.expect(point_per_employee_args)
    @point_ns.marshal_with(points_per_employee_fields, code=200)
    def get(self):
        '''Get total points for specific employee in given time period (defaults to 01/01/1900 - now if no parameters given)'''
        args = point_per_employee_args.parse_args()
        if args['start_date']:
            date_from = args['start_date']
        else:
            date_from = datetime.datetime(1900, 1, 1)
        if args['end_date']:
            date_to = args['end_date']
        else:
            date_to = datetime.datetime.now()
        try:
            employee = Employees.objects(name=args['employee_name']).get()
        except Employees.DoesNotExist:
            abort(404, message="Could not find employee with that name")
        point_count = Points.objects.filter(date_earned__gte=date_from, date_earned__lte=date_to, employee=employee).count()
        return {'date_from':date_from, 'date_to': date_to,'employee': employee.name, 'total_points': point_count}

all_employee_points_args = reqparse.RequestParser()
all_employee_points_args.add_argument("start_date", type=inputs.date_from_iso8601, help="Provide date from which you want to count employees' points (YYYY-MM-DD)")
all_employee_points_args.add_argument("end_date", type=inputs.date_from_iso8601, help="Provide date until which you want to count employees' points (YYYY-MM-DD)")

employee_point_pair_fields = point_ns.model('Employee-point pair', {
    "employee_name":fields.String,
    "total_points":fields.Integer
})

all_employee_points_fields = point_ns.model('Total points for all employees', {
    "date_from":fields.DateTime,
    "date_to":fields.DateTime,
    "point_totals":fields.List(fields.Nested(employee_point_pair_fields), attribute='total_points')
})


@point_ns.route('/allemployees')
class AllEmployeePoints(Resource):
    @point_ns.doc('get points for all employees')
    @point_ns.expect(all_employee_points_args)
    @point_ns.marshal_with(all_employee_points_fields, code=200)
    def get(self):
        '''Get points for all employees in specific time period (defaults to 01/01/1900 - now if no parameters given)'''
        args = all_employee_points_args.parse_args()
        if args['start_date']:
            date_from = args['start_date']
        else:
            date_from = datetime.datetime(1900, 1, 1)
        if args['end_date']:
            date_to = args['end_date']
        else:
            date_to = datetime.datetime.now()
        
        point_totals = []

        for employee in Employees.objects():
            name = employee.name
            point_count = Points.objects.filter(date_earned__gte=date_from, date_earned__lte=date_to, employee=employee).count()
            point_totals.append({'employee_name':name, 'total_points':point_count})

        return {'date_from': date_from, 'date_to':date_to, 'total_points':point_totals}

@point_ns.route('/allpoints')
class AllPoints(Resource):
    @point_ns.doc('get all the points, with the option to specify a period')
    @point_ns.marshal_list_with(point_fields, code=200)
    @point_ns.expect(all_employee_points_args)
    def get(self):
        '''Get all single points in the database, with the option to specify a period (defaults to 01/01/1900 - now if no parameters given)'''
        args = all_employee_points_args.parse_args()
        if args['start_date']:
            date_from = args['start_date']
        else:
            date_from = datetime.datetime(1900, 1, 1)
        if args['end_date']:
            date_to = args['end_date']
        else:
            date_to = datetime.datetime.now()
        points = []
        for point in Points.objects.filter(date_earned__gte=date_from, date_earned__lte=date_to):
            points.append(point)
        return points, 200
        

