from parent_class import ParentClass
import py_starter as ps
import dir_ops as do

from kabbes_config import Value, Key

class Node( ParentClass ):

    _SPECIAL_REF_OBJS = {
        "$Dir": do.Dir()
    }

    _ONE_LINE_ATTS = ['type','key']

    def __init__( self, key, parent=None, value=None, dict={}):

        ParentClass.__init__( self )

        self.nodes = {}
        self.key = key
        self.make_Value( value )
        self.parent = parent
        self.load_dict( dict )

    def __len__( self ):
        return len(self.nodes)

    def __iter__( self ):
        self.i = -1
        return self

    def __next__( self ):

        self.i += 1

        if self.i >= len(self):
            raise StopIteration
        else:
            return self.nodes[ list(self.nodes.keys())[self.i] ]

    def __contains__( self, key ):
        return key in self.nodes

    def __getitem__( self, key: str ):
        return self.get_key( key, ref=True )

    ### Value
    def make_Value( self, value ):
        self.Value = Value( self, value )

    def set_value( self, value ):
        self.Value.set( value )
        self.nodes = {}

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
        self.load_dict( node.get_dict(ref=False,eval=False) )

    ### Nodes
    def _add_Node( self, node ):
        self.nodes[ node.key ] = node

    def make_Node( self, *args, **kwargs ):

        node = Node( *args, **kwargs, parent=self )
        self._add_Node( node )
        return node

    def del_self( self ):
        del self.parent.nodes[ self.key ]

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

        ###
        head, body = Key.chop_off_head( key )
        
        if head == '':
            if kwargs['has']:
                return True
            else:   
                return self

        if head in self:
            return self.nodes[ head ].get_node( body, **kwargs )

        if head not in self:

            if Key.add_eval_code( head ) in self:
                if kwargs['eval']:
                    return self.eval( key ).get_node( body, **kwargs )
                elif kwargs['has']:
                    return self.nodes[ Key.add_eval_code(head) ].get_node( body, **kwargs )

            elif kwargs['make']:
                self.make_Node( head )
                return self.nodes[ head ].get_node( body, **kwargs )
    
        if kwargs['has']:
            return False
        else:
            return None

    ### get, set, has
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
    
    ### evaluate.!this 
    def eval( self, key: str ):
        
        eval_key = Key.add_eval_code( key )  

        # if the node "!eval_key" is not present
        if not self.has_key( eval_key ):
            return self

        #otherwise...
        eval_key_node = self.nodes[ eval_key ]

        # if $ref is found under the node
        if eval_key_node.has_key( Key._REF_OBJ_KEY ):

            # $ref
            ref_obj_node = eval_key_node.nodes[ Key._REF_OBJ_KEY ]
            ref_obj = ref_obj_node.get_ref_value()

            if type(ref_obj) == str:
                if ref_obj in self._SPECIAL_REF_OBJS:
                    ref_obj = self._SPECIAL_REF_OBJS[ ref_obj ]

            #method
            if eval_key_node.has_key( Key._METHOD_KEY ):
                
                method_node = eval_key_node.nodes[ Key._METHOD_KEY ]
                method_name_node = method_node.nodes[ Key._METHOD_NAME_KEY ]

                args = method_node.get_args()
                kwargs = method_node.get_kwargs()

                method_name_str = method_name_node.get_ref_value()

                try:
                    method_pointer = ref_obj.get_attr( method_name_str )
                except:
                    print ('ERROR')
                    print ('Could not find method ' + method_name_str + ' for ' + str(ref_obj))
                    print ('REF NODE: ' + str( ref_obj ))
                    print ('type: ' + str(type(ref_obj)))
                    assert False
                new_obj = method_pointer( *args, **kwargs )

            #attribute
            elif eval_key_node.has_key( Key._ATTRIBUTE_KEY ):
                attribute_node = eval_key_node.nodes[ Key._ATTRIBUTE_KEY ]
                new_obj = ref_obj.get_attr( attribute_node.get_ref_value() )

        # if $ref isn't found just return the node's value
        else:
            new_obj = eval_key_node.get_ref_value()

        # Do not add this Node to the parent's nodes, since we will only evaluate it once on runtime
        new_node = Node( key, parent=self.parent, value=new_obj )
        return new_node

    ### getting args, kwargs
    def get_args( self ):

        if Key._ARGS_KEY in self.nodes:
            args_node = self.nodes[ Key._ARGS_KEY ]
            return args_node.get_list( ref=True, eval=True )

        return []

    def get_kwargs( self ):
        
        if Key._KWARGS_KEY in self.nodes:
            kwargs_node = self.nodes[ Key._KWARGS_KEY ]
            return kwargs_node.get_dict( ref=True, eval=True )
        
        return {}

    def get_list( self, **kwargs ):

        default_kwargs = {
             "ref": True, 
             "eval":True
        }
        kwargs = ps.merge_dicts( default_kwargs, kwargs )

        og_list = self.get_raw_value()
        l = []

        for item in self.get_raw_value():

            self.set_value( item )
            l.append ( self.get_ref_value() )

        self.set_value( og_list )
        return l


    def get_dict( self, **kwargs ):

        ### Loading
        def load_dict( self, dict ):
            for key in dict:
                self.set_key( key, dict[key] )            

        default_kwargs = {
             "ref": True, 
             "eval":True
        }
        kwargs = ps.merge_dicts( default_kwargs, kwargs )

        d = {}

        #parent node
        for node_key in self.nodes:

            #!attr
            if Key.has_eval_code( node_key ) and kwargs['eval']:
                
                value = self.get_node( Key.strip_eval_code( node_key ), eval=kwargs['eval'] )
                d[Key.strip_eval_code( node_key )] = value.get_dict( **kwargs )

            #attr
            else:
                node = self.get_node( node_key, eval=kwargs['eval'] )
                value =  node.get_dict( **kwargs )

                d[ node_key ] = node.get_dict( **kwargs )

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
    def print_imp_atts( self, tab=0, ref=False, **override_kwargs ):
        
        default_kwargs = {'print_off': True}
        kwargs = ps.merge_dicts( default_kwargs, override_kwargs ) 

        string = ''
        string += '\t'*tab + self.key + '\n'
        for node in self:
            new_kwargs = kwargs.copy()
            new_kwargs['print_off'] = False
            string += node.print_imp_atts( tab=tab+1, ref=ref, **new_kwargs ) 
        
        value = self.get_value( ref=ref )
        if value != None:
            string += '\t'*(tab+1) + str(value) + '\n'

        return self.print_string( string, print_off = kwargs['print_off'] )
