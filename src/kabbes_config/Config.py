from parent_class import ParentClass
import py_starter as ps
import dir_ops as do

class Config( ParentClass ):

    _ATT_SPLIT = '.'
    _EVAL_CODE = '!'
    _REF_TRIGGER_BEG = '{{'
    _REF_TRIGGER_END = '}}'
    _REF_OBJ_KEY = '$ref'

    _METHOD_KEY = 'method'
    _ATTRIBUTE_KEY = 'attribute'
    _METHOD_NAME_KEY = 'name'
    _ARGS_KEY = 'args'
    _KWARGS_KEY = 'kwargs'

    _SPECIAL_REF_OBJS = {
        "$Dir": do.Dir()
    }

    def __init__( self, key, parent=None, value = None, **dict ):

        ParentClass.__init__( self )
        self.key = key
        self.parent = parent
        self.value = value
        self.children = {}
        self.load_dict( dict )

    def __contains__( self, key ):
        return key in self.children

    def load_dict( self, dict ):

        for key in dict:
            self.set_attr( key, dict[key] )            

    def make_Child( self, *args, **kwargs ):

        child_Config = Config( *args, **kwargs, parent=self )
        self.children[ child_Config.key ] = child_Config
        return child_Config

    def chop_off_attr_head( self, attr ):
        nested = attr.split( self._ATT_SPLIT )
        return nested[0], self._ATT_SPLIT.join(nested[1:])

    def set_value( self, value ):
        self.value = value
        self.children = []

    def get_value( self, ref=True ):
        if ref:
            return self.get_ref_value()
        else:
            return self.get_raw_value()

    def get_ref_value( self ):

        # "{{repo.name}} {{repo.dir}}"
        if type(self.value) == str:
            stripped_atts = ps.find_string_formatting( self.value, self._REF_TRIGGER_BEG, self._REF_TRIGGER_END )
            ref_obj_atts = [ ps.strip_trigger( stripped_att, self._REF_TRIGGER_BEG, self._REF_TRIGGER_END ) for stripped_att in stripped_atts ]

            # ["repo.name", "repo.dir"]
            ref_atts_and_values = {}
            for att in ref_obj_atts:
                print (att)
                ref_obj = self.get_root().get_node( att ).get_ref_value()
                ref_atts_and_values[ att ] = ref_obj
            
            object_only=True
            if len(stripped_atts) != 1:
                object_only = False
            else:
                if len(stripped_atts[0]) != len(self.value):
                    object_only = False

            # can return an Object
            if object_only:
                return ref_atts_and_values[ att ]
            
            # with multiple Objects, we must turn them into string representations
            else:
                for key in ref_atts_and_values:
                    ref_atts_and_values[key] = str(ref_atts_and_values[key])
                return ps.smart_format( self.value, formatting_dict=ref_atts_and_values, trigger_beg=self._REF_TRIGGER_BEG, trigger_end=self._REF_TRIGGER_END )

        else:
            return self.value

    def get_raw_value( self ):
        return self.value

    def get_node( self, attr: str, **kwargs ):

        """level1.level2.level3"""
        default_kwargs = {
            "make": False,
            "eval": True
        }
        kwargs = ps.merge_dicts( default_kwargs, kwargs )

        ###
        head, body = self.chop_off_attr_head( attr )

        if head == '':
            return self
        if head in self.children:
            return self.children[ head ].get_node( body, **kwargs )
        if head not in self.children:
            
            if (self._EVAL_CODE + head) in self.children and kwargs['eval']:
                return self.eval( attr ).get_node( body, **kwargs )

            elif kwargs['make']:
                self.make_Child( head )
                return self.children[ head ].get_node( body, **kwargs )
        return None

    def set_attr( self, attr: str, value ):

        node = self.get_node( attr, make=True, eval=False )
        if isinstance( value, dict ):
            node.load_dict( value )
        else:
            node.set_value( value )

    def has_attr( self, attr: str ):
        
        node = self.get_node( attr, make=False, eval=False)
        return node != None

    def get_attr( self, attr: str, ref=True ):

        node = self.get_node( attr, make=False, eval=True)
        if node != None:
            return node.get_value( ref=ref )
        return None

    def get_ref_attr( self, attr: str):
        return self.get_attr( attr, ref=True )
    def get_raw_attr( self, attr: str ):
        return self.get_attr( attr, ref=False )
    
    def get_dict( self, ref=True ):

        d = {}
        for key in self.children:
            d[ key ] = self.children[ key ].get_dict( ref=ref )
        if self.value != None:
            return self.get_value( ref=ref )

        return d 

    def get_args( self ):

        if self._ARGS_KEY in self.children:
            args_node = self.children[ self._ARGS_KEY ]
            args =  args_node.get_raw_value()

            for i in range(len(args)):
                self.value = args[i]
                self.get_ref_value()
                args[i] = self.value

            return args
        return []

    def get_kwargs( self ):

        if self._KWARGS_KEY in self.children:
            kwargs_node = self.children[ self._KWARGS_KEY ]
            return kwargs_node.get_dict()
       
        return {}

    def eval( self, attr: str ):

        joined_attr = self._EVAL_CODE + attr

        if self.has_attr( joined_attr ):
            attr_node = self.children[ joined_attr ]

            if attr_node.has_attr( self._REF_OBJ_KEY ):
                ref_obj_node = attr_node.children[ self._REF_OBJ_KEY ]

                ref_obj = ref_obj_node.get_ref_value()
                if type(ref_obj) == str:
                    if ref_obj in self._SPECIAL_REF_OBJS:
                        ref_obj = self._SPECIAL_REF_OBJS[ ref_obj ]

                #method
                if attr_node.has_attr( self._METHOD_KEY ):
                    method_node = attr_node.children[ self._METHOD_KEY ]
                    method_name_node = method_node.children[ self._METHOD_NAME_KEY ]

                    args = method_node.get_args()
                    kwargs = method_node.get_kwargs()

                    method_pointer = ref_obj.get_attr( method_name_node.get_ref_value() )
                    new_obj = method_pointer( *args, **kwargs )

                if attr_node.has_attr( self._ATTRIBUTE_KEY ):
                    new_obj = ref_obj.get_attr( attr_node.get_ref_value( self._ATTRIBUTE_KEY ) )

            new_node = Config( attr, parent=self.parent, value=new_obj )
            return new_node
        return None

    def get_root( self ):

        """get the highest point of the config tree"""

        node = self
        while node.parent != None:
            node = node.parent
        
        return node

    def print_imp_atts( self, tab=0, ref=False, **override_kwargs ):
        
        default_kwargs = {'print_off': True}
        kwargs = ps.merge_dicts( default_kwargs, override_kwargs ) 

        string = ''
        string += '\t'*tab + self.key + '\n'
        for key in self.children:
            new_kwargs = kwargs.copy()
            new_kwargs['print_off'] = False
            string += self.children[key].print_imp_atts( tab=tab+1, ref=ref, **new_kwargs ) 
        
        if self.value != None:
            string += '\t'*(tab+1) + str(self.get_value(ref=ref)) + '\n'

        return self.print_string( string, print_off = kwargs['print_off'] )

class RootConfig( Config ):

    def __init__( self, **kwargs ):
        Config.__init__( self, 'config', parent=None, value=None, **kwargs )





