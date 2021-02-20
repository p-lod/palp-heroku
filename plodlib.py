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
    
        # type and label first
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

        # now in alphabetical order
        self.geojson = None
        try:
        	self.geojson = id_df.loc['urn:p-lod:id:geojson','o']
        except:
        	self.geojson = None


        self.p_in_p_url = None
        try:
        	self.p_in_p_url = id_df.loc['urn:p-lod:id:p-in-p-url','o']
        except:
        	self.p_in_p_url = None


        self.wikidata_url = None
        try:
        	self.wikidata_url = id_df.loc['urn:p-lod:id:wikidata-url','o']
        except:
        	self.wikidata_url = None
        
        # set identifer if it exists. None otherwise. Preserve identifier as passed
        self._identifier_parameter = identifier
        if len(id_df.index) > 0:
        	self.identifier = identifier
        else:
        	self.identifier = None

        # convenience (remove if too much overhead?)
        self._sparql_results_as_html_table = id_df.to_html()
        self._id_df = id_df


    ## get_predicate_values ##
    def get_predicate_values(self,predicate = 'urn:p-lod:id:label'):
        # predicate should be a fully qualified url or urn as a string.
        # returns a list.


        # Connect to the remote triplestore with read-only connection
        store = rdf.plugin.get("SPARQLStore", rdf.store.Store)(endpoint="http://52.170.134.25:3030/plod_endpoint/query",
                                                       context_aware = False,
                                                       returnFormat = 'json')
        g = rdf.Graph(store)

        identifier = self.identifier
        if identifier == None:
            return []

        qt = Template("""
PREFIX p-lod: <urn:p-lod:id:>
SELECT ?o WHERE { p-lod:$identifier <$predicate> ?o . }
""")

        results = g.query(qt.substitute(identifier = identifier, predicate = predicate))
        id_df = pd.DataFrame(results, columns = results.json['head']['vars'])
        id_df = id_df.applymap(str)

        return list(id_df['o'])

    

    ## get_spatial_hierarchy ##
    def get_spatial_hierarchy(self):
        # Connect to the remote triplestore with read-only connection
        store = rdf.plugin.get("SPARQLStore", rdf.store.Store)(endpoint="http://52.170.134.25:3030/plod_endpoint/query",
                                                       context_aware = False,
                                                       returnFormat = 'json')
        g = rdf.Graph(store)

        identifier = self.identifier
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
        results = g.query(qt.substitute(identifier = identifier))
        df = pd.DataFrame(results, columns = results.json['head']['vars'])
        df = df.applymap(str)
    
        return df.values.tolist()


    ## get_depicted_concepts ##
    def get_depicted_concepts(self):
        # Connect to the remote triplestore with read-only connection
        store = rdf.plugin.get("SPARQLStore", rdf.store.Store)(endpoint="http://52.170.134.25:3030/plod_endpoint/query",
                                                       context_aware = False,
                                                       returnFormat = 'json')
        g = rdf.Graph(store)

        identifier = self.identifier

        qt = Template("""
PREFIX plod: <urn:p-lod:id:>

SELECT DISTINCT ?concept WHERE {
 
    plod:$identifier ^plod:spatially-within*/^plod:created-on-surface-of*/^plod:is-part-of* ?component .
    ?component a plod:artwork-component .
    ?component plod:depicts ?concept .

    # when this is part of the PALP interface, this clause can select "smallest 
    # clickable spatial unit" that will be shown to public via its own page
    #?component plod:is-part-of+/plod:created-on-surface-of/plod:spatially-within* ?within .
    #?within a plod:####within_resolution .

} ORDER BY ?depiction LIMIT 100""")
        results = g.query(qt.substitute(identifier = identifier))
        df = pd.DataFrame(results, columns = results.json['head']['vars'])
        df = df.applymap(str)
    
        return df.values.tolist()


    ## get_depicted_where ##
    def get_depicted_where(self, level_of_detail = 'space'):
        # Connect to the remote triplestore with read-only connection
        store = rdf.plugin.get("SPARQLStore", rdf.store.Store)(endpoint="http://52.170.134.25:3030/plod_endpoint/query",
                                                       context_aware = False,
                                                       returnFormat = 'json')
        g = rdf.Graph(store)

        identifier = self.identifier

        qt = Template("""
PREFIX plod: <urn:p-lod:id:>

SELECT DISTINCT ?within ?action ?color  WHERE {
    
    BIND ( plod:$resource AS ?resource )
   
    ?component plod:depicts ?resource .

    ?component plod:is-part-of+/plod:created-on-surface-of/plod:spatially-within* ?within .
    ?within a plod:$level_of_detail
 
    OPTIONAL { ?component plod:has-action ?action . }
    OPTIONAL { ?component plod:has-color  ?color . }

} ORDER BY ?within""")

       # resource = what you're looking for, within_resolution = spatial resolution at which to list results 
        results = g.query(qt.substitute(resource = identifier, level_of_detail = level_of_detail))

        df = pd.DataFrame(results, columns = results.json['head']['vars'])
        df = df.applymap(str)

        return df.values.tolist()



    