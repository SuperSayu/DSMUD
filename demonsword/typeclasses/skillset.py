"""
    A skillset is a group of skills indexed by leading Aspect, and is the core
    functionality behind Stances, Roles, job, and Proficiencies.
    Generally, a skillset has rules to limit the total number of skills you
    can be displaying across all active skillsets, based on skill advancement
    and associated aspect.
"""
from .attr_aspect import Aspect,AspectList
from .skills import Skill
from util.AttributeProperty import RemoteAttributeProperty,SubProperty

skillset_default = {"key":None,"slots":1,"locked":[],"loaded":{}}
class SkillsetAttribute(RemoteAttributeProperty):
    _key_get = lambda _,instance: instance.key
    _data_default = skillset_default
    _category_get=lambda _s,parent,_a,_k: parent.category

class SkillSet:
    """
    Skillsets are string mappings to find out what skills are currently active.
    """
    parent = None
    category="skillset"
    data = SkillsetAttribute(skillset_default)
    slots  = SubProperty()
    locked = SubProperty()
    loaded = SubProperty()
    
    def __init__(self, parent,key): # Parent: character
        self.parent = parent
        self.key = key
        self.data["key"]=key # don't want to reuse varname here
    def __str__(self):
        return str(self.data)
    def find(self,skill):
        for k,v in self.loaded.items():
            if v==None:
                continue
            if v == skill:
                return k
        return None
    def __contains__(self,index):
        return self.find(index)
    def __getitem__(self,index:str):
        if index in AspectList:
            return loaded[index] if index in loaded else None
        skill = self.parent.skills[index]
    def SetSkill(self,aspect,skill):
        if isinstance(aspect,Aspect):
            aspect = aspect.key
        elif not aspect in AspectList:
            raise ValueError(f"Not an aspect: {aspect}")
        if aspect in self.loaded:
            if aspect in self.locked:
                self.parent.msg(f"Aspect is locked: {aspect}")
                return
            if skill == None:
                del self.loaded[aspect]
                self.parent.msg(f"Cleared aspect {aspect}.")
                return
            if isinstance(skill,Skill):
                skill = skill.key
            if self.loaded[aspect] != skill and self.find(skill):
                self.parent.msg(f"Skill is already slotted in a different aspect.")
                return
        elif len(self.loaded) >= self.slots:
            self.parent.msg("No remaining slots")
            return
        self.loaded[aspect]=skill
        self.parent.msg(f"Slotted skill {skill} into aspect {aspect}")
                
    def LockAspect(self,aspect):
        if isinstance(aspect,Aspect):
            aspect = aspect.key
        if not aspect in AspectList:
            raise ValueError(f"Not an aspect: {aspect}")
        if aspect in self.locked:
            self.locked.remove(aspect)
            self.parent.msg(f"Unlocked aspect {aspect}")
        else:
            self.locked.append(aspect)
            self.parent.msg(f"Locked aspect {aspect}")
    pass

# Stance skillset: what you are doing at any moment, can change fairly freely, unrestrained
class Stance(SkillSet):
    category="stance"
    pass
# job skillset: What you do for a living, change only on rest, some restrictions
class Job(SkillSet):
    category="job"
    pass
# Role skillset: What you do in combat, change only on rest, some restrictions
class Role(SkillSet):
    category="role"
    pass