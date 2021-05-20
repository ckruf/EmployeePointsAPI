from flask import jsonify
from flask_restx import Resource
from models.employees import Employees

class EmployeesApi(Resource):
    def get(self):
        output = Employees.objects()
        return jsonify({'result':output})

