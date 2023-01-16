import kabbes_config
import py_starter as ps
cfg = kabbes_config.Config( dict=kabbes_config._Dir.join_Path(path='__main__.json').read_json_to_dict()  )

print ('----RAW CONFIG----')
cfg.print_atts()
print ()
print ()

print ('----EVAL CONFIG----')
cfg.print_atts( eval=True,ref=True )
print ()
print ()
