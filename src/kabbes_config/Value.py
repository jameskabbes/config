from parent_class import ParentClass
import py_starter as ps

class Value( ParentClass ):

    _REF_TRIGGER_BEG = '{{'
    _REF_TRIGGER_END = '}}'

    def __init__( self, Node, value ):
        self.Node = Node
        self.value = value

    def set( self, value ):
        self.value = value

    def get( self, ref=True ):
        if ref:
            return self.get_ref()
        else:
            return self.get_raw()

    def get_raw( self ):
        return self.value

    def get_ref( self ):
        
        # "{{repo.name}} {{repo.dir}}"
        if type(self.value) == str:

            formatted_nodes = ps.find_string_formatting( self.value, self._REF_TRIGGER_BEG, self._REF_TRIGGER_END )
            ref_node_keys = [ ps.strip_trigger( formatted_node, self._REF_TRIGGER_BEG, self._REF_TRIGGER_END ) for formatted_node in formatted_nodes ]

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
                if len(formatted_nodes[0]) != len(self.value):
                    object_only = False

            # can return an Object
            if object_only:
                return ref_node.get_ref_value()
            
            # with multiple Objects, we must turn them into string representations
            else:
                for node_key in ref_node_values:
                    ref_node_values[node_key] = str(ref_node_values[node_key])
                return ps.smart_format( self.value, formatting_dict=ref_node_values, trigger_beg=self._REF_TRIGGER_BEG, trigger_end=self._REF_TRIGGER_END )

        else:
            return self.value

