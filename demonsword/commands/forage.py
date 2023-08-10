"""
"""
from evennia import Command
class ForageCommand(Command):
    """
        This is being used as a temporary skill test
        
    """
    key="forage"
    def parse(self):
       self.caller.msg(f"Echo: {self.args}")
    def func(self):
        self.caller.msg("Attempting forage skill check...")
        result = self.caller.skills.Check("forage",1)
        self.caller.msg(f"Got a {result}")
