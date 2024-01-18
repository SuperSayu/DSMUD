"""
    The skillcore is a central facility for characters to attempt difficult tasks
    and grow with their success and failure.
    
    The skillcore does not handle translating actions into skill rolls.  That is the
    action core, which takes input from equipment and magical effects.
    
    Use the skills category for all named attributes
    
    The DSP skill advancement system includes gains and losses and takes more and more effort
    as you go up in skill.
"""
from util.random import roll
from .skills import Skill
from typing import Union,Generator
from util.AttributeProperty import RemoteAttributeProperty
from .skillset import Stance,Job,Role

class SkillCore:
    """
        A character SkillCore is the central point for asking the character to roll a skill check.
        It will also handle advancement when the character rests.
    """
    parent      = None
    # Active skillsets
    _stance      = RemoteAttributeProperty(None,key="stance")
    stance = None
    _job  = RemoteAttributeProperty(None,key="job")
    job = None
    _role        = RemoteAttributeProperty(None,key="role")
    role = None

    # Set to a skill if you are currently doing a thing.  This is a temporary measure.
    # I am pretty sure the mechanic behind this will go away soon.
    training    = None
    populated   = False
    # The cached skills, these can be accessed with the skillcore get[] instead
    skills      = {}
    skillsets   = {"stance":{},"job":{},"role":{}}
    
    def __init__(self,parent):
        self.parent=parent
        self.normalize()
    def __contains__(self,key) -> bool:
        return True
    def __getitem__(self, key) -> Skill:
        """
            Returns the requested skill (as the class Skill).
            If no such skill exists, a new Skill will be created.
        """
        if key in self.skills:
            return self.skills[key]
        temp = Skill(self.parent,key)
        self.skills[key] = temp
        return temp
    def __delitem__(self,key):
        if key in self.skills:
            del self.skills[key]
        self.parent.attributes.remove(key,category="skills")
        
    def __str__(self):
        """
            Debug/Temporary: Formal all skills into a simple list.
        """
        result=f"|CSkill Name |||n  exp  |C|||n  EV   |C|||n Stat  |C|||n  eff\u25b3 |C|||n  trn\u25ca |C|||n  aff\u25c8 |C|||n  mas\u25cc|/|C------------------------------------------------------------------|n|/"
        for skill in self.parent.attributes.all(category="skills"):
            result += self[skill.key].__str__() + "|/"
        return result
    
    def __iter__(self):
        """
            Allow using the skill core as a generator for the character's skills.
        """
        yield from self.All()
    
    def __len__(self):
        """
            Returns the total number of skills for this character.
        """
        if not self.populated:
            self.populate()
        return len(self.skills)
    def skillset_exists(self,key,stype="stance"):
        if not stype in ["stance","job","role"]:
            raise IndexError(f"get_skillset: invalid stype {stype}")
        return self.parent.attributes.has(key=key,category=stype)
    def rename_skillset(self,oldkey,newkey, stype="stance"):
        if not self.skillset_exists(oldkey):
            return
        if self.skillset_exists(newkey):
            return
        active = self.active_skillset(stype)
        if active != None:
            active = active.key
        # Get rid of the pythonic data structure so we can deal with the evennia attribute
        del self.skillsets[stype][oldkey]
        attr=self.parent.attributes.get(key=oldkey,category=stype)
        attr.key = newkey
        self.parent.attributes.add(newkey,attr,category=stype)
        self.parent.attributes.remove(key=oldkey,category=stype)
        if active == oldkey:
            self.activate_skillset(newkey,stype)
        self.parent.msg(f"Renamed {stype} '{oldkey}' to '{newkey}'")
            
    def get_skillset(self, key, stype="stance"):
        if not stype in ["stance","job","role"]:
            raise IndexError(f"get_skillset: invalid stype {stype}")
        if not key in self.skillsets[stype]:
            generators = {"stance":Stance,"job":Job,"role":Role}
            temp = generators[stype](self.parent,key)
            self.skillsets[stype][key]=temp
            return temp
        return self.skillsets[stype][key]
    def active_skillset(self,stype="stance"):
        match stype:
            case 'stance':
                return self.stance
            case 'job':
                return self.job
            case 'role':
                return self.role
            case _:
                raise ValueError(f"Bad skillset type {stype}")
    def del_skillset(self,key,stype="stance"):
        if not stype in ["stance","job","role"]:
            raise IndexError(f"get_skillset: invalid stype {stype}")
        if self.skillset_exists(key,stype):
            if key in self.skillsets[stype]:
                del self.skillsets[stype][key]
            
            if key == getattr(self,f"_{stype}"):
                setattr(self,f"_{stype}",None)
                setattr(self,stype,None)
                self.parent.attributes.remove(key=key,category=stype)
                self.parent.msg(f"Deactivated and removed {stype} {key}.")
                self.normalize()
            else:
                self.parent.attributes.remove(key=key,category=stype)
                self.parent.msg(f"Removed {stype} {key}")
        else:
            self.parent.msg(f"{stype.capitalize()} {key} does not exist.")
        
    def activate_skillset(self,skillset,stype="stance",quiet=False):
        if not stype in ["stance","job","role"]:
            raise ValueError(f"activate_skillset: Invalid skillset type '{stype}'")
        if skillset == "" or skillset == None:
            setattr(self,f"_{stype}",None)
            setattr(self,stype,None)
            self.normalize()
            return
        if isinstance(skillset,str):
            if not self.skillset_exists(skillset,stype):
                if not quiet:
                    self.parent.msg(f"Not activating missing {stype} {skillset}")
                return
            skillset = self.get_skillset(skillset,stype)
        setattr(self,f"_{stype}",skillset.key)
        setattr(self,stype,skillset)
        if not quiet:
            self.parent.msg(f"Activated {stype} {skillset.key}")
    def normalize(self):
        """
            Internal: Make sure skillsets etc are in a sane configuration
        """
        if self._stance == None:
            self.get_skillset("main",'stance') # activate will not create one if it doesn't exist, but get will.
            self.activate_skillset("main",'stance',quiet=True)
            return
        if self.stance == None:
            self.activate_skillset(self._stance or list(self.skillsets["stance"].keys())[0],quiet=True)
            if self.stance == None:
                self.get_skillset("main",'stance') # activate will not create one if it doesn't exist, but get will.
                self.activate_skillset("main",'stance',quiet=True)                
        return
    def populate(self):
        """
            Internal: Finish lazy-loading all skills from their Evennia attributes.
        """
        if self.populated:
            return
        for skill in self.parent.attributes.all(category="skills"):
            if not (skill.key in self.skills):
                self.skills[skill.key] = Skill(self.parent,skill.key)#,data=skill.value)
        generators = {"stance":Stance,"job":job,"role":Role}
        for stype in ["stance","job","role"]:
            for skillset in self.parent.attributes.all(category=stype):
                if not skillset.key in self.skillsets[stype]:
                    self.skillsets[stype][skillset.key] = generators[stype](self.parent,skillset.key)
        self.populated = True
    
    def show(self,selected:Union[str,list[str]]=None):
        """
            Temporary: Show one, a subset, or all skills to the user in a simple list.
        """
        if(selected != None):
            if not self.parent.attributes.has(selected,category="skills"):
                self.parent.msg(f"You have no {selected} skill.")
                return
            self.parent.msg("|CSkill Name |||n  exp  |C|||n  eff\u25b3 |C|||n  trn\u25ca |C|||n  aff\u25c8 |C|||n  mas\u25cc|/|C----------------------------------------------------|n|/")
            if type(selected) is list:
                for s in selected:
                    self.parent.msg(self[s].__str__())
                    self.parent.msg("|/"+self[s].desc)
            else:
                self.parent.msg(self[selected].__str__())
                self.parent.msg("|/"+self[selected].desc)
        else:
            self.parent.msg(self.__str__())
        
    def _reset(self): # Debug: reset everything
        """
            Debug: Remove all character skills and return to base state.
        """
        if self.training != None:
            try:
                self.training.Cancel()
            except:
                pass
            self.training = None
        while len(self.skills):
            (k,o) = self.skills.popitem()
            del o
        self.parent.attributes.clear(category="skills")
        self.stance = None
        self.job = None
        self.role = None
        for stype in ["stance","job","role"]:
            d = self.skillsets[stype]
            while len(d):
                (k,o) = d.popitem()
                del o
            self.parent.attributes.clear(category=stype)
            self.parent.attributes.remove(stype)
        self.populated=False # Though technically true since no skills exist
        self.normalize() # sanity
    
    def isActive(self,skillName):
        if self.stance != None and self.stance.find(skillName):
            return True
        if self.job != None and self.job.find(skillName):
            return True
        if self.role != None and self.role.find(skillName):
            return True
        return False
    
    def Check(self,skillName,tier = 1, min_tier = -1, max_tier = -1, **kwargs) -> int:
        """
            Performs a skill check.  A result less than zero is a failure.
            Results close to zero exercise the skill and associated stats.
            This may change in later versions of the system.
        """
        
        skill = self[skillName]
        result = skill.Check(tier,min_tier,max_tier,**kwargs)
        return result
        
    def TagCheck(self,tags):
        """
            ???
        """
        # Rolls a 
        return 0
    
    def All(self) -> Generator[Skill,None,None]:
        """
            Returns a Generator for all this character's skills.
        """
        if not self.populated:
            self.populate()
        for key in self.skills:
            yield self.skills[key]

    def Cooldown(self):
        for skill in self.All():
            skill.Cooldown()
#
# These functions advance your skills
#
    def Rest(self):
        """
            Resting is necessary to advance skills.  When you rest, all skills that can advance will.
        """
        for skill in self.All():
            skill.Rest()
    
    def Train(self):
        """
            Training is a step above simply putting in effort and should require a trainer.
            You can only train when resting would ordinarily raise you (max practice)
            but you have also reached the limit of effort alone (max effort)
            and do not need to meditate yet (training is not maxed)
        """
        # todo: should require and check for trainer
        for skill in self.All():
            if skill.can_train:
                if not skill.can_meditate:
                    skill.train_up() 
                else:
                    self.parent.msg(f"You need to meditate on {skill.name}ing before you can train any more.")
    
    def Meditate(self):
        """
            Meditation consolidates your training and allows you to advance further.
        """
        for skill in self.All():
            if skill.can_train and skill.can_meditate:
                skill.affinity_up()
