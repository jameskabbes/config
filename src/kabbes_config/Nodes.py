from parent_class import ParentPluralDict
import py_seedlings as ps

class Nodes( ParentPluralDict ):

    def __init__( self, Node ):
        ParentPluralDict.__init__( self, att='Nodes' )
        self.Node = Node

    def __contains__( self, key: str ):
        return key in self.Nodes

    def __getitem__( self, key: str ):
        return self.Nodes[ key ]


