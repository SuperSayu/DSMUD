"""
"""
from evennia import Command
from .StateCommandBase import StateCommand
from time import sleep
from random import randint,shuffle
from typeclasses.dice import prob
class RestCommand(StateCommand):
    """
        Temporary: Resting distributes skill and stat exp
        and increases skill effort.
    """
    key="rest"
    doing="resting"
    
    def state_start(self):
        self.caller.msg("You begin resting.")
        candidates= [*self.caller.skills]
        candidates.extend([*self.caller.stats.Aspects])
        self.need=[]
        for n in candidates:
            if n.can_rest:
                self.need.append(n)
        self.needless = (len(self.need) == 0)
        shuffle(self.need)
        self.sleep(randint(3,5) + randint(0,len(self.need)))
    def state_cancel(self):
        self.caller.msg("You stop resting.\n\n")
    def state_finish(self):
        self.caller.msg("You finish resting.\n\n")
    def state_continue(self):
        if len(self.need) == 0:
            if self.needless:
                self.caller.msg("You didn't feel much need to rest in the first place.")
            self.finish()
            return
        etwas = self.need.pop()
        etwas.Rest()
        self.sleep_rand(1,4)
    
class TrainCommand(StateCommand):
    """
        Temporary: Skills at max effort/practice increase train level.
    """
    key="train"
    doing="training"
    trainer="Dick Seaman"
    last_skill = None
    def state_start(self):
        self.caller.msg(f"You begin training with {self.trainer}")
        self.need = []
        for s in self.caller.skills:
            if s.can_train: # deliberately leaving out the meditate check here, get dunked on
                self.need.append(s)
        self.needless = (len(self.need) == 0)
        shuffle(self.need)
        self.sleep_rand(3,5)
    def state_cancel(self):
        self.caller.msg("You stop training.")
    def state_finish(self):
        self.caller.msg("You finish training.")
    def state_skip(self):
        if prob(20):
            self.caller.msg("You converse with your trainer for a while.")
    def state_continue(self):
        if len(self.need) == 0:
            if self.needless:
                self.caller.msg("Your trainer says they have nothing to teach you right now.")
            self.finish()
            self.last_skill = None
            return
        etwas = self.need.pop()
        etwas.train_up()
        self.sleep_rand(3,5)
        
class MeditateCommand(StateCommand):
    """
        Temporary: Skills at max train/effort/practice increase affinity.
    """
    key="meditate"
    last_skill = None
    def state_start(self):
        self.caller.msg("You begin meditating...")
        self.need = []
        for s in self.caller.skills:
            if s.can_meditate:
                self.need.append(s)
        self.needless = len(self.need) == 0
        self.sleep_rand(3,5)
    def state_cancel(self):
        self.caller.msg("You stop meditating.")
    def state_finish(self):
        self.caller.msg("You finish meditating.")
    def state_continue(self):
        if len(self.need) == 0:
            if self.needless:
                self.caller.msg("You feel like your meditation was unproductive.")
            self.finish()
            return
        etwas = self.need.pop()
        etwas.Meditate()
        self.sleep_rand(3,5)
class SleepCommand(StateCommand):
    """
        Temporary: Stats at max xp gain bonus.
    """
    key="sleep"
    def state_start(self):
        self.caller.msg("You begin sleeping...")
        self.need = []
        for s in self.caller.skills:
            if s.can_meditate:
                self.need.append(s)
        for s in self.caller.stats.Stats:
            if s.can_improve:
                self.need.append(s)
        self.needless = (len(self.need) == 0)
        shuffle(self.need)
        self.sleep_rand(3,5)
    def state_cancel(self):
        self.caller.msg("You wake up with a start!")
    def state_finish(self):
        self.caller.msg("You wake up.")
    def state_continue(self):
        if len(self.need) == 0:
            if self.needless:
                self.caller.msg("You feel rested but not any stronger.")
            self.finish()
            return
        etwas = self.need.pop()
        etwas.Sleep()
        self.sleep_rand(3,5)
    
class ResetStatsCommand(Command):
    """
        Debug: Reset all skills and stats
    """
    key="resetstats"
    def func(self):
        self.caller.stats._reset()
        self.caller.skills._reset()
        self.caller.msg("DEBUG: All skills and stats have been stripped and reset.")
        self.caller.msg("If this function is still around when this server is in use,")
        self.caller.msg("please punch Sayu in the face.")