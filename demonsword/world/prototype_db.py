"""
    Prototypes Database
    Reads TOML files for flavor text and related values for skills.
    Does not include skill mechanical data (exp, etc).
    
"""
import tomllib
from os import listdir
from copy import copy
import random
from util.random import randfloat
from evennia.prototypes.prototypes import create_prototype,load_module_prototypes
proto_proto = {
    "prototype_key":None#, "prototype_parent":None, "prototype_tags": [], "typeclass":None, "key":None,
}
proto_typing = {
    "prototype_key": str, "prototype_parent": str, "prototype_tags":list,"prototype_desc":str,"typeclass": str, "key": str, 
}
proto_proto_keys = [*proto_typing.keys()]

# Support the following TOML inline tables as callables:
# { "randint" = [min,max] }
# { "randrange" = [min,max] }
# { "choice" = ["a","b","c"] }
# { "choices" = [ ["a","b","c"], [10,80,10] ] # choices, weights
# For more options I'll need to implement protfuncs somewhere https://www.evennia.com/docs/0.9.5/Spawner-and-Prototypes.html#protfuncs 
proto_callables = {
    "randint":random.randint,"randfloat":randfloat,"choice":random.choice,"choices":random.choices
}
proto_callable_keys = [*proto_callables.keys()]

class PrototypeDB:
    """
    Prototypes database.
    """
    toml_dir = "world/prototypes"
    def __new__(cls):
        if not hasattr(cls,"instance"):
            cls.instance = super().__new__(cls)
        return cls.instance
    def __init__(self):
        self.loaded = []
        self.populate()
        
    def check_callable(self,d):
        if not isinstance(d,dict):
            return False
        i=d.items()
        if len(i) > 1 or len(i) == 0:
            return False
        t = [*i][0]
        if len(t) != 2:
            return False
        cname,cargs = t        
        if not isinstance(cname,str) or not isinstance(cargs,list):
            return False
        if not cname in proto_callable_keys:
            return False
        cname = proto_callables[cname]
        return (cname,*cargs)
        
    def is_callable(c):
        return isinstance(c,tuple) and len(c) == 2 and callable(c[0]) and isinstance(c[1],tuple)
        
    def validate(self, filen, key, incoming):
        for k,v in incoming.items():
            if not k in proto_proto_keys: # just an attribute.  Todo: sanity check key names?
                cal = self.check_callable(v)
                if cal:
                    #print(cal)
                    incoming[k]=cal
                continue
            # If we expect a scalar value and get a dict, we may have a callable            
            if not isinstance(v,proto_typing[k]):
                cal = self.check_callable(v)
                if cal == False:
                    raise ValueError(f"PrototypeDB.validate({filen},{key})[{k}] should be of type '{proto_typing[k]}' (was '{type(v)}')")
                incoming[k]=cal
        return True
        
    def populate(self):
        for f in listdir(self.toml_dir):
            if f[-5:].lower() != ".toml":
                continue
            self.loaded.append(f)
            with open(f"{self.toml_dir}/{f}","rb") as file:
                dat = tomllib.load(file)
                for k,v in dat.items():
                    if not isinstance(v,dict):
                        raise ValueError(f"PrototypeDB.populate({f}): Top level variable is not dict.")
                        continue
                    if self.validate(f,k,v):
                        v["prototype_key"]=k
                        #v["exec"]=["obj.at_post_spawn()"] #does get loaded but doesn't work?
                        load_module_prototypes(v)
                        self.loaded.append(f"> {k}")
