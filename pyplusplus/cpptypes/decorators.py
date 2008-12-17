class public( object ):
    def __init__(self ,  dll,  decorated_name,  return_type,  argumen_types):
        self.decorated_name = decorated_name
        self.func = getattr( dll,  decorated_name )
        self.func.restype = return_type
        self.func.argtypes = argumen_types

    def __call__(self, *args, **keywd ):
        return self.func( *args,  **keywd )
