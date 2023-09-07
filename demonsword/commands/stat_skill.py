"""
	Commands for viewing your stats and skills
"""
from evennia import Command

class SkillsCommand(Command):
    """
        Your skills will be checked when you attempt anything useful.
        Your skill's effort, training, affinity, and mastery will provide
        increasing value.  When you cannot gain any more experience, rest.
        When your effort is maxed, train.  When your training is maxed,
        meditate.  Your maximum of each goes up when stats above it raise.
        
        When you first train, you will associate skills with an attribute.
        Later, you will associate skills with an aspect.
        I hate your face.
    """
    key="skill"
    aliases=["skills"]
    def func(self):
        target=self.args.strip().lower()
        if len(target):
            self.caller.skills.show(target)
        else:
            self.caller.skills.show()
class StatsCommand(Command):
    key="stats"
    def func(self):
        self.caller.msg("Your stats:")
        self.caller.msg(self.caller.stats.show())
