"""
    Skills are attached to characters and are referenced by items and skill challenges.
    Actions that exercise a skill increase its practice
    
    Use the skills category to store skill dicts
    skill: { key: string, attribute: string|null, aspect: string|null, exp:int, effort:int, training:int, mastery:int, affinity:int }
"""
from evennia.objects.objects import DefaultObject
from .objects import ObjectParent
from util.random import roll,show_roll
from .attr_aspect import AttributeList,AspectList,StatGrid,StatNames
from random import randint
from evennia.utils.evmenu import get_input # caller, prompt, callback, *args, **kwargs
from world.skills import SkillDB
# Increment when revised
SKILLS_VERSION = 0.1

# I believe this coefficient may be better at 0.55 for approx 1% xp at +/-8
# This coefficient is for debugging (involving massive skill grinding)
SKILL_PRACTICE_COEFFICIENT = 0.875

skilldb = SkillDB()

def link_skill_to_stat(caller,skill):
    caller.msg(f"You need to pick a primary stat to use for the {skill.name} skill.  Choose one from this grid:")
    caller.msg(StatGrid(with_aspects=False,include_health=False))
    skill.choosing = True
    caller.skills.training = skill
    get_input(caller,"Which one?",link_skill_stat_callback,None,**{"skill":skill})
def link_skill_stat_callback(caller,prompt,response,skill):
    skill.choosing = False
    response = response.strip().lower()
    if not response in AttributeList:
        caller.msg("Ok, maybe later.")
        caller.skills.training = None
        return
    skill.stat = response
    res_name = StatNames[response]
    caller.msg(f"You link the {skill.name} skill to your {res_name} stat.")
    skill.train_up()
    caller.skills.training = None

def link_skill_to_aspect(caller,skill):
    stat = caller.stats[skill.stat]
    caller.msg(f"You need to pick an aspect (row or column) to use for the {skill.name} skill.")
    caller.msg(f"This will improve your aspect, allowing further growth.")
    caller.msg(f"Since it is associated with {stat.name}, you can pick between {stat.col.name} ({stat.col_key}) and {stat.row.name} ({stat.row_key}).")
    [can_col,can_row] = [caller.stats[stat.col_key].can_improve,caller.stats[stat.row_key].can_improve]
    if not can_col and not can_row:
        caller.msg(f"Unfortunately, neither aspect is ready.  You should exercise and improve your stats.")
        return
    skill.choosing = True
    caller.skills.training = skill
    if not can_col:
        caller.msg(f"Unfortunately, your {stat.col.name} aspect is not ready.  You should exercise and improve your stats.")
        get_input(caller,f"Link with your {stat.row.name} aspect?  Type yes or {stat.row_key} to proceed.",link_skill_aspect_callback,None,**{"skill":skill,"yes_opt":stat.row_key})
    elif not can_row:
        caller.msg(f"Unfortunately, your {stat.row.name} aspect is not ready.  You should exercise and improve your stats.")
        get_input(caller,f"Link with your {stat.col.name} aspect?  Type yes or {stat.col_key} to proceed.",link_skill_aspect_callback,None,**{"skill":skill,"yes_opt":stat.col_key})
    else:
        get_input(caller,"Which one?  Type the three letter code, or nothing to cancel.",link_skill_aspect_callback,None,**{"skill":skill,"yes_opt":None})

def link_skill_aspect_callback(caller,prompt,response,skill,yes_opt):
    stat = caller.stats[skill.stat]
    response = response.strip().lower()
    if response == "yes":
        if not isinstance(yes_opt,str):
            link_skill_to_aspect(caller,skill)
            return
        response = opts
    if (not response in [stat.col_key,stat.row_key]):
        caller.msg("Ok, maybe later.")
        caller.skills.training = None
        skill.choosing = False
        caller.skills.training = None
        return
    chosen = caller.stats[response]
    # You can only raise an aspect when its row or column is full
    if not chosen.can_improve:
        caller.msg("You can only improve an aspect when all it is full.")
        caller.msg(f"You need to exercise your {chosen.name} stats more.")
        skill.choosing = False
        caller.skills.training = None
        return
    skill.choosing = False
    skill.aspect = response
    caller.msg(f"You link the {skill.name} skill to the {chosen.name} Aspect.")
    chosen.improve(skill)
    skill.affinity_up()
    caller.skills.training = None

