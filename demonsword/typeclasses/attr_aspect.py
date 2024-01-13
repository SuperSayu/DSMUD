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
        
def StatGrid(with_aspects=True,include_health=True,with_values=None) -> str:
    table=[]
    cols=[['luc','pow','fin','cap','res','aes','hea'],['bod','str','dex','stm','con','bea','hp'],['mnd','int','wit','mem','stb','san','mp'],['spr','wil','per','aur','wis','gra','sp']]
    if not include_health:
        del cols[0][-1], cols[1][-1], cols[2][-1], cols[3][-1]
    if not with_aspects:
        del cols[0], cols[0][0], cols[1][0], cols[2][0]
    if not with_values:
        table = cols
    else:
        for col in cols:
            c = []
            for r in col:
                if with_aspects and (r in AspectList):
                    c.extend( [f"|w{r.upper()}|n", f"|c{with_values[r].value}|n" ] )
                else:
                    c.extend( [r.upper(), f"|y{with_values[r].value}|n" ] )
            table.append( c )
    return EvTable(table=table,pad_width=0,pad_left=2,pad_right=2,align='c')

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
    
    # Exercising a stat actually either exercises the row or column.
    # When you rest, the exp is distributed randomly.  Full stats improve with sleep.
    def Exercise(self,skill, amt):
        """
        """
        (col_mult,row_mult) = (0.5,0.5)
        if skill and skill.aspect != None:
            if skill.aspect == self.col:
                (col_mult,row_mult) = (0.75,0.25)
            else:
                (col_mult,row_mult) = (0.25,0.75)
        amt = pow(0.5,amt)
        if self.col.can_exercise:
            base = self.col.exp // 1
            self.col.exp += amt * col_mult
            newbase = self.col.exp // 1
            if newbase > base:
                if not self.col.can_exercise:
                    self.col.exp = newbase
                    self.parent.msg(f"|CYour |w{self.col.name}|C aspect is full.  Perhaps you should |yrest|C.|n")
                else:
                    self.parent.msg(f"Your {self.col.name} is more experienced.")
        if self.row.can_exercise:
            base = self.row.exp // 1
            self.row.exp += amt * row_mult
            newbase = self.row.exp // 1
            if newbase > base:
                if not self.row.can_exercise:
                    self.row.exp = newbase
                    self.parent.msg(f"|CYour |w{self.row.name}|C aspect is full.  Perhaps you should |yrest|C.|n")
                else:
                    self.parent.msg(f"Your {self.row.name} is more experienced.")
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
    
    # Resting: Distribute experience to child 
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
            self.parent.msg(f"|CYou feel like your |w{self.name}|C aspect is at full capacity!|n")
            return
        while len(candidates)>0 and self.exp > 0:
            n = randint(0,len(candidates)-1)
            c = candidates[n]
            c.exp += 1
            #c._save()
            self.exp -= 1
            if not c.can_exercise: # now full
                candidates.remove(c)
                self.parent.msg(f"|CYour |w{c.name}|C feels full.  Maybe you should |ysleep|C it off.|n")
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
    
    @property
    def value(self): # For compatability.  For stats, value = bonus + aspects.
        return self.data["bonus"]
    @property
    def can_exercise(self):
        return self.exp < (self.bonus + 2)
    @property
    def can_rest(self):
        return self.exp == (self.bonus+2)
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
