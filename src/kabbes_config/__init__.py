import dir_ops as do
import os
import py_starter as ps
import xdg

_Dir = do.Dir( os.path.abspath( __file__ ) ).ascend()   #Dir that contains the package 
_src_Dir = _Dir.ascend()                                  #src Dir that is one above
_repo_Dir = _src_Dir.ascend()                    
_cwd_Dir = do.Dir( do.get_cwd() )
_xdg_Dir = do.Dir( str(xdg.XDG_CONFIG_HOME ) )
_home_Dir = do.Dir( do.get_home_dir() )
settings_Path = _Dir.join_Path( path = 'default_settings.json' )

settings = ps.json_to_dict( settings_Path.read() )
_config_Dir = _xdg_Dir.join_Dir( path = settings['config_rel_dir'] )

if not _config_Dir.exists():
    _config_Dir.create()

sys_args, sys_kwargs = ps.get_system_input_arguments()

from .utils import *
from .Config import Config

