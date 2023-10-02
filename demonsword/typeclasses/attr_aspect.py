"""
    Stat and Aspect wrappers
    
    Each character stat is associated with two Aspects (except Luck)
"""
from util.random import roll
from random import randint,choice
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
    if with_aspects and with_values:
        return f"""| XP:{with_values.exp.__str__().rjust(6)} | LV:{with_values.level.__str__().rjust(6)} |
| LUC | BOD | MND | SPR |
| {with_values.PADSTR('luc')} | {with_values.PADSTR('bod')} | {with_values.PADSTR('mnd')} | {with_values.PADSTR('spr')} |
| POW | STR | INT | WIL |
| {with_values.PADSTR('pow')} | {with_values.PADSTR('str')} | {with_values.PADSTR('int')} | {with_values.PADSTR('wil')} |
| FIN | DEX | WIT | PER |
| {with_values.PADSTR('fin')} | {with_values.PADSTR('dex')} | {with_values.PADSTR('wit')} | {with_values.PADSTR('per')} |
| CAP | STM | MEM | AUR |
| {with_values.PADSTR('cap')} | {with_values.PADSTR('stm')} | {with_values.PADSTR('mem')} | {with_values.PADSTR('aur')} |
| RES | CON | STB | WIS |
| {with_values.PADSTR('res')} | {with_values.PADSTR('con')} | {with_values.PADSTR('stb')} | {with_values.PADSTR('wis')} |
| AES | BEA | SAN | GRA |
| {with_values.PADSTR('aes')} | {with_values.PADSTR('bea')} | {with_values.PADSTR('san')} | {with_values.PADSTR('gra')} |
| HEA |  HP |  MP |  SP |
| {with_values.PADSTR('hea')} | {with_values.PADSTR('hp')} | {with_values.PADSTR('mp')} | {with_values.PADSTR('sp')} |"""
    if with_values:
        return f"""| XP:{with_values.exp.__str__().rjust(6)} | LV:{with_values.level.__str__().rjust(6)} |
| STR | INT | WIL |
| {with_values.PADSTR('str')} | {with_values.PADSTR('int')} | {with_values.PADSTR('wil')} |
| DEX | WIT | PER |
| {with_values.PADSTR('dex')} | {with_values.PADSTR('wit')} | {with_values.PADSTR('per')} |
| STM | MEM | AUR |
| {with_values.PADSTR('stm')} | {with_values.PADSTR('mem')} | {with_values.PADSTR('aur')} |
| CON | STB | WIS |
| {with_values.PADSTR('con')} | {with_values.PADSTR('stb')} | {with_values.PADSTR('wis')} |
| BEA | SAN | GRA |
| {with_values.PADSTR('bea')} | {with_values.PADSTR('san')} | {with_values.PADSTR('gra')} |
|  HP |  MP |  SP |
| {with_values.PADSTR('hp')} | {with_values.PADSTR('mp')} | {with_values.PADSTR('sp')} |"""
    if with_aspects:
        return f"""| LUC | BOD | MND | SPR |
| POW | STR | INT | WIL |
| FIN | DEX | WIT | PER |
| CAP | STM | MEM | AUR |
| RES | CON | STB | WIS |
| AES | BEA | SAN | GRA |
| HEA |  HP |  MP |  SP |"""
    if include_health:
        return f"""| STR | INT | WIL |
| DEX | WIT | PER |
| STM | MEM | AUR |
| CON | STB | WIS |
| BEA | SAN | GRA |
|  HP |  MP |  SP |"""
    return f"""| STR | INT | WIL |
| DEX | WIT | PER |
| STM | MEM | AUR |
| CON | STB | WIS |
| BEA | SAN | GRA |"""

# ---

class Stat:
    """
        A Stat class is a wrapper around Evennia attribute dictionary.
    """
    def __init__(self,character,key:str):
        self.parent = character
        self.core   = character.stats
        self.key    = key
        if not (key in AttributeList):
            raise Exception(f"Not a stat: {key}")
        self._load()
        
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
    def _load(self):
        """
            Internal: Load data from Evennia attribute dictionary
        """
        self.data = self.core.attributes.get(self.key,category="stats",
            default={"bonus":0,"exp":0,"stress":0} )
        self.col_key, self.row_key = AttributeToAspects(self.key) # I love python :)
        self.col = self.core[self.col_key]
        self.row = self.core[self.row_key]
        
    def _save(self):
        """
            Internal: Save data to EVennia attribute dictionary
        """
        self.core.attributes.add(self.key,self.data,category="stats")
    
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
                    self.parent.msg(f"Your {self.col.name} aspect is full.  Perhaps you should rest.")
                else:
                    self.parent.msg(f"Your {self.col.name} is more experienced.")
                self.col._save()
        if self.row.can_exercise:
            base = self.row.exp // 1
            self.row.exp += amt * row_mult
            newbase = self.row.exp // 1
            if newbase > base:
                if not self.row.can_exercise:
                    self.row.exp = newbase
                    self.parent.msg(f"Your {self.row.name} aspect is full.  Perhaps you should rest.")
                else:
                    self.parent.msg(f"Your {self.row.name} is more experienced.")
                self.row._save()
    # Attribute exp into bonus increase
    def Improve(self):
        self.exp = 0
        self.bonus += 1
        self._save()
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
    def bonus(self):
        return self.data["bonus"]
    @bonus.setter
    def bonus(self,b):
        self.data["bonus"] = b
        self._save()
    @property
    def stress(self):
        return self.data["stress"]
    @stress.setter
    def stress(self,s):
        self.data["stress"] = s
        self._save()
    @property
    def overstressed(self):
        return self.stress > self.bonus
    @property
    def exp(self):
        return self.data["exp"]
    @exp.setter
    def exp(self,e):
        self.data["exp"]=e
        self._save()
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

class Aspect:
    """
        Handler/wrapper for aspect rows/columns
    """
    key=None
    type=None # row or col
    related=[] # stats
    data=None # { bonus:int,exp:int }
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
        self._load()
    def __str__(self):
        return self.data.__str__()
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
            self.parent.msg(f"You feel like your {self.name} aspect is at full capacity!")
            return
        while len(candidates)>0 and self.exp > 0:
            n = randint(0,len(candidates)-1)
            c = candidates[n]
            c.exp += 1
            c._save()
            self.exp -= 1
            if not c.can_exercise: # now full
                candidates.remove(c)
                self.parent.msg(f"Your {c.name} feels full.  Maybe you should sleep it off.")
                if len(candidates) == 0:
                    return # give message next time
        self._save()
    
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
    def bonus(self):
        return self.data["bonus"]
    @bonus.setter
    def bonus(self,b):
        self.data["bonus"]=b
        #self._save()
    @property
    def value(self): # For compatability.  For stats, value = bonus + aspects.
        return self.data["bonus"]
    @property
    def exp(self):
        return self.data["exp"]
    @exp.setter
    def exp(self,e):
        self.data["exp"]=e
        #self._save()
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
