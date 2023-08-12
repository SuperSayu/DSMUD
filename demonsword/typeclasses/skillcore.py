"""
    The skillcore is a central facility for characters to attempt difficult tasks
    and grow with their success and failure.
    
    The skillcore does not handle translating actions into skill rolls.  That is the
    action core, which takes input from equipment and magical effects.
    
    Use the skills category for all named attributes
    
    The DSP skill advancement system includes gains and losses and takes more and more effort
    as you go up in skill.
"""
from .dice import roll
from .skills import Skill

class SkillCore:
    """
        A character SkillCore is the central point for asking the character to roll a skill check.
        It will also handle advancement when the character rests.
    """
    parent = None
    skills = {}
    training = None
    def __init__(self,parent):
        self.parent=parent
        
    def __getitem__(self, key):
        if key in self.skills:
            return self.skills[key]
        temp = Skill(self.parent,key)
        self.skills[key] = temp
        return temp
    def __str__(self):
        result=""
        for skill in self.parent.attributes.all(category="skills"):
            result += skill.value.__str__() + "\n"
        return result
        
    def _load(self): # Not really needed since skills load on a lazy basis
        """
        """
        
    def _save(self): # Probably not needed
        """
        """
        for key in skills:
            skills[key]._save()
        pass
        
    def Check(self,skillName,difficulty,tags=[]):
        skill = self[skillName]
        result=skill.Check(difficulty)
        near = abs(result)
        if near <= 1: # Exercise when close
            skill.practice(near)
            if skill.stat != None:
                self.parent.stats.Exercise(skill.stat,near)
        return result
        
    def TagCheck(self,tags):
        # Rolls a 
        return 0
    

#
# These functions advance your skills
#
    def Rest(self):
        """
            Resting is necessary to advance skills.  When you rest, all skills that can advance will.
        """
        # This could be more efficient if we knew that we had already pulled all skills
        # 
        for skill in self.parent.attributes.all(category="skills"):
            if not (skill.key in self.skills):
                self.skills[skill.key] = Skill(self.parent,skill.key,data=skill.value)
            self.skills[skill.key].Rest()
        pass
    def Train(self):
        """
            Training is a step above simply putting in effort and should require a trainer.
            You can only train when resting would ordinarily raise you (max practice)
            but you have also reached the limit of effort alone (max effort)
            and do not need to meditate yet (training is not maxed)
        """
        # todo: should require and check for trainer
        for skill in self.parent.attributes.all(category="skills"):
            if not (skill.key in self.skills):
                skill = Skill(self.parent,skill.key,data=skill.value)
                self.skills[skill.key] = skill
            else:
                skill = self.skills[skill.key] 
            if skill.can_train:
                if not skill.can_meditate:
                    skill.train_up() 
                else:
                    self.parent.msg(f"You need to meditate on {skill.name}ing before you can train any more.")
    def Meditate(self):
        """
            Meditation consolidates your training and allows you to advance further.
        """
        # todo: should require and check for trainer
        for skill in self.parent.attributes.all(category="skills"):
            if not (skill.key in self.skills):
                skill = Skill(self.parent,skill.key,data=skill.value)
            skill = self.skills[skill.key] 
            if skill.can_train and skill.can_meditate:
                skill.affinity_up()
