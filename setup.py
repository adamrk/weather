from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import logging

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.environ['DB_PATH']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
logging.basicConfig(
    filename = "app.log",
    format = "%(levelname)-10s %(asctime)s %(message)s",
    level = logging.INFO
)