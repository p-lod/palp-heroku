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
      with div():
        a("[display in p-lod]", href=f"http://p-lod.herokuapp.com/p-lod/id/{identifier}")




def spatial_hierarchy(identifier):
  # spatial ancestors
    qt = Template("""
PREFIX p-lod: <urn:p-lod:id:>
SELECT DISTINCT ?spatial_id ?type WHERE { 
  { p-lod:$identifier p-lod:is-part-of*/p-lod:created-on-surface-of* ?feature .
    ?feature p-lod:spatially-within* ?spatial_id .
    ?feature a p-lod:feature  .
    OPTIONAL { ?spatial_id a ?type }
    }
    UNION
    { p-lod:$identifier p-lod:spatially-within+ ?spatial_id  . 
      OPTIONAL { ?spatial_id a ?type }
    }
  }""")
    id_spatial_ancestors = g.query(qt.substitute(identifier = identifier))
    id_spatial_ancestors_df = pd.DataFrame(id_spatial_ancestors, columns = id_spatial_ancestors.json['head']['vars']).astype(str)
    

    return id_spatial_ancestors_df[['spatial_id','type']].to_html()
 



# list of types to render for PALP
render_these = ['city','region','insula','property','space','feature','artwork','concept']

# type renderers
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
      palp_page_footer(html_doc, identifier)
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
          span(f"Check that it's a region and if yess, query the triple store for info about {identifier}.")
          div(dominate.util.raw(spatial_hierarchy(identifier)))
  palp_page_footer(html_doc, identifier)
  return html_doc.render()

def insula_render(identifier):
  html_doc = dominate.document(title="Pompeii Artistic Landscape Project: %s" % (identifier))
  palp_html_head(html_doc, identifier)
  html_doc.body
  palp_page_header(html_doc)
  with html_doc:
      with div(id="page-content-wrapper"):
        with div(id="container-fluid"):
          span(f"Check that it's an insula and if yes, query the triple store for info about {identifier}.")
          div(dominate.util.raw(spatial_hierarchy(identifier)))
  palp_page_footer(html_doc, identifier)
  return html_doc.render()

def property_render(identifier):
  html_doc = dominate.document(title="Pompeii Artistic Landscape Project: %s" % (identifier))
  palp_html_head(html_doc, identifier)
  html_doc.body
  palp_page_header(html_doc)
  with html_doc:
      with div(id="page-content-wrapper"):
        with div(id="container-fluid"):
          span(f"Check that it's a property and if yes, query the triple store for info about {identifier}.")
          div(dominate.util.raw(spatial_hierarchy(identifier)))
  palp_page_footer(html_doc, identifier)
  return html_doc.render()

def space_render(identifier):
  html_doc = dominate.document(title="Pompeii Artistic Landscape Project: %s" % (identifier))
  palp_html_head(html_doc, identifier)
  html_doc.body
  palp_page_header(html_doc)
  with html_doc:
      with div(id="page-content-wrapper"):
        with div(id="container-fluid"):
          span(f"Check that it's a space and if yes, query the triple store for info about {identifier}.")
          div(dominate.util.raw(spatial_hierarchy(identifier)))
  palp_page_footer(html_doc, identifier)
  return html_doc.render()

def feature_render(identifier):
  html_doc = dominate.document(title="Pompeii Artistic Landscape Project: %s" % (identifier))
  palp_html_head(html_doc, identifier)
  html_doc.body
  palp_page_header(html_doc)
  with html_doc:
      with div(id="page-content-wrapper"):
        with div(id="container-fluid"):
          span(f"Check that it's a feature and if yes, query the triple store for info about {identifier}.")
          div(dominate.util.raw(spatial_hierarchy(identifier)))
  palp_page_footer(html_doc, identifier)
  return html_doc.render()

def feature_render(identifier):
  html_doc = dominate.document(title="Pompeii Artistic Landscape Project: %s" % (identifier))
  palp_html_head(html_doc, identifier)
  html_doc.body
  palp_page_header(html_doc)
  with html_doc:
      with div(id="page-content-wrapper"):
        with div(id="container-fluid"):
          span(f"Assuming it's right type, query the triple store for info about {identifier}.")
          div(dominate.util.raw(spatial_hierarchy(identifier)))
  palp_page_footer(html_doc, identifier)
  return html_doc.render()

def artwork_render(identifier):
  html_doc = dominate.document(title="Pompeii Artistic Landscape Project: %s" % (identifier))
  palp_html_head(html_doc, identifier)
  html_doc.body
  palp_page_header(html_doc)
  with html_doc:
      with div(id="page-content-wrapper"):
        with div(id="container-fluid"):
          span(f"Assuming it's right type, query the triple store for info about {identifier}.")
          div(dominate.util.raw(spatial_hierarchy(identifier)))
          palp_page_footer(html_doc, identifier)
  return html_doc.render()

def concept_render(identifier):
  html_doc = dominate.document(title="Pompeii Artistic Landscape Project: %s" % (identifier))
  palp_html_head(html_doc, identifier)
  html_doc.body
  palp_page_header(html_doc)
  with html_doc:
      with div(id="page-content-wrapper"):
        with div(id="container-fluid"):
          span(f"Assuming it's right type, query the triple store for info about {identifier}.")
  palp_page_footer(html_doc, identifier)
  return html_doc.render()


@app.route('/palp/<path:type_to_render>/<path:identifier>')
def render_types(type_to_render,identifier):
    if type_to_render not in render_these:
      return(f"No specific PALP view available. Try at https://p-lod.herokuapp.com/p-lod/id/{identifier}")
    else:
      return globals()[f'{type_to_render}_render'](identifier) # dispatch to function for render


@app.route('/')
def index():
    return redirect("/palp/city//pompeii", code=302)

    
