"""
"""
from evennia import Command
class RestCommand(Command):
    """
        This is being used as a temporary skill test
    """
    key="rest"
    def parse(self):
       self.caller.msg(f"Rest: {self.args}")
    def func(self):
        self.caller.msg("Resting skills...")
        self.caller.skills.Rest()
