import turbogears.validators as v
import pdb

pdb.set_trace()
v = v.DateTimeConverter(not_empty=True)
print v.to_python("2002-4-4")


