from flask import Flask

app = Flask(__name__)
app.config["DEBUG"] = True

from PotterParser import routes
from .Library import *
from . import __main__


