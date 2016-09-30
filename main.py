import os

import dominate
from dominate.tags import *

from flask import Flask
from flask import render_template
from flask import request

import rdflib

app = Flask(__name__)

@app.route('/', methods=['GET'], defaults={'path': ''})
@app.route('/<path:path>')
def hello(path):
    g = rdflib.Graph()

    result = g.parse("p-lod.nt", format="nt")

    doc = dominate.document(title="Pompeii LOD: ")
    with doc:
        h1("Pompeii LOD")
        p(path)
    return doc.render()

