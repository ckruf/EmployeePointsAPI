from flask import Flask, app
from flask_restx import Api
from flask_mongoengine import MongoEngine

from api.routes import create_routes

default_config = {'MONGODB_SETTINGS':{
    'db':'employeepoints',
    'host':'localhost',
    'port':27017
}}

def get_flask_app(config: dict = None) -> app.Flask:
    flask_app = Flask(__name__)
    config = default_config if config is None else config
    flask_app.config.update(config)
    api=Api(app=flask_app, version='0.1', title='EmployeePointsAPI', description='A simple API for keeping track of points awarded to employees for fixing bugs')
    create_routes(api=api)
    db = MongoEngine(app=flask_app)

    return flask_app

if __name__ == '__main__':
    app = get_flask_app()
    app.run(debug=True)