import py_starter as ps
import kabbes_config
import dir_ops as do

def load_Config( DEFAULT_CONFIG_PATH=None, config =None ):

    if config == None:
        config = kabbes_config.Config()

    # 1. Load default settings
    if DEFAULT_CONFIG_PATH != None:
        dictionary = ps.json_to_dict( DEFAULT_CONFIG_PATH.read() )
        config.load_dict( dictionary )
        config.reevaluate()

    # 2. Overwrite with system kwargs
    if len(kabbes_config.sys_kwargs) > 0:
        config.load_dict( kabbes_config.sys_kwargs )
        config.reevaluate()

    # 3. Load user_settings
    if config.has_attr( "user_config" ):
        if config.user_config.has_attr( 'Path' ):
            config.user_config.path = config.user_config.Path.path             

        if config.has_attr( 'user_config.path' ):
            config_Path = do.Path( config.user_config.path )
            if config_Path.exists():
                config.load_dict( ps.json_to_dict( config_Path.read() ) )
                config.load_dict( kabbes_config.sys_kwargs )
                config.reevaluate()

    return config