class Skill:
    parent      = None
    key         = ""
    data        = None
    choosing    = False

#region internals    
    def __init__(self, character, key, data=None):
        self.parent = character
        self.key = key
        if data == None:
            self._load()
        else: # Override used when the skill core needs to pull all skills, no use redoing queries
            self.data = data
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
        
    def __str__(self): # todo pretty print
        v=" |C|||n "
        return v.join([
            f"|w{self.name}|n".rjust(14),
            self.exp_str().center(5),
            self.effort.__str__().center(5),
            self.training.__str__().center(5),
            self.affinity.__str__().center(5),
            self.mastery.__str__().center(5)
        ])
    def _save(self):
        self.parent.attributes.add(self.key,self.data,category="skills")
    def _load(self):
        self.data = self.parent.attributes.get(self.key,category="skills",default={"key":self.key,"stat":None,"aspect":None,"exp":0.0,"effort":0,"training":0,"affinity":0,"mastery":0})
        self.flavor = skilldb[self.key]
        # todo: lookup tags on first set
    def _reset(self):
        self.parent.attributes.remove(self.key,category="skills")
        self._load()
#endregion

    def roll(self,max_aff = -1, show=False):
        """
            Roll the skill.  The maximum tier of the skill check caps your affinity.
            Any stats above your training value are turned into Brute dice.
        """
        stat = self.statValue
        aff = self.data["affinity"]
        if max_aff > 0:
            aff = min( aff, max_aff )
        
        # Penalize stats above your training
        trn = self.data["training"]
        brute = 0
        if stat > trn + 1:
            brute = stat - trn - 1
            stat = trn + 1
        if show:
            return show_roll(self.parent,self.name,d4=self.data["effort"], d6=stat, d8=self.data["training"],d10=aff,d12=self.data["mastery"],brute=brute)
        else:
            return roll(d4=self.data["effort"], d6=stat, d8=self.data["training"],d10=aff,d12=self.data["mastery"],brute=brute)
            

    def Check(self,tier = 1, min_tier = -1, max_tier = -1, *, show=True,do_practice=True, success_func=None, fail_func=None, **data ):
        """
            Perform a skill check, DC 1 + 2*tier.
            If the check fails but would succeed at a lower tier,
            down to the given minimum, take penalties to reach that state.
            These penalties may create a de facto failure despite check success.
            Practices the skill.  Effective exp gain within 2 tiers of nominal.
        """
        if min_tier == -1:
            min_tier = tier
        if max_tier == -1:
            max_tier = tier
        challenge = 1 + 2 * tier
        result = self.roll(max_tier,show=True)
        result_tier = (result-1)//2
        if do_practice:
            self.practice(abs(result - challenge))
        if result < 1: # Hard minimum, no matter the min tier.  This might be negative with brute stats!
            if fail_func != None:
                #self.parent.msg(f"Hard fail {result}:{result_tier} ({min_tier}-{tier}-{max_tier})")
                fail_func(self,result_tier,tier - result_tier,**data)
            return -1
        
        boost = 0
        if result_tier < min_tier:
            if fail_func != None:
                #self.parent.msg(f"Hard fail {result}:{result_tier} ({min_tier}-{tier}-{max_tier})")
                fail_func(self,result_tier,result_tier - tier,**data)
        elif success_func != None:
            boost = min(result_tier - tier, max_tier)
            #if boost < 0:
                #self.parent.msg(f"Penalty {boost}; {result}:{result_tier} ({min_tier}-{tier}-{max_tier})")
            #else:
                #self.parent.msg(f"Boost {boost}; {result}:{result_tier} ({min_tier}-{tier}-{max_tier})")
            success_func(self,result_tier, boost, **data)
        return result_tier

