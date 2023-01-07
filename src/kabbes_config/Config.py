from kabbes_config import Node
import py_starter as ps

class Config( Node ):

    def __init__( self, **kwargs ):
        Node.__init__( self, 'config', parent=None, value=None, **kwargs )


