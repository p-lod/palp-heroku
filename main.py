import html

# because dominate will stop on html
pyhtml = html

import os
import re

import pandas as pd

import dominate
from dominate.tags import *

from bs4 import BeautifulSoup

from flask import Flask
from flask import render_template
from flask import request
from flask import redirect, url_for, after_this_request

from string import Template

import markdown

import rdflib as rdf
from rdflib.plugins.stores import sparqlstore


ns = {"dcterms" : "http://purl.org/dc/terms/",
      "owl"     : "http://www.w3.org/2002/07/owl#",
      "rdf"     : "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
      "rdfs"    : "http://www.w3.org/2000/01/rdf-schema#" ,
      "p-lod"   : "urn:p-lod:id:" }

app = Flask(__name__)



# Connect to the remote triplestore with read-only connection
store = rdf.plugin.get("SPARQLStore", rdf.store.Store)(endpoint="http://52.170.134.25:3030/plod_endpoint/query",
                                                       context_aware = False,
                                                       returnFormat = 'json')
g = rdf.Graph(store)


def palp_html_head(doc, plod = ''):
    doc.head += meta(charset="utf-8")
    doc.head += meta(http_equiv="X-UA-Compatible", content="IE=edge")
    doc.head += meta(name="viewport", content="width=device-width, initial-scale=1")    
    doc.head += link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/css/bootstrap.min.css", integrity="sha384-TX8t27EcRE3e/ihU7zmQxVncDAy5uIKz4rEkgIXeMed4M0jlfIDPvg6uqKI2xXr2", crossorigin="anonymous")
    doc.head += script(src="https://code.jquery.com/jquery-3.5.1.slim.min.js", integrity = "sha384-DfXdz2htPH0lsSSs5nCTpuj/zy4C+OGpamoFVy38MVBnE+IbbVYUew+OrCXaRkfj", crossorigin="anonymous")
    doc.head += script(src="https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/js/bootstrap.bundle.min.js",integrity="sha384-ho+j7jyWK8fNQe+A12Hb8AhRq26LrZ/JpcUGGOn+Y7RsweNrtN/tE3MoK7ZeZDyx",crossorigin="anonymous")
    doc.head += style("body { padding-top: 60px; }")
    doc.head += meta(name="DC.title",lang="en",content="%s" % (plod) )
    doc.head += meta(name="DC.identifier", content="urn:p-lod:id/%s" % plod)

def palp_page_header(doc):
    with doc:
      with div(cls="jumbotron text-center"):
        div("Standard (smaller?) PALP Banner Here",)
        div("And other content / navigation /etc. Same for every page.", style="font-size:smaller")

def palp_page_footer(doc, identifier):
    with doc:
      with div:
        a("[display in p-lod]",href=f"http://p-lod.herokuapp.com/p-lod/id/{identifier}")


format_these = ['city','region','insula','property','space','feature','artwork','concept']

def city_render(identifier):
  if identifier == 'pompeii':
      html_doc = dominate.document(title="Pompeii Artistic Landscape Project: %s" % (identifier))
      palp_html_head(html_doc, identifier)
      html_doc.body
      palp_page_header(html_doc)
      with html_doc:
          with div(id="page-content-wrapper"):
            with div(id="container-fluid"):
              span(f"Query the triple store and show the results but we can also add all sorts of stuff.")
              a("Pompeii In Pictures ", href="https://pompeiiinpictures.com/pompeiiinpictures/index.htm")
              a("Getty DAH Grants", href="https://www.getty.edu/foundation/initiatives/current/dah/dah_grants_awarded.html")


      return html_doc.render()
      
  else:
      return("Unknown city.")

def region_render(identifier):
  html_doc = dominate.document(title="Pompeii Artistic Landscape Project: %s" % (identifier))
  palp_html_head(html_doc, identifier)
  html_doc.body
  palp_page_header(html_doc)
  with html_doc:
      with div(id="page-content-wrapper"):
        with div(id="container-fluid"):
          span(f"Query the triple store for info about {identifier} if that's a region.")
  
  return html_doc.render()


@app.route('/palp/<path:formatted_type>/<path:identifier>')
def formatted_types(formatted_type,identifier):
    if formatted_type not in format_these:
      return("Don't know what to do")
    else:
      return globals()[f'{formatted_type}_render'](identifier)


@app.route('/')
def index():
    return redirect("/palp/city//pompeii", code=302)

    
