from parent_class import ParentClass
import kabbes_config
import dir_ops as do
import py_starter as ps

class Config( ParentClass ):

    _DO_NOT_PRINT = ['type','Parent']
    _DO_NOT_CHECK = ['type','Parent']
    _TRIGGER_BEG = '{{'
    _TRIGGER_END = '}}'
    _REF_OBJ_KEY = '$ref'
    _EVAL_CODE = '!'
    _ATT_SPLIT = '.'
    _METHOD_KEY = 'method'
    _ATTRIBUTE_KEY = 'attribute'
    _METHOD_NAME_KEY = 'name'
    _ARGS_KEY = 'args'
    _KWARGS_KEY = 'kwargs'

    def __init__( self, Parent=None, **kwargs ):

        ParentClass.__init__( self )
        self.Parent = Parent
        self.load_dict( kwargs )

    def set_attr(self, att: str, val):

        self.__dict__[ att ] = val

    def has_attr( self, att: str, get=True, use_ref=False ):

        nested = Config.split_att( att )
        first_level = nested[0]

        if first_level in self.__dict__:
            if len(nested) > 1:

                next_levels = self._ATT_SPLIT.join(nested[1:])
                return self.__dict__[ first_level ].get_attr( next_levels, use_ref=use_ref ) 

            else:
                if get:
                    if use_ref:
                        val = self.check_ref( self.get_attr(first_level) )
                    else:
                        val =  self.__dict__[ first_level ]

                if not get:
                    return True

        else:
            val = None
            if not get:
                return False

        if get:
            return val            

    def get_attr( self, att: str, use_ref=False ):

        """given an attribute, return the value
        att.nest1.nest2 will return the value of att[nest1][nest2]
        """

        return self.has_attr( att, get = True, use_ref=use_ref )
    
    def load_key_value( self, key, value):

        nested = Config.split_att( key )
        first_level = nested[0]

        if len(nested[1:]) > 0: #given a nested a.b.c value
            value_to_set = Config( Parent = self, **{self._ATT_SPLIT.join(nested[1:]) : value})

        else:
            if isinstance(value, dict):
                value_to_set = Config( Parent = self, **value)
            else:
                value_to_set = value

        self.set_attr( first_level, value_to_set )
        self.check_eval( first_level )


    def get_head( self ):

        """find the Head of all Configs"""

        config_obj = self
        while config_obj.Parent != None:
            config_obj = config_obj.Parent
        
        return config_obj

    def get_dict( self, use_ref=False ):

        d = self.__dict__.copy()
        for att in Config._DO_NOT_CHECK:
            del d[ att ]

        if use_ref:
            for key in d:
                d[ key ] = self.get_attr( key, use_ref=use_ref )

        return d

    @classmethod
    def split_att( cls, att ):

        """split up a string '1.2.3' into ['1','2','3']"""
        return att.split( cls._ATT_SPLIT )

    def load_dict( self, d: dict ):

        """load the dictionary, overwrite all previous keys"""

        for key, value in d.items():
            self.load_key_value( key, value )

    def check_ref( self, value ):

        if type(value) == str:
            stripped_atts = ps.find_string_formatting( value, Config._TRIGGER_BEG, Config._TRIGGER_END )
            ref_obj_atts = [ ps.strip_trigger( stripped_att, Config._TRIGGER_BEG, Config._TRIGGER_END ) for stripped_att in stripped_atts ]

            ref_atts_and_values = {}
            for att in ref_obj_atts:
                ref_obj = self.check_ref( self.get_head().get_attr( att ) )
                ref_atts_and_values[ att ] = ref_obj

            object_only=True
            if len(stripped_atts) != 1:
                object_only = False
            else:
                if len(stripped_atts[0]) != len(value):
                    object_only = False

            # can return an Object
            if object_only:
                return ref_atts_and_values[ att ]
            
            # with multiple Objects, we must turn them into string representations
            else:
                for key in ref_atts_and_values:
                    ref_atts_and_values[key] = str(ref_atts_and_values[key])
                return ps.smart_format( value, formatting_dict=ref_atts_and_values, trigger_beg=Config._TRIGGER_BEG, trigger_end=Config._TRIGGER_END )

        return value

    def get_args( self ):
        
        if self.has_attr( Config._ARGS_KEY ):
            args = self.get_attr( Config._ARGS_KEY )
            for i in range(len(args)):
                args[i] = self.check_ref( args[i] )
            
            return args

        return []

    def get_kwargs( self ):

        if self.has_attr( Config._KWARGS_KEY ):
            
            kwargs = self.get_attr( Config._KWARGS_KEY )

            #kwargs is a Config object
            return kwargs.get_dict( use_ref=True )
        
        return {}

    def reevaluate( self ):
        
        for key in self.get_dict():
            value = self.get_attr(key)
            if isinstance( value, Config ):
                value.reevaluate()

            self.check_eval( key )


    def check_eval( self, att: str ):

        if Config._EVAL_CODE in att:
            att_config = self.get_attr( att )  

            #looking for $ref
            if att_config.has_attr( Config._REF_OBJ_KEY ):
                
                #get ref Config obj
                ref = self.check_ref( att_config.get_attr( Config._REF_OBJ_KEY) )

                # method
                if att_config.has_attr( Config._METHOD_KEY ):
                    method_config = att_config.get_attr( Config._METHOD_KEY )
                    
                    args = method_config.get_args()
                    kwargs = method_config.get_kwargs()

                    method_pointer = ref.get_attr( method_config.get_attr( Config._METHOD_NAME_KEY ) ) 
                    new_obj = method_pointer( *args, **kwargs )

                #attribute
                if att_config.has_attr( Config._ATTRIBUTE_KEY ):
                    new_obj = ref.get_attr( att_config.get_attr( Config._ATTRIBUTE_KEY ) )

            self.set_attr( att.replace( self._EVAL_CODE, '' ), new_obj )

    def print_imp_atts(self, tab=0, **override_kwargs):

        """print off an overview of the Settings __dict__ with tabbed out increments"""

        default_kwargs = {'print_off': True}
        kwargs = ps.merge_dicts( default_kwargs, override_kwargs ) 

        string = ''
        for key in self.__dict__:
            if key not in self._DO_NOT_PRINT:
                string += '\t'*tab + key + '\n'
                value = self.get_attr( key, use_ref=False )

                if not isinstance( value, Config ):
                    string += '\t'*(tab+1)+str(value) + '\n'
                else:
                    new_kwargs = kwargs.copy()
                    new_kwargs['print_off'] = False
                    string += value.print_imp_atts( tab=tab+1, **new_kwargs )

        return self.print_string( string, print_off = kwargs['print_off'] )


