from parent_class import ParentPluralList
import kabbes_config

from .Base import Base
from .Single import Single

class List( ParentPluralList, Base ):

    def __init__( self, *args, **kwargs ):
        Base.__init__( self, *args, **kwargs ) 
        ParentPluralList.__init__( self, att='Values')

        self.load_Singles()

    def load_Singles( self ):

        for item in self.value:
            self._add( Single( self.Node, item ) )

    def get_raw( self ):
        return [ Single.get_raw() for Single in self ]

    def get_ref( self ):
        return [ Single.get_ref() for Single in self ]

    def merge_ref( self, *args, **kwargs ):
        
        for Single in self:
            Single.merge_ref( *args, **kwargs )
