import os

import dominate
from dominate.tags import *

from flask import Flask
from flask import render_template
from flask import request

import rdflib

app = Flask(__name__)

@app.route('/', methods=['GET'])
def hello():
    doc = dominate.document(title="Pompeii LOD: ")
    with doc:
        h1("Pompeii LOD")
    return doc.render()

