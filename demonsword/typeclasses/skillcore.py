"""
    The skillcore is a central facility for characters to attempt difficult tasks
    and grow with their success and failure.
    
    The skillcore does not handle translating actions into skill rolls.  That is the
    action core, which takes input from equipment and magical effects.
    
    Use the skills category for all named attributes
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
        
    def _save(self):
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
        return result
        
    def TagCheck(self,tags):
        # Rolls a 
        return 0
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
