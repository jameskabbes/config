import py_seedlings as ps
from parent_class import ParentClass
import kabbes_config

class Base( ParentClass ):

    _ABS_REF_TRIGGER_BEG = '{{'
    _ABS_REF_TRIGGER_END = '}}'

    _LOCAL_REF_TRIGGER_BEG = '{R{'
    _LOCAL_REF_TRIGGER_END = '}R}'

    _ONE_LINE_ATTS = ['value']
    _IMP_ATTS = ['value']

    def __init__( self, Node, value ):
        ParentClass.__init__( self )
        self.Node = Node
        self.value = value

    def get_raw( self ):
        return self.value
    
    def set( self, value ):
        self.value = value

    def merge_ref( self, og_parents=[], new_parents=[] ):

        """when merging two Nodes, make sure the references point are remapped to the appropriate path"""

        if type(self.get_raw()) == str:

            formatted_nodes, ref_node_keys = self._get_ref_node_keys( abs=False,local=True )
            og_keys =  [ node.Key.key for node in og_parents  ]
            new_keys = [ node.Key.key for node in new_parents ]

            value = self.get_raw()

            for i in range(len(ref_node_keys)):
                
                node_keys = ref_node_keys[i].split( kabbes_config.key.Key._ATT_SPLIT )
                assert node_keys[:len(og_keys)] == og_keys

                rel_node_keys = node_keys[ len(og_keys): ]
                full_node_keys = new_keys + rel_node_keys

                new_key = self._LOCAL_REF_TRIGGER_BEG + kabbes_config.key.Key._ATT_SPLIT.join(full_node_keys) + self._LOCAL_REF_TRIGGER_END
                value = value.replace( formatted_nodes[i], new_key )

            self.set( value )

    def _get_ref_node_keys( self, abs:bool=True, local:bool=True ):
        
        formatted_nodes = []
        ref_node_keys = []

        if abs:
            new_formatted_nodes = ps.find_string_formatting( self.get_raw(), self._ABS_REF_TRIGGER_BEG, self._ABS_REF_TRIGGER_END )
            ref_node_keys.extend( [ ps.strip_trigger( formatted_node, self._ABS_REF_TRIGGER_BEG, self._ABS_REF_TRIGGER_END ) for formatted_node in new_formatted_nodes ] )
            formatted_nodes.extend( new_formatted_nodes )  

        if local:
            new_formatted_nodes = ps.find_string_formatting( self.get_raw(), self._LOCAL_REF_TRIGGER_BEG, self._LOCAL_REF_TRIGGER_END ) 
            ref_node_keys.extend( [ ps.strip_trigger( formatted_node, self._LOCAL_REF_TRIGGER_BEG, self._LOCAL_REF_TRIGGER_END ) for formatted_node in new_formatted_nodes ] )
            formatted_nodes.extend( new_formatted_nodes )  

        return formatted_nodes, ref_node_keys

    def get_ref( self ):
        
        # "{{repo.name}} {{repo.dir}}"
        if type(self.get_raw()) == str:

            formatted_nodes, ref_node_keys = self._get_ref_node_keys( abs=True,local=True )

            # ["repo.name", "repo.dir"]
            ref_node_values = {}
            for node_key in ref_node_keys:
                ref_node = self.Node.get_root().get_node( node_key )

                try:
                    #recursively find what string or object this {{value}} is referencing
                    ref_node_value = ref_node.get_ref_value()
                except:
                    print ('ERROR: could not find value for ref_obj')
                    print ('Node key: ' + str(node_key))
                    print ('Node: ' + str(ref_node))
                    assert False
                ref_node_values[ node_key ] = ref_node_value
            
            object_only=True
            if len(ref_node_keys) != 1:
                object_only = False
            else:
                if len(formatted_nodes[0]) != len(self.get_raw()):
                    object_only = False

            # can return an Object
            if object_only:
                return ref_node.get_ref_value()
            
            # with multiple Objects, we must turn them into string representations
            else:
                for node_key in ref_node_values:
                    ref_node_values[node_key] = str(ref_node_values[node_key])

                string = ps.smart_format( self.get_raw(), formatting_dict=ref_node_values, trigger_beg=self._ABS_REF_TRIGGER_BEG, trigger_end=self._ABS_REF_TRIGGER_END )
                string = ps.smart_format( string, formatting_dict=ref_node_values, trigger_beg=self._LOCAL_REF_TRIGGER_BEG, trigger_end=self._LOCAL_REF_TRIGGER_END )

                return string

        else:
            return self.get_raw()


