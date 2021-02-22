import html

# because dominate will stop on html
pyhtml = html

import os
import re
import sys

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

# install with python3 -m pip install git+https://github.com/p-lod/plodlib
import plodlib


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


def palp_html_head(r, html_dom):
    html_dom.head += meta(charset="utf-8")
    html_dom.head += meta(http_equiv="X-UA-Compatible", content="IE=edge")
    html_dom.head += meta(name="viewport", content="width=device-width, initial-scale=1")    
    html_dom.head += link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/css/bootstrap.min.css", integrity="sha384-TX8t27EcRE3e/ihU7zmQxVncDAy5uIKz4rEkgIXeMed4M0jlfIDPvg6uqKI2xXr2", crossorigin="anonymous")
    html_dom.head += script(src="https://code.jquery.com/jquery-3.5.1.slim.min.js", integrity = "sha384-DfXdz2htPH0lsSSs5nCTpuj/zy4C+OGpamoFVy38MVBnE+IbbVYUew+OrCXaRkfj", crossorigin="anonymous")
    html_dom.head += script(src="https://cdn.jsdelivr.net/npm/bootstrap@4.5.3/dist/js/bootstrap.bundle.min.js",integrity="sha384-ho+j7jyWK8fNQe+A12Hb8AhRq26LrZ/JpcUGGOn+Y7RsweNrtN/tE3MoK7ZeZDyx",crossorigin="anonymous")
    html_dom.head += style("body { padding-top: 60px; }")
    html_dom.head += meta(name="DC.title",lang="en",content=r.identifier )
    html_dom.head += meta(name="DC.identifier", content=f"urn:p-lod:id:{r.identifier}" )

def palp_page_header(r, html_dom):
    with html_dom:
      with div(cls="jumbotron text-center"):
        div("Pompeii Artistic Landscape Project (PALP)")
        if r.label:
          div(r.label)
        if r.identifier:
          div(r.identifier, style="font-size:smaller")
        with div(style="margin-top:1em"):
          # feature request: suppress a link when displaying the page it links to.
          a("[start]", href="/start")
          a("[map]", href="/map")
          a("[search]", href="/search")

def palp_page_footer(r, doc):
    with doc:
      with div():
        span("The Pompeii Artistic Landscape Project (PALP) is hosted at the University of Massachusetts-Amherst. PALP is funded by the Getty Foundation.")
        if r.identifier:
          a(f"[view {r.identifier} in p-lod]", href=f"http://p-lod.herokuapp.com/p-lod/id/{r.identifier}")


# convenience functions
def urn_to_anchor(urn):

  label         = urn.replace("urn:p-lod:id:","") # eventually get the actual label
  relative_url  = f'/browse/{urn.replace("urn:p-lod:id:","")}'

  return relative_url, label


# type renderers
def city_render(r,html_dom):

  with html_dom:
    with div(id="page-content-wrapper"):
      with div(id="container-fluid"):

        with div(id="spatial_children"):
          span("Insula and Streets Within")
          for i in r.spatial_children():
            relative_url, label = urn_to_anchor(i[0])
            a(f"{label} / ", href=relative_url)

        with div(id="depicts_concepts"):
          span("Depicts Concepts")
          for i in r.depicts_concepts():
            relative_url, label = urn_to_anchor(i[0])
            a(f"{label} / ", href=relative_url)


def region_render(r,html_dom):

  with html_dom:
      with div(id="page-content-wrapper"):
        with div(id="container-fluid"):

          if r.geojson:
            with div(id="geojson"):
              span(f"Geojson: {r.geojson[0:20]} ...")


          with div(id="spatial_hierarchy"):
            span("Spatial Hierarchy: ")
            for i in r.spatial_hierarchy_up():
              relative_url, label = urn_to_anchor(i[0])
              a(f"{label} / ", href=relative_url)

          with div(id="spatial_children"):
            span("Insula and Streets Within")
            for i in r.spatial_children():
              relative_url, label = urn_to_anchor(i[0])
              a(f"{label} / ", href=relative_url)

          with div(id="depicts_concepts"):
            span("Depicts Concepts")
            for i in r.depicts_concepts():
              relative_url, label = urn_to_anchor(i[0])
              a(f"{label} / ", href=relative_url)


def insula_render(r,html_dom):

  with html_dom:
      with div(id="page-content-wrapper"):
        with div(id="container-fluid"):

          if r.geojson:
            with div(id="geojson"):
              span(f"Geojson: {r.geojson[0:20]} ...")

          with div(id="spatial_hierarchy"):
            span("Spatial Hierarchy")
            for i in r.spatial_hierarchy_up():
              relative_url, label = urn_to_anchor(i[0])
              a(f"{label} / ", href=relative_url)

          with div(id="spatial_children"):
            span("Properties Within")
            for i in r.spatial_children():
              relative_url, label = urn_to_anchor(i[0])
              a(f"{label} / ", href=relative_url)

          with div(id="depicts_concepts"):
            span("Depicts Concepts")
            for i in r.depicts_concepts():
              relative_url, label = urn_to_anchor(i[0])
              a(f"{label} / ", href=relative_url)


