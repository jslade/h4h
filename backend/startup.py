from flask import Flask

from hfh.app import APP
import hfh.db
import hfh.models.all
import hfh.controllers

if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=5000)
