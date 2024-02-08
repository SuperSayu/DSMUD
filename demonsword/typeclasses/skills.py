"""
    Skills are attached to characters and are referenced by items and skill challenges.
    Actions that exercise a skill increase its practice
    
    Use the skills category to store skill dicts
    skill: { key: string, attribute: string|null, aspect: string|null, exp:int, effort:int, training:int, mastery:int, affinity:int }
"""
from evennia.objects.objects import DefaultObject
from .objects import ObjectParent
from util.random import roll,show_roll
from util.AttributeProperty import AttributeProperty,SubProperty
from .attr_aspect import AttributeList,AspectList,StatNames
from random import randint
from evennia.utils.evmenu import get_input # caller, prompt, callback, *args, **kwargs
from world.skills import SkillDB
# Increment when revised
SKILLS_VERSION = 0.1

# I believe this coefficient may be better at 0.55 for approx 1% xp at +/-8
# Current coefficient is for debugging (involving massive skill grinding)
SKILL_PRACTICE_COEFFICIENT = 0.875

skilldb = SkillDB()

skill_default = lambda _s,_i,_a,key: {"key":key,"aspect":None,"stance":None,"job":None,"role":None,"exp":0.0,"streak":0,"effort":0,"training":0,"affinity":0,"mastery":0}

# data = SA() -> packed data available for standard SubProperty()
class SkillAttribute(AttributeProperty):
    _attr_get_source = lambda _, instance: instance.parent.attributes
    _key_get = lambda _,instance: instance.key
    _data_default = skill_default
    _category="skills"

class SkillStatSubProperty(SubProperty):
    pass

# x = SFSP() -> skill.x == skill.flavor["x"]
class SkillFlavorSubProperty(SubProperty):
    _data_access = lambda _,instance: instance.flavor

class Skill:
    parent      = None  # Character
    key         = ""    # Skill unique identifier\
    
    flavor      = None  # -> skilldb[key]
    name        = SkillFlavorSubProperty()
    doing       = SkillFlavorSubProperty()
    desc        = SkillFlavorSubProperty()
    stat        = SkillFlavorSubProperty() # !

    data        = SkillAttribute() # packed data stored in attribute dict()
    exp         = SubProperty()
    streak      = SubProperty()
    effort      = SubProperty()
    training    = SubProperty()
    affinity    = SubProperty()
    mastery     = SubProperty()
    
    aspect      = SubProperty() # set when you enter a stance
    stance      = SubProperty() # set to the stance name when put in a stance
    job         = SubProperty() # set to the job name when slotted
    role        = SubProperty() # set to the role name when slotted

#region internals    
    def __init__(self, character, key):#, data=None):
        self.parent = character
        self.key = key
        self.flavor = skilldb[self.key]
    
    def exp_fraction(self,f):
        simple={1:"⅞",7/8:"¾",3/4:"⅝",5/8:"½",1/2:"⅜",3/8:"¼",1/4:"⅛",1/8:""}
        while len(simple):
            (n,s) = simple.popitem()
            if f < n:
                return s
        return "?"
        
    def exp_str(self):
        x = self.exp
        i = int(x)
        if x == i:
            return i.__str__()
        return f"{i}{self.exp_fraction(x-i)}"
    def streak_str(self):
        x = self.streak
        i = int(x)
        if x == i:
            return i.__str__()
        return f"{i}{self.exp_fraction(x-i)}"
    def __str__(self): # todo pretty print
        v=" |C|||n "
        return v.join([
            f"|w{self.name}({self.stat})|n".rjust(19),
            self.exp_str().center(5),
            str(self.EV).center(5),
            str(self.statValue).center(5),
            f"{self.streak_str()}/{self.effort}".center(5),
            str(self.training).center(5),
            str(self.affinity).center(5),
            str(self.mastery).center(5)
        ])
    def _reset(self):
        self.parent.attributes.remove(self.key,category="skills")
        del self.parent.skills[self.key]
