import os
import urllib.request

import dominate
from dominate.tags import *

from flask import Flask
from flask import render_template
from flask import request

import rdflib

ns = {"dcterms" : "http://purl.org/dc/terms/",
      "rdf"     : "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
      "rdfs"    : "http://www.w3.org/2000/01/rdf-schema#" ,
      "p-lod"   : "http://digitalhumanities.umass.edu/p-lod/",
      "p-lod-v" : "http://digitalhumanities.umass.edu/p-lod/vocabulary/",
      "p-lod-e" : "http://digitalhumanities.umass.edu/p-lod/entities/" }

app = Flask(__name__)

g = rdflib.Graph()

result = g.parse("https://p-lod.github.io/p-lod.nt", format="nt")

@app.route('/p-lod/entities/<path:entity>')
def entities(entity):
 
    result = g.query(
        """SELECT ?p ?o ?plabel ?olabel
           WHERE {
              p-lod-e:%s ?p ?o .
              OPTIONAL { ?p rdfs:label ?plabel }
              OPTIONAL { ?o rdfs:label ?olabel }
           }""" % (entity), initNs = ns)

    label = g.query(
        """SELECT ?slabel 
           WHERE {
              p-lod-e:%s rdfs:label ?slabel
           }""" % (entity), initNs = ns)
           
    parts = g.query(
        """SELECT ?part ?label
           WHERE {
              ?part dcterms:isPartOf p-lod-e:%s .
              ?part rdfs:label ?label .
           } ORDER BY ?label""" % (entity), initNs = ns)

    edoc = dominate.document(title="Pompeii LOD: ")
    with edoc:
        h1("P-LOD: Linked Open Data for Pompeii")
        hr()

        for row in label:
            h2(str(row.slabel))

        for row in result:
            if str(row.p) == 'http://www.w3.org/2000/01/rdf-schema#label':
                continue
            elif str(row.plabel) != 'None':
                p(str(row.plabel)+":", style = "margin-left:.25em")
            else:
                p(i(str(row.p)), style = "margin-left:.25em")
                
            with p(style="margin-left:1em"):
                if str(row.olabel) != "None":
                    olabel = str(row.olabel)
                else:
                    olabel = str(row.o)
                
                if str(row.o)[0:4] == 'http':
                    a(olabel,href = str(row.o).replace('http://digitalhumanities.umass.edu',''))
                else:
                    span(olabel)
            p()
        
        if len(parts) > 0:
            h3('Has parts')
            for part in parts:
                p(a(str(part.label), href = str(part.part).replace('http://digitalhumanities.umass.edu','')))
        
        hr()
        with p():
            span("P-LOD is overseen by Steven Ellis, Sebastian Heath and Eric Poehler. Data available on ")
            a("Github", href = "https://github.com/p-lod/p-lod")
            span(".")
                
    return edoc.render()
    
@app.route('/p-lod/vocabulary/<path:vocab>')
def vocabulary(vocab):
    vresult = g.query(
        """SELECT ?p ?o ?plabel ?olabel
           WHERE {
              p-lod-v:%s ?p ?o .
              OPTIONAL { ?p rdfs:label ?plabel }
              OPTIONAL { ?o rdfs:label ?olabel }
           }""" % (vocab), initNs = ns)

    vlabel = g.query(
        """SELECT ?slabel 
           WHERE {
              p-lod-v:%s rdfs:label ?slabel
           }""" % (vocab), initNs = ns)
           
    vinstances = g.query(
        """SELECT ?instance ?label
           WHERE {
              ?instance rdf:type p-lod-v:%s .
              ?instance rdfs:label ?label .
           } ORDER BY ?label""" % (vocab), initNs = ns)

    vdoc = dominate.document(title="Pompeii LOD: ")
    with vdoc:
        h1("P-LOD: Linked Open Data for Pompeii")
        hr()

        for row in vlabel:
            h2(str(row.slabel))

        for row in vresult:
            if str(row.p) == 'http://www.w3.org/2000/01/rdf-schema#label':
                continue
            elif str(row.plabel) != 'None':
                p(str(row.plabel)+":", style = "margin-left:.25em")
            else:
                p(i(str(row.p)), style = "margin-left:.25em")
                
            with p(style="margin-left:1em"):
                if str(row.olabel) != "None":
                    olabel = str(row.olabel)
                else:
                    olabel = str(row.o)
                
                if str(row.o)[0:4] == 'http':
                    a(olabel,href = str(row.o).replace('http://digitalhumanities.umass.edu',''))
                else:
                    span(olabel)
            p()
        
        if len(vinstances) > 0:
            h3('Entities')
            for instance in vinstances:
                p(a(str(instance.label), href = str(instance.instance).replace('http://digitalhumanities.umass.edu','')))
                
    return vdoc.render()


@app.route('/')
def index():
    indexdoc = dominate.document(title="Pompeii LOD")
    with indexdoc:
        h1("Pompeii LOD")
        p(a("r1", href='/p-lod/entities/r1'))
             
    return indexdoc.render()
    