#region properties    
    @property
    def exp(self):
        return self.data["exp"]
    @exp.setter
    def exp(self,e):
        self.data["exp"]=e
        #self._save()
    @property
    def name(self):
        return self.flavor["name"]
    @property
    def doing(self):
        return self.flavor["doing"]
    @property
    def desc(self):
        return self.flavor["desc"]
    @property
    def effort(self):
        return self.data["effort"]
    @effort.setter
    def effort(self,e):
        self.data["effort"]=e
        #self._save()
    @property
    def training(self):
        return self.data["training"]
    @training.setter
    def training(self,t):
        self.data["training"]=t
        #self._save()
    @property
    def stat(self):
        return self.data["stat"]
    @stat.setter
    def stat(self,s):
        self.data["stat"]=s
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
    def aspect(self):
        return self.data["aspect"]
    @aspect.setter
    def aspect(self,a):
        self.data["aspect"]=a
        #self._save()
    @property
    def affinity(self):
        return self.data["affinity"]
    @affinity.setter
    def affinity(self,a):
        self.data["affinity"]=a
        #self._save()
    @property
    def mastery(self):
        return self.data["mastery"]
    @mastery.setter
    def mastery(self,m):
        self.data["mastery"]=m
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
        return int( self.practice*0.25 + (self.statValue - self.statBrute)*0.5 + self.training * 0.75 + self.affinity + self.mastery * 1.25 )
#endregion properties
  
#region advancement
    def practice(self,amt):
        # The amount of exp you can have before resting is capped by your current effort in a skill
        # You get more exp if you are close to the target difficulty
        # Practicing a skill with wide min-max tiering is not necessarily good for xp
        amt = (self.affinity + 1) * round(pow(SKILL_PRACTICE_COEFFICIENT,amt),4)
        if amt < 0.01 or self.can_rest:
            return
            
        base = self.exp // 1 # integer of experience
        self.exp += amt
        newbase = self.exp // 1
        
        if newbase > base:
            if self.can_rest:
                self.exp = newbase # In case we reach maximum, truncate to integer
                self.parent.msg("Your skill feels full.  You should rest for a while.")
            else:
                self.parent.msg("Your skill feels more experienced.")
        else:
            #debug print
            #self.parent.msg(f"Gained {amt} skill xp")
            pass
        self._save()
        if self.stat != None:
            self.parent.stats[self.stat].Exercise(self,amt)
        
    def Rest(self):
        if not self.can_rest:
            return
        self.effort_up()
        self._save()
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
            self.parent.msg(f"You have learned all you can about {self.name}ing by effort alone.  You need to find a trainer.")
            return
            #self.train_up()
        else:
            self.parent.msg(f"Your efforts with the {self.name} skill have borne fruit.  You can now practice it better.")
            self.effort += 1
        self.exp = 0
        self._save()
    def train_up(self):
        if self.can_meditate:
            # if self.can_master
            self.parent.msg(f"After all the work you've put into {self.name}, you feel you need to meditate and search your soul to figure out what you need to do to get better.  You won't be able to train until you have cleared your mind.")
            return
        if self.stat == None:
            if self.parent.skills.training == None:
                self.parent.skills.training = self
                link_skill_to_stat(self.parent,self) # this is asynchronous, nothing more to do here
            return
        self.parent.msg(f"Your training with the {self.name} skill has improved your technique, but it will take some effort to get used to it.")
        self.training += 1 # todo
        self.effort=0
        self.exp=0
        return
    def affinity_up(self):
        if self.can_master:
            #todo separate mechanism
            self.mastery_up()
            return
        else:
            if self.aspect == None:
                if self.parent.skills.training == None:
                    self.parent.skills.training = self
                    link_skill_to_aspect(self.parent,self)
                else:
                    self.parent.msg(f"Bug: skillcore.training is set to {self.parent.skills.training.name} during {self.name} affinity linking")
                return
            self.affinity += 1
            self.parent.msg(f"Your affinity with the {self.name} skill increases to {self.affinity}.")
            self.parent.msg("You will have to start your training over from scratch.")
        self.training = 0
        self.effort=0
        self.exp=0
    def mastery_up(self):
        # Todo: Select some mechanism here, most likely a permanent unlock or circumstantial bonus
        self.mastery += 1
        self.affinity = 0
        self.training = 0
        self.effort=0
        self.exp=0
        self.parent.msg(f"You feel your mastery with the {self.name} skill increase to {self.mastery}")
        self.parent.msg("You will need to gain affinity with this skill all over again.")
        
#endregion
