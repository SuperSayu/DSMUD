"""
    Skills Database
    Reads TOML files for flavor text and related values for skills.
    Does not include skill mechanical data (exp, etc).
    
"""
import tomllib
from os import listdir
from copy import copy
skill_proto = {
    "key":None, "name":None, "doing":None, "desc":"No skill description given.", "tags":[], "stat":"luc"
}
skill_typing = {
    "key": str, "name": str, "doing": str, "desc": str, "tags":list, "stat":str
}
skill_proto_keys = [*skill_proto.keys()]

class SkillDB:
    """
    Skills database.
    """
    toml_dir = "world/skills"
    def __new__(cls):
        if not hasattr(cls,"instance"):
            cls.instance = super().__new__(cls)
        return cls.instance
    def __init__(self):
        self.populated = False
        self.db = None
        self.loaded = []
        self.faked = []
    def __contains__(self,key):
        if not self.populated:
            self.populate()
        return key in self.db
        
    def validate(self, filen, key, incoming):
        for k,v in incoming.items():
            if not k in skill_proto_keys:
                raise KeyError(f"SkillDB.validate({filen},{key}): key '{k}' is not valid")
            if not isinstance(v,skill_typing[k]):
                raise ValueError(f"SkillDB.validate({filen},{key})[{k}] should be of type '{skill_typing[k]}' (was '{type(v)}')")
        return True
    def populate(self):
        self.db = {}
        for f in listdir(self.toml_dir):
            if f[-5:].lower() != ".toml":
                continue
            self.loaded.append(f)
            with open(f"{self.toml_dir}/{f}","rb") as file:
                dat = tomllib.load(file)
                
                for k,v in dat.items():
                    if not isinstance(v,dict):
                        raise ValueError(f"SkillDB.populate({f}): Top level variable is not dict.")
                        continue
                    if self.validate(f,k,v):
                        self.db[k] = self.factory(k,**v)
                        self.loaded.append(f"> {k}")
        self.populated = True
    @classmethod
    def factory(cls,key,**kwargs):
        """
        Factory for creating new entries, not including syncing them with
        stored information from a character's Evennia attributes.
        At present, this is very basic and uninteresting.
        """
        if not isinstance(key,str) or key == "":
            raise ValueError(f"SkillDB Factory: key string cannot be empty")
        template = copy(skill_proto)
        template["key"] = key
        for k,v in kwargs.items():
            if not k in skill_proto_keys:
                raise KeyError(f"Skill template does not have key {k}")
            template[k]=v
        return template
    def __getitem__(self,index):
        if not self.populated:
            self.populate()
        if not index in self.db:
            self.faked.append(index)
            temp = self.factory(index,name=index,doing=str(index)+"ing",desc="Work in progress - Standby")
            self.db[index]=temp
            return temp
        return self.db[index]
