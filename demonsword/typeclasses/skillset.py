"""
    A skillset is a group of skills indexed by leading Aspect, and is the core
    functionality behind Stances, Roles, Occupation, and Proficiencies.
    Generally, a skillset has rules to limit the total number of skills you
    can be displaying across all active skillsets, based on skill advancement
    and associated aspect.
"""
from .attr_aspect import ValidStatIndex
from util.AttributeProperty import AttributeProperty,SubProperty

class SkillsetAttribute(AttributeProperty):
    _attr_get_source = lambda _, instance: instance.parent.attributes
    _key_get = lambda _,instance: instance.key
    _data_default = skill_default
    _category="skillsets"

class SkillSet:
    data = SkillsetAttribute({"locked":[],"loaded":{}},
    locked = SubProperty()
    loaded = SubProperty()
    
    def __init__(self, parent,key): # Parent
        self.parent = parent
        self.key = key
    def find(self,skill):
        for k,v in self.loaded:
            if v==None:
                continue
            if v == skill or (isinstance(v,list) and skill in v):
                return k
        return None
    def __contains__(self,index):
        if isinstance(index,str):
    def __getitem__(self,index:str):
        if index in ValidStatIndex:
            return loaded[index] if index in loaded else None
        skill = self.parent.skills[index]
        #if skill in loaded.
    pass

class Stance(SkillSet):
    pass
class Occupation(SkillSet):
    pass
class Role(SkillSet):
    pass