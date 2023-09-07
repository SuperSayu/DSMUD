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

class SkillCore:
    """
        A character SkillCore is the central point for asking the character to roll a skill check.
        It will also handle advancement when the character rests.
    """
    parent = None
    skills = {}
    training = None
    populated=False
    
    def __init__(self,parent):
        self.parent=parent
        
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
        
    def __str__(self):
        """
            Debug/Temporary: Formal all skills into a simple list.
        """
        result=f"Skill Name |  exp  |  eff\u25b3 |  trn\u25ca |  aff\u25c8 |  mas\u25cc\n----------------------------------------------------\n"
        for skill in self.parent.attributes.all(category="skills"):
            result += self[skill.key].__str__() + "\n"
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
    
    def populate(self):
        """
            Internal: Finish lazy-loading all skills from their Evennia attributes.
        """
        if self.populated:
            return
        for skill in self.parent.attributes.all(category="skills"):
            if not (skill.key in self.skills):
                self.skills[skill.key] = Skill(self.parent,skill.key,data=skill.value)
        self.populated = True
    
    def show(self,selected:Union[str,list[str]]=None):
        """
            Temporary: Show one, a subset, or all skills to the user in a simple list.
        """
        if(selected != None):
            if not self.parent.attributes.has(selected,category="skills"):
                self.parent.msg(f"You have no {selected} skill.")
                return
            self.parent.msg("Skill Name |  exp  |  eff\u25b3 |  trn\u25ca |  aff\u25c8 |  mas\u25cc\n----------------------------------------------------\n")
            if type(selected) is list:
                for s in selected:
                    self.parent.msg(self[s].__str__())
            else:
                self.parent.msg(self[selected].__str__())
        else:
            self.parent.msg(self.__str__())
    def _load(self): # Not really needed since skills load on a lazy basis
        """
            Internal: Load data from Evennia attributes.
        """
        self.Populate()
        
    def _save(self):
        """
            Internal: Save data to Evennia attributes.
            The Skill Core does not have any unique data
            and only force-saves all extant skills.
        """
        for key in skills:
            skills[key]._save()
        pass
        
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
        self.populated=False # Technically true since no skills exist
        
    def Check(self,skillName,tier = 1, min_tier = -1, max_tier = -1, **kwargs) -> int:
        """
            Performs a skill check.  A result less than zero is a failure.
            Results close to zero exercise the skill and associated stats.
            This may change in later versions of the system.
        """
        
        """skill = self[skillName]
        result=skill.Check(difficulty)
        near = abs(result)
        if near <= 4:
            skill.practice(near)
            if skill.stat != None:
                self.parent.stats.Exercise(skill.stat,skill,near)"""
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
