"""
    Stat and Aspect wrappers
    
    Each character stat is associated with two Aspects (except Luck)
"""
from util.random import roll
from random import randint,choice
from evennia.utils.evtable import EvTable
from util.AttributeProperty import AttributeProperty,SubProperty
AspectList = [
    "bod","mnd","spr", # Columns
    "pow","fin","cap","res","aes","hea", # Rows
    "luc" # Luck is luck
]
AttributeList = [
    "str","dex","stm","con","bea","hp",
    "int","wit","mem","stb","san","mp",
    "wil","per","aur","wis","gra","sp"
]
ValidStatIndex = AspectList + AttributeList
StatNames = {
    "bod":"Body","mnd":"Mind","spr":"Spirit",
    "pow":"Power","fin":"Finesse","cap":"Capacity",
    "res":"Resillience","aes":"Aesthetics","hea":"Health",
    "luc":"Luck",
    "str":"Strength","dex":"Dexterity","stm":"Stamina",
    "con":"Constitution","bea":"Beauty","hp":"Health Points",
    "int":"Intelligence","wit":"Wit","mem":"Memory",
    "stb":"Stability","san":"Sanity","mp":"Mind Points",
    "wil":"Willpower","per":"Perception","aur":"Aura",
    "wis":"Wisdom","gra":"Grace","sp":"Spirit Points"
}
def AttributeToAspects(attr:str) -> tuple[str,str]:
    """
        Helper: Returns the two aspect keys associated with an attribute, or (luc,luc) on error.
    """
    try:
        i = AttributeList.index(attr)
        col = i//6
        row = i%6 + 3
        return (AspectList[col],AspectList[row])
    except:
        return ("luc","luc")
def AttributeToAspectsIndex(attr:str) -> tuple[int,int]:
    try:
        i = AttributeList.index(attr)
        col = i//6
        row = i%6 + 3
        return (col,row)
    except:
        return (-1,-1)    

stat_default = {"bonus":0,"exp":0,"stress":0}

class StatAttribute(AttributeProperty):
    _attr_get_source = lambda _, instance: instance.core.attributes
    _key_get = lambda _,instance: instance.key
    _data_default = stat_default
    _category="stats"

class Stat:
    """
        A Stat class is a wrapper around Evennia attribute dictionary.
    """
    data = StatAttribute()
    bonus = SubProperty()
    exp = SubProperty()
    stress = SubProperty()
    stat_full_hint="|CYour |w{name}|C Stat feels full.  Maybe you should |yrest|C.|n"
    
    def __init__(self,character,key:str):
        self.parent = character
        self.core   = character.stats
        self.key    = key
        if not (key in AttributeList):
            raise Exception(f"Not a stat: {key}")
        self.col_key, self.row_key = AttributeToAspects(self.key) # I love python :)
        self.col = self.core[self.col_key]
        self.row = self.core[self.row_key]
        
    def __str__(self):
        """
            Debug: Returns string representation of Evennia attribute dictionary
        """
        return self.data.__str__()
    def __int__(self):
        """
        int(Stat) is its value
        """
        return self.value

    def Exercise(self,skill, amt):
        """
        """
        (stat_mult,col_mult,row_mult) = (0.2,0.1,0.1)
        if self.can_improve: # Stat capped on exp, redistribute without bias, with a little loss:
            (stat_mult,col_mult,row_mult) = (0, 0.15, 0.15)
        # if the skill is placed in a stance, distribute xp with bias and a little advantage:
        if skill.aspect == self.col_key:
            col_mult += row_mult * .75 + stat_mult * .25
            row_mult *= .375
            stat_mult *= .875
        elif skill.aspect == self.row_key:
            row_mult += col_mult * .75 + stat_mult * .25
            col_mult * .375
            stat_mult *= .875
            
        self.add_xp(stat_mult * amt)
        self.col.add_xp(col_mult * amt)
        self.row.add_xp(row_mult * amt)
            
    # Attribute exp into bonus increase
    def Improve(self):
        self.exp = 0
        self.bonus += 1
        self.parent.msg(f"Your {self.name} gets better.")
    def Rest(self):
        self.stress = 0
    def Sleep(self):
        self.stress = 0
        if self.can_improve:
            self.Improve()
    @property
    def name(self):
        return StatNames[self.key]
    
    @property
    def overstressed(self):
        return self.stress > self.bonus
    @property
    def value(self):
        return self.bonus + self.row.bonus + self.col.bonus
    @property
    def can_rest(self):
        return self.stress > 0
    @property
    def can_exercise(self):
        return self.exp < (self.bonus + 1)
    @property
    def can_improve(self):
        return self.exp >= (self.bonus+1) and self.bonus < (self.col.bonus + self.row.bonus + 3)
    def add_xp(self,amt):
        if self.exp == self.bonus + 1:
            return
        self.exp = min(self.exp + amt, self.bonus + 1)
        if self.exp == self.bonus + 1:
            self.parent.msg(self.stat_full_hint.format(name = self.name))

