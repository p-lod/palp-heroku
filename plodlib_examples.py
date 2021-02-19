import plodlib

r_list = ['pompeii','r1','r1-i1','r1-ii-p1','bird']

for r in r_list:
	c = plodlib.PLODId(r)
	print(f'''*Got info for "{r}" now reading from returned object
  Identifer: {c.identifier}
  Type: {c.type}
  Label: {c.label}

		''')

