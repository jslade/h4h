from flask import Flask
from flask_sqlalchemy import SQLAlchemy

APP = Flask(__name__)
APP.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@db:5432/hfh'
DB = SQLAlchemy(APP)

@APP.route('/')
def hello_world():
    return 'Hello, World!'

@APP.route('/api/test')
def test_json():
    return {"test": "TEST "}

if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=5000)
