"""
"""
from evennia import Command
class ForageCommand(Command):
    """
        This is being used as a temporary skill test
        
    """
    key="forage"
    skillName="forage"
    skillKey="forage"
    #def parse(self):
    #   self.caller.msg(f"{self.skillName}: {self.args}")
    def func(self):
        #self.caller.msg(f"Attempting {self.skillName} skill check...")
        result = self.caller.skills.Check(self.skillKey,1)
        if result >= 0:
            self.success(result)
        else:
            self.failure(result)
    def success(self,value):
        
        self.caller.msg(f"You {self.skillName} for a while and find stuff I guess. ({value})")
    def failure(self,value):
        self.caller.msg(f"You {self.skillName} for a while and find nothing. ({value})")
class MineCommand(ForageCommand):
    key="mine"
    skillName="mine"
    skillKey="mine"