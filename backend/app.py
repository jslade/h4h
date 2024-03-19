from flask import Flask
from flask_sqlalchemy import SQLAlchemy

APP = Flask(__name__)
APP.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@db:5432/hfh'
DB = SQLAlchemy(APP)

@APP.route('/')
def hello_world():
    return 'Hello, World!'

if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=5000)
