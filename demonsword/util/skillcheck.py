"""
    Handling objects for skill checks
    
    The math behind skill checks is actually stupidly complex,
    all to create a weighted bell curve.  Because the skill checks
    go up almost forever with skill, we have to ratchet up our expectations
    and give bonuses for high rolls, with commensurately lower rewards for
    trivial rolls.  Different types of skill checks have different types of
    rowards, and different difficulty tiers are configured differently.
    
    The skill check class is meant to be inherited by subtypes for things
    like resource spawning, resource conversion, combat, etc.
    
    Uncontested skill difficulty is tiered, with:
    * a default tier that has nominal rewards
    * a minimum tier below which the skill never succeeds
    * a maximum tier at which you cannot get better rewards
    
    These skill checks work by having penalty and bonus adds, which tweak check rewards.
    If your skill affinity is lower than the default tier but at or above the minimum,
    you will gain penalty adds and the difficulty will lower.
    If your skill affinity is above the maximum tier, it will be capped.
    For every two successes above the DC, you gain a bonus add (or lose a penalty add),
    to a maximum of max_tier bonus adds.
    
    The skill check result is a dictionary:
        * returned by skill.check_success(result,penalty_count)
        * submitted to skill.check_results(result)
    
    A contested skill check is different and TBD lol.
    
    ---
    
    this model can't work because stat gains are too op here
    bound state 
    
"""

from util.random import roll,show_roll

def SkillCheck(character,skill,tier,min_tier=0,max_tier=10,show=True):
    eff_tier = tier



"""
class SkillCheck:
    def __init__(self,character,skill,tier=5,min_tier=0,max_tier=10,**kwargs):
        self.character=character
        self.skill=skill
        self.tier = tier
        self.min_tier = min_tier
        self.max_tier = max_tier
        self.kwargs=kwargs
    def silent_roll(self):
        tier = self.tier
        aff = self.skill.affinity
        penalty = 0
        if aff < tier:
            penalty = tier - aff
            tier = aff
        result = skill.roll(1 + tier * 2,self.max_tier)
        result_struct = skill.check_success(result)
        #return roll(d4=self.data["effort"], d6=stat, d8=self.data["training"],d10=self.data["affinity"],d12=self.data["mastery"]) - 1 - self.tier*2
    def visual_roll(self):
        pass
        #return show_roll(self.parent,self.name,challenge,d4=self.data["effort"], d6=stat, d8=self.data["training"],d10=self.data["affinity"],d12=self.data["mastery"]) - 1 - self.tier * 2
"""