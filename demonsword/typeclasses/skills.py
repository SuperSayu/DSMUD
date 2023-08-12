"""
    Skills are attached to characters and are referenced by items and skill challenges.
    Actions that exercise a skill increase its practice
    
    Use the skills category to store skill dicts
    skill: { key: string, attribute: string|null, aspect: string|null, exp:int, effort:int, training:int, mastery:int, affinity:int }
"""
from evennia.objects.objects import DefaultObject
from .objects import ObjectParent
from .dice import roll,show_roll
from .attr_aspect import AttributeList,AspectList,StatGrid
from random import randint
from evennia.utils.evmenu import get_input # caller, prompt, callback, *args, **kwargs
# Increment when revised
SKILLS_VERSION = 0.1

def link_skill_to_stat(caller,skill):
    caller.msg("You need to pick a primary stat to use for this skill.  Choose one from this grid:")
    caller.msg(StatGrid(with_aspects=False,include_health=False))
    get_input(caller,"Which one?",link_skill_stat_callback,None,**{"skill":skill})
def link_skill_stat_callback(caller,prompt,response,skill):
    response = response.strip().lower()
    if not response in AttributeList:
        caller.msg("Ok, maybe later.")
        caller.skills.training = None
        caller.msg("You finish training.")
        return
    skill.stat = response
    caller.msg(f"You link the {skill.name} skill to the {response} stat.")
    skill.train_up()
    caller.skills.training = None
    caller.msg("You finish training.")

class Skill:
    parent      = None
    key         = ""
    data        = None

#region internals    
    def __init__(self, character, key, data=None):
        self.parent = character
        self.key = key
        if data == None:
            self._load()
        else: # Override used when the skill core needs to pull all skills, no use redoing queries
            self.data = data
    def __str__(self): # todo pretty print
        return self.data.__str__()
    def _save(self):
        self.parent.attributes.add(self.key,self.data,category="skills")
    def _load(self):
        self.data = self.parent.attributes.get(self.key,category="skills",default={"key":self.key,"name":self.key,"stat":None,"aspect":None,"tags":None,"exp":0,"effort":0,"training":0,"affinity":0,"mastery":0})
        # todo: lookup tags on first set
    def _reset(self):
        self.parent.attributes.remove(self.key,category="skills")
        self._load()
#endregion

    def Check(self,challenge):
        stat = 0
        if self.stat != None:
            stat = self.parent.stats[self.stat].value
        
        return show_roll(self.parent,self.name,d4=self.data["effort"], d6=stat, d8=self.data["training"],d10=self.data["affinity"],d12=self.data["mastery"]) - challenge

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
        return self.data["name"]
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
    def can_train(self):
        return self.effort == (self.training+1)
    @property
    def can_meditate(self):
        return self.training == (self.affinity+1)
#endregion

#region advancement
    def practice(self,amt):
        # The amount of exp you can have before resting is capped by your current effort in a skill
        if self.exp < self.effort+1:
            self.parent.msg("Your skill feels more experienced.")
            self.exp += 1
            self._save()
    def Rest(self):
        if self.exp < (self.effort+1):
            return
        self.effort_up()
        self._save()
    def effort_up(self):
        if self.can_train: # Maxed on effort
            if self.can_meditate:
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
            #self.affinity_up()
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
    def affinity_up(self):
        if self.affinity == self.mastery + 1:
            self.mastery_up()
        else:
            self.parent.msg(f"Your affinity with the {self.name} skill increase")
            self.parent.msg("You will have to start your training over from scratch.")
            self.affinity += 1
        self.training = 0
        self.effort=0
        self.exp=0
    def mastery_up(self):
        self.parent.msg(f"You feel your mastery with the {self.name} skill increase")
        self.parent.msg("You will need to gain affinity with this skill again.")
        self.mastery += 1 # todo
        self.affinity = 0
#endregion