def property_render(r,html_dom):

  with html_dom:
      with div(id="page-content-wrapper"):
        with div(id="container-fluid"):

          with div(id="spatial_hierarchy"):
            span("Spatial Hierarchy")
            for i in r.spatial_hierarchy_up():
              relative_url, label = urn_to_anchor(i[0])
              a(f"{label} / ", href=relative_url)

          with div(id="spatial_children"):
            span("Spaces Within")
            for i in r.spatial_children():
              relative_url, label = urn_to_anchor(i[0])
              a(f"{label} / ", href=relative_url)

          with div(id="depicts_concepts"):
            span("Depicts Concepts")
            for i in r.depicts_concepts():
              relative_url, label = urn_to_anchor(i[0])
              a(f"{label} / ", href=relative_url)


def space_render(r,html_dom):

  with html_dom:
      with div(id="page-content-wrapper"):
        with div(id="container-fluid"):

          with div(id="spatial_hierarchy"):
            span("Spatial Hierarchy: ")
            for i in r.spatial_hierarchy_up():
              relative_url, label = urn_to_anchor(i[0])
              a(f"{label} / ", href=relative_url)

          with div(id="spatial_children"):
            span("Features Within")
            for i in r.spatial_children():
              relative_url, label = urn_to_anchor(i[0])
              a(f"{label} / ", href=relative_url)

          with div(id="depicts_concepts"):
            span("Depicts Concepts")
            for i in r.depicts_concepts():
              relative_url, label = urn_to_anchor(i[0])
              a(f"{label} / ", href=relative_url)


def feature_render(r,html_dom):

  with html_dom:
      with div(id="page-content-wrapper"):
        with div(id="container-fluid"):

          with div(id="spatial_hierarchy"):
            span("Spatial Hierarchy")
            for i in r.spatial_hierarchy_up():
              relative_url, label = urn_to_anchor(i[0])
              a(f"{label} / ", href=relative_url)

          with div(id="depicts_concepts"):
            span("Depicts Concepts")
            for i in r.depicts_concepts():
              relative_url, label = urn_to_anchor(i[0])
              a(f"{label} / ", href=relative_url)
 


def artwork_render(r,html_dom):

  with html_dom:
      with div(id="page-content-wrapper"):
        with div(id="container-fluid"):

          with div(id="spatial_hierarchy"):
            span("Spatial Hierarchy")
            for i in r.spatial_hierarchy_up():
              relative_url, label = urn_to_anchor(i[0])
              a(f"{label} / ", href=relative_url)

          with div(id="depicts_concepts"):
            span("Depicts Concepts")
            for i in r.depicts_concepts():
              relative_url, label = urn_to_anchor(i[0])
              a(f"{label} / ", href=relative_url)


def concept_render(r,html_dom):

  with html_dom:
      with div(id="page-content-wrapper"):
        with div(id="container-fluid"):
          span("Depicted in the following Pompeian spaces: ")
          for i in r.depicted_where():
              relative_url, label = urn_to_anchor(i[0])
              with span():
                a(f"{label} / ", href=relative_url)


def street_render(r,html_dom):

  with html_dom:
      with div(id="page-content-wrapper"):
        with div(id="container-fluid"):
          span(f"Assuming it's right type, query the triple store for info about {r.identifier}.")
          for i in r.depicted_where():
            pre(' '.join(i))



def unknown_render(r,html_dom):

  with html_dom:
      with div(id="page-content-wrapper"):
        with div(id="container-fluid"):
          span(f"Unknown type.")



def palp_html_document(r,renderer):

  html_dom = dominate.document(title=f"Pompeii Artistic Landscape Project: {r.identifier}" )

  palp_html_head(r, html_dom)
  html_dom.body
  palp_page_header(r,html_dom)

  renderer(r, html_dom)

  palp_page_footer(r, html_dom)

  return html_dom


# The PALP Verbs that Enable Navigation

@app.route('/start')
def palp_start():
  return """Useful, appealing, and explanatory start page that looks like a PALP page.
  Eric Poehler (UMass), Director and Sebastian Heath (NYU/ISAW), Co-Director. Funded by Getty Foundation. Etc., etc., etc.
  <a href="/browse/pompeii">Pompeii</a>.
  """

@app.route('/browse/<path:identifier>')
def palp_browse(identifier):

  r = plodlib.PLODResource(identifier)

  try:
    return palp_html_document(r, globals()[f'{r.type}_render']).render() # call p_h_d with right render function if it exists
  except KeyError as e:
    return palp_html_document(r,unknown_render).render()

@app.route('/map/')
def palp_map():
    return """Super cool and useful map page. What should it do? <a href="/start">Start</a>."""

@app.route('/search/')
def palp_search():
    return """Super cool and useful search page. What should it do? <a href="/start">Start</a>."""

@app.route('/')
def index():
    return redirect("/start", code=302)