#endregion

    def Cooldown(self):
        if self.streak > 0:
            self.streak = max(self.streak - 0.05, 0)
            if self.streak == 0:
                self.parent.msg(f"Your {self.name} skill has completely cooled down.")
                self.parent.skills.warm.remove(self.key)
        
    def roll(self,show=False):
        """
            Roll the skill.  The maximum tier of the skill check caps your affinity.
            Any stats above your training value are turned into Brute dice.
        """
        streak = int(self.streak)
        mas = self.mastery  # d12: 25% 0, 33% 1, 33% 2, 8% 3 
        aff = self.affinity # d10: 30% 0, 40% 1, 30% 2 
        trn = self.training #  d8: 37% 0, 50% 1, 13% 2
        stat = self.statValue   # d6: 50% 0, 50% 1
        eff = min(self.effort,streak)  # d4: 75% 0, 25% 1        
        
        # If you are rolling a standby or inactive skill, some dice are penalized
        stat_brute = 0  # Brute: 50% -1, 50% +1
        aff_slip = 0    #  Slip: 30% -1, 40% +1, 30% +2
        active = self.active
        if active != True:
            if stat > streak:
                stat_brute = stat - streak
                stat = streak
        if active == None:
            eff = 0
            if aff > streak:
                aff_slip = aff - streak
                aff = streak
        
        # Penalize stats above your training
        
        brute = 0
        if stat > trn + 1:
            brute = stat - trn - 1
            stat = trn + 1
        if show:
            astate = "(active)" if active else "(passive)" if active==False else "(inactive)"
            return show_roll(self.parent,f"{self.name}{astate}",d4=eff, d6=stat, d8=trn,d10=aff,d12=mas,brute=stat_brute,slip=aff_slip)
        else:
            return roll(d4=eff, d6=stat, d8=trn,d10=aff,d12=mas,brute=stat_brute,slip=aff_slip)
            

    def Check(self,tier = 1, min_tier = -1, max_tier = -1, *, show=True,do_practice=True, success_func=None, fail_func=None, **data ):
        """
            Perform a skill check, DC 1 + 2*tier.
            If the check fails but would succeed at a lower tier,
            down to the given minimum, take penalties to reach that state.
            These penalties may create a de facto failure despite check success.
            Practices the skill.  Effective exp gain closest to nominal check tier.
            
            Should have progressively worse rolls when the skill is:
                Active (in stance - best)
                Passive (not in stance, but in role/job
                Neither (worst)
        """
        if min_tier == -1:
            min_tier = tier
        if max_tier == -1:
            max_tier = tier
        challenge = 1 + 2 * tier
        result = self.roll(show=True)
        result_tier = (result-1)//2
        if do_practice:
            self.practice(abs(result - challenge))
        boost = 0
        if result_tier < min_tier:
            if fail_func != None:
                #self.parent.msg(f"Hard fail {result}:{result_tier} ({min_tier}-{tier}-{max_tier})")
                fail_func(self,result_tier,result_tier - tier,**data)
        elif success_func != None:
            boost = min(result_tier - tier, max_tier)
            success_func(self,result_tier, boost, **data)
        return result_tier

#region properties
    @property
    def active(self):
        if self.stance:
            return True
        if self.job or self.role:
            return False
        return None
    @property
    def passive(self):
        if self.stance:
            return False
        if self.job or self.role:
            return True
        return None
    @property
    def statValue(self):
        if self.stat == None:
            return 0
        return self.parent.stats[self.stat].value
    @property
    def statBrute(self):
        """
        Brute value for this skill's stat.  Applies if you have more stats than training.
        """
        sv = self.statValue
        t = self.training + 1
        if sv <= t:
            return 0
        return sv - t
    
    @property
    def can_rest(self):
        return self.exp >= (self.effort + 2)
    @property
    def can_train(self):
        return self.effort == (self.training+2) and self.can_rest
    @property
    def can_meditate(self):
        return self.training == (self.affinity+2) and self.can_train
    @property
    def can_master(self):
        return self.affinity == (self.mastery+2) and self.can_meditate
    @property
    def EV(self):
        """
        Expected value of the dice roll.  Used for difficulty calculations.
        
        Practice is 3/4 +0, 1/4 +1                      = 1/4
        Stats are 3/6 +0, 3/6 +1                        = 1/2
        Brute stats are 3/6 -1, 3/6 +1                  = 0
        Training is 3/8 +0, 4/8 +1, 1/8 +2              = 3/4
        Affinity is 3/10 +0, 4/10 +1, 3/10 +2           = 1
        Mastery is 3/12 +0, 4/12 +1, 4/12 +2, 1/12 +3   = 1 1/4

        The more dice you have, the more you will trend towards your EV (sharper bell curve).
        """
        x=self.effort*0.25 + (self.statValue - self.statBrute)*0.5 + self.training * 0.75 + self.affinity + self.mastery * 1.25
        i=int(x)
        s= "+" if i>=0 else "-"
        return f"{s}{i}{self.exp_fraction(x-i)}"
