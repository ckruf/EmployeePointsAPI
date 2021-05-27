from flask import jsonify
from flask_restx import Resource, Namespace, reqparse, fields, marshal_with, inputs, abort
from models.applications import Applications

applications_ns = Namespace('applications', description="Operations with application list")

application_fields = applications_ns.model('Application', {
    'name':fields.String
})

application_args = reqparse.RequestParser()
application_args.add_argument("name", type=str, help="Provide a name for the application", required=True)

@applications_ns.route('/add')
class AddApplication(Resource):
    @applications_ns.doc('add an application')
    @applications_ns.marshal_with(application_fields, code=201)
    @applications_ns.expect(application_args)
    def post(self):
        '''Add an application'''
        args = application_args.parse_args()
        new_application = Applications(name=args['name'])
        new_application.save()
        return new_application, 201

@applications_ns.route('/all')
class AllApplications(Resource):
    @applications_ns.doc('get all applications')
    @applications_ns.marshal_list_with(application_fields, code=200)
    def get(self):
        '''Get all applications'''
        allapplications = []
        for application in Applications.objects():
            allapplications.append(application)
        return allapplications, 200

@applications_ns.route('/remove')
class DeleteApplication(Resource):
    @applications_ns.doc('delete an application', code=200)
    @applications_ns.marshal_with(application_fields)
    @applications_ns.expect(application_args)
    def delete(self):
        args = application_args.parse_args()
        deleted_application = Applications.objects(name=args['name']).get()
        deleted_application.delete()
        return deleted_application, 200