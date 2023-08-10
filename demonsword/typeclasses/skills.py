"""
    Skills are attached to characters and are referenced by items and skill challenges.
    Actions that exercise a skill increase its practice
    
    Use the skills category to store skill dicts
    skill: { key: string, attribute: string|null, aspect: string|null, exp:int, effort:int, training:int, mastery:int, affinity:int }
"""
from evennia.objects.objects import DefaultObject
from .objects import ObjectParent
from .dice import roll
from random import randint

# Increment when revised
SKILLS_VERSION = 0.1

class Skill:
    parent      = None
    key         = ""
    data        = None
    
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
        self.data = self.parent.attributes.get(self.key,category="skills",default={"key":self.key,"name":self.key,"attribute":None,"aspect":None,"tags":None,"exp":0,"effort":0,"training":0,"affinity":0,"mastery":0})
        # todo: lookup tags on first set
        
    def practice(self,amt):
        # The amount of exp you can have before resting is capped by your current effort in a skill
        if self.data["exp"] < self.data["effort"]+1:
            self.parent.msg("You feel more experienced.")
            self.data["exp"] += 1
            self._save()
    def Rest(self):
        if self.data["exp"] < (self.data["effort"]+1):
            return
        self.effort_up()
        self._save()
    def effort_up(self):
        if self.data["effort"] == self.data["training"] + 1:
            self.train_up()
        else:
            self.parent.msg(f"You feel your efforts with the {self.data['name']} skill increase")
            self.data["effort"] += 1
        self.data["exp"] = 0
    def train_up(self):
        if self.data["training"] == self.data["affinity"] + 1:
            self.affinity_up()
        else:
            self.parent.msg(f"You feel your training with the {self.data['name']} skill increase")
            self.data["training"] += 1 # todo
        self.data["effort"] = 0
    def affinity_up(self):
        if self.data["affinity"] == self.data["mastery"] + 1:
            self.mastery_up()
        else:
            self.parent.msg(f"You feel your affinity with the {self.data['name']} skill increase")
            self.data["affinity"] += 1
        self.data["training"] = 0
        
    def mastery_up(self):
        self.parent.msg(f"You feel your mastery with the {self.data['name']} skill increase")
        self.data["mastery"] += 1 # todo
        
    def Check(self,challenge):
        return roll(d4=self.data["effort"],d8=self.data["training"],d10=self.data["affinity"],d12=self.data["mastery"]) - challenge
    