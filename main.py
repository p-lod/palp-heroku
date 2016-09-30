import os

import dominate
from dominate.tags import *

from flask import Flask
from flask import render_template
from flask import request

import rdflib

ns = {"dcterms": "http://purl.org/dc/terms/",
      "rdf" : "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
      "rdfs": "http://www.w3.org/2000/01/rdf-schema#" ,
      "p-lod" : "http://digitalhumanities.umass.edu/p-lod/",
      "p-lod-v" : "http://digitalhumanities.umass.edu/p-lod/vocabulary/",
      "p-lod-e" : "http://digitalhumanities.umass.edu/p-lod/entities/"}

app = Flask(__name__)

@app.route('/', methods=['GET'], defaults={'path': ''})
@app.route('/<path:path>')
def hello(path):
    g = rdflib.Graph()

    result = g.parse("p-lod.nt", format="nt")
    subjects = g.query(
        """SELECT DISTINCT ?s ?label
           WHERE {
              ?s ?p ?o .
              ?s rdfs:label ?label .
              ?s rdf:type ?type .
           } ORDER BY ?s""", initNs = ns)

    doc = dominate.document(title="Pompeii LOD: ")
    with doc:
        h1("Pompeii LOD")
        p(path)
        p()
        for row in subjects:
            p(str(row.label)
            
    return doc.render()

