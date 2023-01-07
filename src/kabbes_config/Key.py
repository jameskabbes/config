from parent_class import ParentClass

class Key( ParentClass ):

    """keys are evaluated, values are referenced"""

    _EVAL_CODE = '!'
    _ATT_SPLIT = '.'
    _EVAL_CODE = '!'
    _REF_OBJ_KEY = '$ref'

    _METHOD_KEY = 'method'
    _ATTRIBUTE_KEY = 'attribute'
    _METHOD_NAME_KEY = 'name'
    _ARGS_KEY = 'args'
    _KWARGS_KEY = 'kwargs'

    @classmethod
    def has_eval_code( cls, key: str ) -> bool:
        """returns whether a key starts with the eval code"""

        return key.startswith( cls._EVAL_CODE )

    @classmethod
    def strip_eval_code( cls, key: str ) -> str:
        """strips the eval code from the beginning of the key"""

        return key[ len(cls._EVAL_CODE) :  ]

    @classmethod
    def add_eval_code( cls, key: str ) -> str:
        """adds the eval code to the beginning of the key"""

        return cls._EVAL_CODE + key

    @classmethod
    def split_key( cls, key: str ):
        """returns a list of strings split by the _ATT_SPLIT"""

        return key.split( cls._ATT_SPLIT )

    @classmethod
    def chop_off_head( cls, key: str ):
        """chop off at the first split, return the rest"""
        list = key.split( cls._ATT_SPLIT )
        return list[0], cls._ATT_SPLIT.join( list[1:] )


