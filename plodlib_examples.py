import plodlib

r_list = ['pompeii','r1','r1-i1','r1-i1-p1','bird','bogus_id_bogus']

for r in r_list:
	c = plodlib.PLODResource(r)
	print(f'''*Got info for "{r}" now reading from returned object
  Identifier: {c.identifier} (as passed: {c._identifier_parameter})
  Type: {c.type}
  Label: {c.label}

		''')

