import plodlib


# run through instantiating ids and printing standard info
r_list = ['pompeii','r1','r1-i1','r1-i1-p1','bird','bogus_id_bogus']

for r in r_list:
	c = plodlib.PLODResource(r)
	print(f'''*Got info for "{r}" now reading from returned object
  Identifier: {c.identifier} (as passed: {c._identifier_parameter})
  Type: {c.type}
  Label: {c.label}
  P-in-P URL: {c.p_in_p_url}
  Wikidata URL: {c.wikidata_url}

		''')

# some direct calls

print('Dog depicted where')
print(plodlib.PLODResource('dog').get_depicted_where())

print('r1-i9 depicts concepts')

print(plodlib.PLODResource('r1-i9').get_depicted_concepts())