#endregion properties
  
#region advancement
    def practice(self,amt):
        # The amount of exp you can have before resting is capped by your current effort in a skill
        # You get more exp if you are close to the target difficulty
        # Practicing a skill with wide min-max tiering is not necessarily good for xp
        amt = (self.affinity + 1) * round(pow(SKILL_PRACTICE_COEFFICIENT,amt),4)
        if amt < 0.01:
            return
        self.parent.stats[self.stat].Exercise(self,amt)
        self.streak = min(self.effort, self.streak + amt)
        self.parent.skills.warm.add(self.key)

        if self.can_rest:
            return
        base = self.exp // 1 # integer of experience
        self.exp += amt
        newbase = self.exp // 1
        
        if newbase > base:
            if self.can_rest:
                self.exp = newbase # In case we reach maximum, truncate to integer
                self.parent.msg(f"|CYour |w{self.name} skill|C feels full.  You should |yrest|C for a while.|n")
            else:
                self.parent.msg("Your skill feels more experienced.")
        
    def Rest(self):
        if not self.can_rest:
            return
        self.effort_up()
    def Sleep(self):
        self.Rest()
    def Meditate(self):
        self.affinity_up()
    def effort_up(self):
        if self.can_train: # Maxed on effort
            if self.can_meditate:
                # if self.can_master
                self.parent.msg(f"After all the work you've put into {self.name}, you feel you need to meditate and search your soul to figure out what you need to do to get better.  You won't be able to train until you have cleared your mind.")
                return
            self.parent.msg(f"|CYou have learned all you can about |y{self.doing}|C by effort alone.  You need to find a |ytrainer|C.|n")
            return
            #self.train_up()
        else:
            self.parent.msg(f"|CYour efforts with the |w{self.name} skill|C have borne fruit.  You can now practice it better.|n")
            self.effort += 1
        self.exp = 0
    def train_up(self):
        if self.can_meditate:
            # if self.can_master
            self.parent.msg(f"After all the work you've put into {self.name}, you feel you need to meditate and search your soul to figure out what you need to do to get better.  You won't be able to train until you have cleared your mind.")
            return
        self.parent.msg(f"Your training with the {self.name} skill has improved your technique, but it will take some effort to get used to it.")
        self.training += 1 # todo
        self.effort=0
        self.streak=0
        self.exp=0
        return
    def affinity_up(self):
        if self.can_master:
            #todo separate mechanism
            self.mastery_up()
            return
        self.affinity += 1
        self.parent.msg(f"Your affinity with the {self.name} skill increases to {self.affinity}.")
        self.parent.msg("You will have to start your training over from scratch.")
        self.training = 0
        self.effort=0
        self.streak=0
        self.exp=0
    def mastery_up(self):
        # Todo: Select some mechanism here, most likely a permanent unlock or circumstantial bonus
        self.mastery += 1
        self.affinity = 0
        self.training = 0
        self.effort=0
        self.streak=0
        self.exp=0
        self.parent.msg(f"You feel your mastery with the {self.name} skill increase to {self.mastery}")
        self.parent.msg("You will need to gain affinity with this skill all over again.")
        
#endregion
