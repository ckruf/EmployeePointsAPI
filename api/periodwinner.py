from flask import jsonify
from flask_restx import Resource, Namespace, reqparse, fields, marshal_with, inputs, abort
from models.points import Points
from models.employees import Employees
from models.periodwinners import PeriodWinners
import random

period_winner_ns = Namespace('periodwinners', description='Period winners')

new_period_post_args = reqparse.RequestParser()
new_period_post_args.add_argument("period_start", type=inputs.datetime_from_iso8601, help="Provide a date or datetime for the start of the period (YYYY-MM-DDTHH:MM:SS)", required=True)
new_period_post_args.add_argument("period_end", type=inputs.datetime_from_iso8601, help="Provide a date or datetime for the end of the period (YYYY-MM-DDTHH:MM:SS)", required=True)
new_period_post_args.add_argument("period_name", type=str, help="Provide a name for the period", required=True)

period_eval_args = reqparse.RequestParser()
period_eval_args.add_argument("period_name", type=str, help="Provide name of period you want to evaluate", required=True)

class DerefName(fields.Raw):
    def format(self, dbobject):
        return dbobject.name

period_winner_fields = period_winner_ns.model('Winning period', {
    'periodname':fields.String,
    'startdate':fields.DateTime,
    'enddate':fields.DateTime,
    'winner': DerefName(attribute='winner'),
    'evaluated': fields.Boolean
})

@period_winner_ns.route('/add')
class AddPeriod(Resource):
    @period_winner_ns.doc('add period')
    @period_winner_ns.marshal_with(period_winner_fields, code=201)
    @period_winner_ns.expect(new_period_post_args)
    def post(self):
        '''Add a period'''
        args = new_period_post_args.parse_args()
        new_period = PeriodWinners(periodname=args['period_name'], startdate=args['period_start'], enddate=args['period_end'],winner=None)
        new_period.save()
        return new_period

@period_winner_ns.route('/all')
class AllPeriods(Resource):
    @period_winner_ns.doc('view all periods')
    @period_winner_ns.marshal_list_with(period_winner_fields, code=200)
    def get(self):
        '''Get all existing periods, regardless of evaluation'''
        allperiods = []
        for period in PeriodWinners.objects():
            allperiods.append(period)
        return allperiods, 200

@period_winner_ns.route('/evaluate')
class EvaluatePeriod(Resource):
    @period_winner_ns.doc('evaluate period winner')
    @period_winner_ns.marshal_with(period_winner_fields, code=200)
    @period_winner_ns.expect(period_eval_args)
    def put(self):
        '''Evaluate the winner for the given period'''
        args = period_eval_args.parse_args()
        try:
            period = PeriodWinners.objects(periodname=args['period_name']).get()
        except PeriodWinners.DoesNotExist:
            abort(404, message="Could not find period with that name")
        if period.evaluated:
            abort(403, message="A winner already exists for this period")
        else:
            #Create list of tuples, where each tuple will have the employee and their number of points
            employee_point_counts = []
            for employee in Employees.objects():
                point_count = Points.objects.filter(date_earned__gte=period.startdate, date_earned__lte=period.enddate, employee=employee).count()
                employee_point_tuple = (employee, point_count)
                employee_point_counts.append(employee_point_tuple)
            
            #Sort list of tuples, using the second element of each tuple (the number of points) as key
            employee_point_counts.sort(key=lambda x:x[1], reverse=True)
            
            #Check how many employees are tied for the win
            potential_winners = 0
            i = 0
            top_points = employee_point_counts[0][1]
            while employee_point_counts[i][1] == top_points:
                potential_winners += 1
                i += 1
            
            #If there is only one potential winner (one employee has more points than any other employee), then we can set him/her as winner 
            if potential_winners == 1:
                period.winner = employee_point_counts[0][0]
                period.evaluated = True
                period.save()
                return period, 200
            #If there are multiple potential winners (tied for most points), then we choose the winner randomly
            else:
                random_index = random.randrange(potential_winners)
                period.winner = employee_point_counts[random_index][0]
                period.evaluated = True
                period.save()
                return period, 200

@period_winner_ns.route('/unevaluate')
class UnEvaluatePeriod(Resource):
    @period_winner_ns.doc('unevaluate period')
    @period_winner_ns.expect(period_eval_args)
    @period_winner_ns.marshal_with(period_winner_fields, code=200)
    def put(self):
        '''Unevalute period (for example if you want to add more points for that month)'''
        args = period_eval_args.parse_args()
        try:
            period = PeriodWinners.objects(periodname=args['period_name']).get()
        except PeriodWinners.DoesNotExist:
            abort(404, message="Could not find period with that name")
        if not period.evaluated:
            abort(403, message="This period has not been evaluated yet")
        else:
            period.winner = None
            period.evaluated = False
            period.save()
            return period, 200
