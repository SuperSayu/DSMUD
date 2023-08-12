"""
"""
from evennia import Command
from time import sleep
class RestCommand(Command):
    """
        This is being used as a temporary skill test
        Later resting should require a dedicated area and take time
    """
    key="rest"
    def parse(self):
       self.caller.msg(f"Rest: {self.args}")
    def func(self):
        self.caller.msg("You start resting...")
        self.caller.skills.Rest()
        self.caller.stats.Rest()
        self.caller.msg("You finish resting.")
class TrainCommand(Command):
    """
        This is being used as a temporary skill test
        Later resting should require an npc and take time and/or money
    """
    key="train"
    def func(self):
        self.caller.msg("You begin training...")
        self.caller.skills.Train()
        if not self.caller.skills.training:
            self.caller.msg("You finish training.")
        
class MeditateCommand(Command):
    """
        This is being used as a temporary skill test
        Later resting should require a dedicated area and take time
    """
    key="meditate"
    def func(self):
        self.caller.msg("You begin meditating...")
        self.caller.skills.Meditate()
        self.caller.msg("You finish meditating.")
class SleepCommand(Command):
    key="sleep"
    def func(self):
        self.caller.msg("You begin sleeping...")
        self.caller.stats.Sleep()
        self.caller.msg("You finish sleeping.  (More of a power nap, really.)")
