from parent_class import ParentClass
import py_starter as ps
import kabbes_config

from .List import List
from .Single import Single

class Value( ParentClass ):

    def __init__( self, Node, value ):
        ParentClass.__init__( self )
        self.Node = Node
        self.set( value )

    def set( self, value ):
        
        if type(value) == list:
            self.Obj = List( self.Node, value )

        else:
            self.Obj = Single( self.Node, value )

    def get( self, ref=True ):
        if ref:
            return self.Obj.get_ref()
        else:
            return self.Obj.get_raw()

    def get_raw( self ):
        return self.Obj.get_raw()

    def get_ref( self ):
        return self.Obj.get_ref()

    def merge_ref( self, *args, **kwargs ):
        return self.Obj.merge_ref( *args, **kwargs)

