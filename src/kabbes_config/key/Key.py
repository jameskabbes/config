from parent_class import ParentClass
import dir_ops as do
import kabbes_config

class Key( ParentClass ):

    """keys are evaluated, values are referenced"""

    _EVAL_CODE = '!'
    _ATT_SPLIT = '.'
    _REF_OBJ_KEY = '$ref'

    _METHOD_KEY = 'method'
    _ATTRIBUTE_KEY = 'attribute'
    _METHOD_NAME_KEY = 'name'

    _ONE_LINE_ATTS = ['key']
    _IMP_ATTS = ['key']

    _SPECIAL_REF_OBJS = {
        "$Dir": do.Dir()
    }

    def __init__( self, Node, key ):
        ParentClass.__init__( self )
        self.Node = Node
        self.key = key

    def has_eval_code( self ) -> bool:
        """returns whether a key starts with the eval code"""
        return self.key.startswith( self._EVAL_CODE )

    def strip_eval_code( self ) -> str:
        """strips the eval code from the beginning of the key"""
        return self.key[ len(self._EVAL_CODE) :  ]

    def add_eval_code( self ) -> str:
        """adds the eval code to the beginning of the key"""
        return self._EVAL_CODE + self.key

    def split( self ):
        """returns a list of strings split by the _ATT_SPLIT"""
        return self.key.split( self._ATT_SPLIT )

    def chop_off_head( self ):
        """chop off at the first split, return the rest"""
        list = self.key.split( self._ATT_SPLIT )
        return list[0], self._ATT_SPLIT.join( list[1:] )

    ### evaluate.!this 
    def eval( self ):
        
        """This will only be called if the Node Key has ! in it"""

        # if $ref is found under the node
        if self.Node.has_key( self._REF_OBJ_KEY ):

            # $ref
            ref_obj_node = self.Node.nodes[ self._REF_OBJ_KEY ]
            ref_obj = ref_obj_node.get_ref_value()

            if type(ref_obj) == str:
                if ref_obj in self._SPECIAL_REF_OBJS:
                    ref_obj = self._SPECIAL_REF_OBJS[ ref_obj ]

            #method
            if self.Node.has_key( self._METHOD_KEY ):
                
                method_node = self.Node.nodes[ self._METHOD_KEY ]
                method_name_node = method_node.nodes[ self._METHOD_NAME_KEY ]

                args = method_node.get_args()
                kwargs = method_node.get_kwargs()

                method_name_str = method_name_node.Value.get_ref()

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
            elif self.Node.has_key( self._ATTRIBUTE_KEY ):
                attribute_node = self.Node.nodes[ self._ATTRIBUTE_KEY ]
                new_obj = ref_obj.get_attr( attribute_node.get_ref() )

        # if $ref isn't found just return the node's value
        else:
            new_obj = self.Node.get_ref()

        # Do not add this Node to the parent's nodes, since we will only evaluate it once on runtime
        new_node = kabbes_config.Node( self.key, parent=self.Node.parent, value=new_obj )
        return new_node