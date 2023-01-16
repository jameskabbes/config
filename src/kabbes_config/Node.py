from parent_class import ParentClass
import py_starter as ps
import kabbes_config

class Node( ParentClass ):

    _ARGS_KEY = 'args'
    _KWARGS_KEY = 'kwargs'

    _ONE_LINE_ATTS = ['type','Key','Value']

    def __init__( self, key, parent=None, value=None, dict={}):

        ParentClass.__init__( self )

        self._init_Nodes()

        self.Key = kabbes_config.key.Key( self, key )
        self.set_value( value )
        self.parent = parent
        self.load_dict( dict )

    def __len__( self ):
        return len(self.nodes)
    def __contains__( self, key ):
        return key in self.nodes
    def __getitem__( self, key: str ):
        return self.get_key( key, ref=True )

    def _init_Nodes( self ):
        self.nodes = kabbes_config.Nodes( self )

    ### Walk
    def walk( self, leaves:bool=True, branches:bool=True ):

        """returns a list of nodes underneath self, including self"""

        nodes = []
        if len(self) > 0: #branch
            for child in self.nodes:
                nodes.extend( child.walk( leaves=leaves, branches=branches ) )
            if branches:
                nodes.insert( 0, self )

        else: #leaf
            if leaves:
                nodes.extend( [self] )

        return nodes

    def get_parents( self ):

        """returns list of parent node instances, including self"""

        parents = [ self ]
        if self.parent != None:
            return self.parent.get_parents() + parents

        return parents

    def get_root( self ):

        if self.parent != None:
            return self.parent.get_root()
        return self

    ### getting node
    def get_node( self, key: str, **kwargs ):

        """level1.level2.level3"""
        default_kwargs = {
            "make": False,
            "eval": True,
            "has":  False
        }
        kwargs = ps.merge_dicts( default_kwargs, kwargs )

        head, body = kabbes_config.key.Key(None,key).chop_off_head()

        if head == '':
            if kwargs['has']:
                return True
            else:   
                return self

        if head in self:
            return self.nodes[ head ].get_node( body, **kwargs )

        if head not in self:
            
            # !attr in self
            eval_key = kabbes_config.key.Key(None,head).add_eval_code()
            if eval_key in self:
                eval_node = self.nodes[ eval_key ]
                if kwargs['eval']:

                    return eval_node.Key.eval().get_node( body, **kwargs )
                elif kwargs['has']:
                    return self.nodes[ eval_key ].get_node( body, **kwargs )

            elif kwargs['make']:
                self.make_Node( head )
                return self.nodes[ head ].get_node( body, **kwargs )
    
        if kwargs['has']:
            return False
        else:
            print ('returning none')
            return None

    def set_key( self, key: str, value ):

        node = self.get_node( key, make=True, eval=False, has=False )
        if isinstance( value, dict ):
            node.load_dict( value )
        else:
            node.set_value( value )

    def has_key( self, key: str ) -> bool:
        return self.get_node( key, make=False, eval=False, has=True)

    def get_key( self, key: str, ref=True ):

        node = self.get_node( key, make=False, eval=True, has=False)

        if node != None:
           
            # Return the Node
            if node.get_raw_value() == None:
                return node

            # Return the Value
            else:
                return node.get_value( ref=ref )

        return None

    ### Value
    def set_value( self, value ):
        self.Value = kabbes_config.value.Value( self, value )
        self._init_Nodes() #nodes with values cannot have children

    def get_value( self, **kwargs ):
        return self.Value.get( **kwargs )
    def get_ref_value( self ):
        return self.Value.get_ref()
    def get_raw_value( self ):
        return self.Value.get_raw()

    ### Loading
    def load_dict( self, dict ):
        for key in dict:
            self.set_key( key, dict[key] )            

    def merge( self, node ):

        og_parents = node.get_parents()[1:] #don't count config root
        node_copy = Node( 'TEMP', dict=node.get_dict( ref=False, eval=False ) ) #we don't want to overwrite the original object

        new_parents = self.get_parents()[1:] #don't count config root
        leaf_nodes = node_copy.walk( leaves=True,branches=False )
        for leaf_node in leaf_nodes:
            leaf_node.Value.merge_ref( og_parents=og_parents, new_parents=new_parents )

        self.load_dict( node_copy.get_dict(ref=False,eval=False) )

    ### Nodes
    def make_Node( self, *args, **kwargs ):
        """makes a child node and adds it to nodes, do not pass '.' separated keys"""
        new_node = Node( *args, **kwargs, parent=self )
        self.nodes._add( new_node.Key.key, new_node )
        return new_node

    def _del_self( self ):
        self.parent.nodes._remove( self.Key.key )

    ### args, kwargs
    def get_args( self ):
        if self._ARGS_KEY in self.nodes:
            args_node = self.nodes[ self._ARGS_KEY ]
            return args_node.get_value( ref=True )
        return []

    def get_kwargs( self ):
        
        if self._KWARGS_KEY in self.nodes:
            kwargs_node = self.nodes[ self._KWARGS_KEY ]
            return kwargs_node.get_dict( ref=True, eval=True )
        return {}

    def get_dict( self, **kwargs ):

        default_kwargs = {
             "ref": True, 
             "eval":True
        }
        kwargs = ps.merge_dicts( default_kwargs, kwargs )

        d = {}

        #parent node
        for child_Node in self.nodes:

            #!attr
            if child_Node.Key.has_eval_code() and kwargs['eval']:
                value = self.get_node( child_Node.Key.strip_eval_code(), eval=kwargs['eval'] )
                d[child_Node.Key.strip_eval_code()] = value.get_dict( **kwargs )

            #attr
            else:
                node = self.get_node( child_Node.Key.key, eval=kwargs['eval'] )
                value =  node.get_dict( **kwargs )

                d[ child_Node.Key.key ] = node.get_dict( **kwargs )

        if self.get_raw_value() != None:
            return self.get_value( ref=kwargs['ref'] )

        return d 

    def get_raw_dict( self ):
        return self.get_dict( ref=False, eval=False )

    def get_ref_dict( self ): 
        return self.get_dict( ref=True, eval=False )

    def get_eval_dict( self ):
        return self.get_dict( ref=True, eval=True )

    ### feedback
    def print_imp_atts( self, tab=0, ref=False, eval=False, **override_kwargs ):
        
        default_kwargs = {'print_off': True}
        kwargs = ps.merge_dicts( default_kwargs, override_kwargs ) 

        string = ''
        node_dict = self.get_dict( ref=ref, eval=eval )

        if type(node_dict) == dict:
            for key in node_dict:
                string += '\t'*tab + key + '\n'
                new_kwargs = kwargs.copy()
                new_kwargs['print_off'] = False
                string += self.get_node( key, ref=ref,eval=eval ).print_imp_atts( tab=tab+1, ref=ref,eval=eval, **new_kwargs )
       
        value = self.get_value( ref=ref )
        if value != None:
            string += '\t'*(tab) + str(value) + '\n'

        return self.print_string( string, print_off = kwargs['print_off'] )
