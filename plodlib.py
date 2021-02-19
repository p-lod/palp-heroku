# Module for accessing information about P-LOD resource for rendering in PALP
# Define a function

from string import Template

import pandas as pd

import rdflib as rdf
from rdflib.plugins.stores import sparqlstore


# Define a class
class PLODResource:
    def __init__(self,identifier = None):

        # could defaut to 'pompeii' along with its info?
        if identifier == None:
        	self.identifier = None
        	return

    	# Connect to the remote triplestore with read-only connection
        store = rdf.plugin.get("SPARQLStore", rdf.store.Store)(endpoint="http://52.170.134.25:3030/plod_endpoint/query",
                                                       context_aware = False,
                                                       returnFormat = 'json')
        g = rdf.Graph(store)
        
        qt = Template("""
PREFIX p-lod: <urn:p-lod:id:>
SELECT ?p ?o WHERE { p-lod:$identifier ?p ?o . }
""")

        results = g.query(qt.substitute(identifier = identifier))
        id_df = pd.DataFrame(results, columns = results.json['head']['vars'])
        id_df = id_df.applymap(str)
        id_df.set_index('p', inplace = True)
    

        self.type = None
        try:
        	self.type = id_df.loc['http://www.w3.org/1999/02/22-rdf-syntax-ns#type','o'].replace('urn:p-lod:id:','')
        except:
        	self.type = None


        self.label = None
        try:
        	self.label = id_df.loc['http://www.w3.org/2000/01/rdf-schema#label','o']
        except:
        	self.label = None


        self.geojson = None
        try:
        	self.geojson = id_df.loc['urn:p-lod:id:geojson','o']
        except:
        	self.geojson = None


        self.wikidata_url = None
        try:
        	self.wikidata_url = id_df.loc['urn:p-lod:id:wikidata-url','o']
        except:
        	self.wikidata_url = None
        
        self._identifier_parameter = identifier
        if len(id_df.index) > 0:
        	self.identifier = identifier
        else:
        	self.identifier = None

        self._sparql_results_as_html_table = id_df.to_html()
        self._id_df = id_df

    

    