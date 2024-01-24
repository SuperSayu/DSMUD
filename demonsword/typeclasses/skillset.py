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
    active = False
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
    def ident(self):
        return f"{self.key} {self.category}"
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
        old = None
        if aspect in self.loaded:
            if aspect in self.locked:
                self.parent.msg(f"Aspect is locked: {aspect}")
                return
            old = self.loaded[aspect]
            if skill == None:
                del self.loaded[aspect]
                self.onEdit(aspect,None,old)
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
        self.onEdit(aspect,skill,old)
                
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
    def onEquipped(self):
        self.active = True
        for asp,x in self.loaded.items():
            self.onActivateSkill(asp,x)
        pass
    def onUnequipped(self):
        self.active = False
        for asp,x in self.loaded.items():
            self.onDeactivateSkill(asp,x)
        pass
    def onActivateSkill(self,aspect,skill):
        return
    def onDeactivateSkill(self,aspect,skill):
        return
    def onBeforeSetSkill(self,aspect,newSkill):
        # for jobs and roles this should refuse if a skill is in a complementary set
        # you only need one to qualify as passive
        if aspect in self.locked:
            return False
        if self.loaded[aspect] != newSkill and self.find(newSkill):
            return False
        return True
        
    def onEdit(self,aspect,newSkill,oldSkill):
        if not oldSkill and not newSkill:
            self.parent.msg("Nothing to do")
            return
        if aspect in self.locked:
            self.parent.msg("Aspect is locked")
            return
        if oldSkill and not newSkill:
            if self.active:
               self.onDeactivateSkill(aspect,oldSkill)
            self.parent.msg(f"Cleared aspect {aspect}.")
            return
        if oldSkill:
            if self.active:
                self.onDeactivateSkill(aspect,oldSkill)
                self.onActivateSkill(aspect,newSkill)
            self.parent.msg(f"Replaced skill {oldSkill} with skill {newSkill} for aspect {aspect}.")
        else:
            if self.active:
                self.onActivateSkill(aspect,newSkill)
            self.parent.msg(f"Slotted skill {newSkill} into aspect {aspect}.")

# Stance skillset: what you are doing at any moment, can change fairly freely, unrestrained
class Stance(SkillSet):
    category="stance"
    def onActivateSkill(self,aspect,skill):
        s = self.parent.skills[skill]
        s.aspect = aspect
        s.stance = self.key
    def onDeactivateSkill(self,aspect,skill):
        s = self.parent.skills[skill]
        s.aspect = None
        s.stance = None

# job skillset: What you do for a living, change only on rest, some restrictions
class Job(SkillSet):
    category="job"
    def onActivateSkill(self,aspect,skill):
        s = self.parent.skills[skill]
        s.job = self.key
    def onDeactivateSkill(self,aspect,skill):
        s = self.parent.skills[skill]
        s.job = None
# Role skillset: What you do in combat, change only on rest, some restrictions
class Role(SkillSet):
    category="role"
    def onActivateSkill(self,aspect,skill):
        s = self.parent.skills[skill]
        s.role = self.key
    def onDeactivateSkill(self,aspect,skill):
        s = self.parent.skills[skill]
        s.role = None
