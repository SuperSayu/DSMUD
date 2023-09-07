"""
"""
from evennia import Command
from .StateCommandBase import StateCommand
from random import randint
from util.random import prob

class ForageCommand(StateCommand):
    """
        Look for resources in the local environment.
        This is being used as a temporary skill test        
    """
    key="forage"
    skillName="forage"
    doing = "foraging"
    skillKey="forage"
    checkTier = 2
    minCheck = 1
    maxCheck = 3
    
    def state_start(self):
        if self.caller.skills[self.skillKey].can_rest:
            self.caller.msg(f"You don't think you'll be able to get any better at {self.doing} without resting for a bit.")
        self.caller.msg(f"You begin {self.doing}.")
        self.frustration=0
        self.sleep(randint(1,3))
        
    def check_success(self, skill, raw_result, boost):
        if boost < 0:
            self.caller.msg(f"You awkwardly {self.skillName} for a while and find stuff I guess. ({boost})")
        else:
            self.caller.msg(f"You skillfully {self.skillName} around and find great stuff. ({boost})")
        self.caller.location.msg_contents("{person} finishes searching and stands up, looking pleased.",mapping={"person":self.caller},exclude=(self.caller) )
        self.finish()
        
    def check_failure(self,skill,raw_result, boost):
        self.caller.msg(f"You {self.skillName} for a while and find nothing. ({boost})")
        if prob(30):
            self.caller.location.msg_contents("{person} pauses their search with a frown.",mapping={"person":self.caller},exclude=(self.caller) )
        
        if self.caller.skills[self.skillKey].can_rest: # full on exp
            self.frustration += 15
        else:
            self.frustration += 5
        if prob(self.frustration):
            self.caller.msg(f"You give up on {self.doing}.")
            self.cancel()
    
    def state_continue(self):
        self.caller.skills.Check(self.skillKey,self.checkTier,self.minCheck,self.maxCheck,success_func=self.check_success,fail_func=self.check_failure)
        self.sleep(randint(1,3))
    def state_cancel(self):
        self.caller.msg(f"You stop {self.doing}.\n\n")
    def state_finish(self):
        self.caller.msg(f"You finish {self.doing}.\n\n")
    
    # Flavor messages and loot distribution
    def state_skipped(self):
        if prob(20):
            self.caller.msg("You root around a bit.")
            self.caller.location.msg_contents("{person} searches around a bit.",mapping={"person":self.caller},exclude=(self.caller) )
    

class MineCommand(ForageCommand):
    key="mine"
    skillName= "mine"
    doing = "mining"
    skillKey = "mine"