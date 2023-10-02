"""
"""
from evennia import Command
from .StateCommandBase import StateCommand
from random import randint
from util.random import prob
from typeclasses.resources import ResourceNode

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
        room = self.caller.location
        self.source = None
        for obj in room.contents:
            if isinstance(obj,ResourceNode) and obj.skill_key == self.key:
                self.source = obj
                break
        if self.caller.skills[self.skillKey].can_rest:
            self.caller.msg(f"You don't think you'll be able to get any better at |y{self.doing}|n without |yresting|n for a bit.")
        self.caller.msg(f"You begin |y{self.doing}|n.")
        self.frustration=0
        self.sleep(randint(1,3))
        
    def check_success(self, skill, result, boost):
        if self.source:
            if self.source.forage(self.caller,skill,result):
                self.caller.location.msg_contents("{person} finishes searching and stands up.",mapping={"person":self.caller},exclude=(self.caller) )
                self.finish()
            else:
                self.check_failure(skill,result,boost)
            return
        if boost < 0:
            self.caller.msg(f"You awkwardly |y{self.skillName}|n for a while and find stuff I guess. ({boost})")
        else:
            self.caller.msg(f"You skillfully |y{self.skillName}|n around and find great stuff. ({boost})")
        self.caller.location.msg_contents("{person} finishes searching and stands up, looking pleased.",mapping={"person":self.caller},exclude=(self.caller) )
        self.finish()
        
    def check_failure(self,skill,result, boost):
        if self.source:
            if self.source.seen(self.caller):
                self.caller.msg(f"You |y{self.skillName}|n at the |w{self.source}|n and find nothing useful.")
            else:
                self.caller.msg(f"You |y{self.skillName}|n around and find nothing.")
        #self.caller.msg(f"You {self.skillName} for a while and find nothing. ({boost})")
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
        if self.source:
            self.caller.skills.Check(self.skillKey,self.source.nominal_tier,self.source.min_tier,self.source.max_tier,success_func=self.check_success,fail_func=self.check_failure)
        else:
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