aspect_default = {"bonus":0,"exp":0}
class AspectAttribute(StatAttribute):
    _data_default = aspect_default
    
class Aspect:
    """
        Handler/wrapper for aspect rows/columns
    """
    key=None
    type=None # row or col
    related=[] # stats
    #data=None # { bonus:int,exp:int }
    data = AspectAttribute()
    bonus = SubProperty()
    exp = SubProperty()
    xp_full_hint = "|cYour |w{name}|c Aspect feels full.  Perhaps you should |ysleep|c it off.|n"
    stat_full_hint="|CYour |w{name}|C Stat feels full.  Maybe you should |yrest|C.|n"
    aspect_full_hint="|CYou feel like your |w{name}|C Aspect is at full capacity!|n"
    def __init__(self,character,key):
        self.parent = character
        self.core   = character.stats
        self.key    = key
        if not (key in AspectList):
            raise Exception(f"Not an aspect: {key}")
            
        # Getting the related list is actually really easy as long as the lists above are correct
        index = AspectList.index(key)
        if key == 'luc': # ignore the index, luck aspect is luck attribute and of luck type
            self.type = key
            self.related = []
        elif index < 3: # column aspect
            self.type = 'col'
            self.related = AttributeList[index*6:(index+1)*6]
        else:
            self.type = 'row'
            index -= 3 # get position relative to start of row aspects
            self.related = AttributeList[index::6] #index, index+6, index+12 eg 0(str), 6(int),12(wil)
#        self._load()
    def __str__(self):
        return self.data.__str__()
    def __int__(self):
        return self.bonus
    def _load(self):
        self.data = self.core.attributes.get(self.key,category="stats",default={"bonus":0,"exp":0})
    def _save(self):
        self.core.attributes.add(self.key,self.data,category="stats")
    
    # Resting: Distribute experience to children
    def Rest(self):
        if len(self.related) == 0:
            return # luck
        if self.exp == 0:
            return
        candidates=[]
        for s in self.Stats:
            if s.can_exercise:
                candidates.append(s)
        if len(candidates) == 0:
            self.parent.msg(aspect_full_hint.format(name=self.name))
            return
        while len(candidates)>0 and self.exp > 0:
            n = randint(0,len(candidates)-1)
            c = candidates[n]
            c.exp += 1
            #c._save()
            self.exp -= 1
            if not c.can_exercise: # now full
                candidates.remove(c)
                self.parent.msg(self.stat_full_hint.format(name=c.name))
                if len(candidates) == 0:
                    return # give message next time
        #self._save()
    
    def improve(self,skill):
        self.parent.msg(f"Because of your {skill.name} skill, your {self.name} Aspect has increased to {self.bonus+1}")
        self.bonus += 1
        for i in self.Stats:
            i.bonus -= self.bonus
    
    # Sleeping: Attribute xp into bonus increase
    # Todo this is a dumb way of doing it Vincent wtf man seriously
    def Sleep(self):
        for s in self.Stats:
            if s.can_improve:
                s.Improve()
    def add_xp(self,amt):
        cap = self.bonus + 2
        if self.exp == cap:
            return
        self.exp = min(self.exp + amt, cap)
        if self.exp == cap:
            self.parent.msg(self.xp_full_hint.format(name=self.name))
    @property
    def value(self): # For compatability.  For stats, value = bonus + aspects.
        return self.data["bonus"]
    @property
    def can_exercise(self):
        return not self.can_rest
    @property
    def can_rest(self):
        return self.exp >= (self.bonus+2)
    @property
    def can_improve(self):
        for i in self.Stats:
            if i.bonus < (self.bonus+1):
                return False
        return True
    @property
    def name(self):
        return StatNames[self.key]
    @property
    def Stats(self):
        for i in self.related:
            yield self.parent.stats[i]
