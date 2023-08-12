"""
    Stat and Aspect wrappers
    
    Each character stat is associated with two Aspects (except Luck)
"""
from .dice import roll
from random import randint
AspectList = [
    "bod","mnd","spr", # Columns
    "pow","fin","end","res","aes","hea", # Rows
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
    "pow":"Power","fin":"Finesse","end":"Endurance",
    "res":"Resillience","aes":"Aesthetics","hea":"Health",
    "luc":"Luck",
    "str":"Strength","dex":"Dexterity","stm":"Stamina",
    "con":"Constitution","bea":"Beauty","hp":"Heath Points",
    "int":"Intelligence","wit":"Wit","mem":"Memory",
    "stb":"Stability","san":"Sanity","mp":"Mind Points",
    "wil":"Willpower","per":"Perception","aur":"Aura",
    "wis":"Wisdom","gra":"Grace","sp":"Spirit Points"
}
def AttributeToAspects(attr:str) -> list[str]:
    """
        Helper: Returns the two aspect keys associated with an attribute, or [luc,luc] on error.
    """
    try:
        i = AttributeList.index(attr)
        col = i//6
        row = i%6 + 3
        return [AspectList[col],AspectList[row]]
    except:
        return ["luc","luc"]
def StatGrid(with_aspects=True,include_health=True,with_values=None,):
    if with_aspects and with_values:
        return f"""| XP:{with_values.exp.__str__().rjust(6)} | LV:{with_values.level.__str__().rjust(6)} |
| LUC | BOD | MND | SPR |
| {with_values.PADSTR('luc')} | {with_values.PADSTR('bod')} | {with_values.PADSTR('mnd')} | {with_values.PADSTR('spr')} |
| POW | STR | INT | WIL |
| {with_values.PADSTR('pow')} | {with_values.PADSTR('str')} | {with_values.PADSTR('int')} | {with_values.PADSTR('wil')} |
| FIN | DEX | WIT | PER |
| {with_values.PADSTR('fin')} | {with_values.PADSTR('dex')} | {with_values.PADSTR('wit')} | {with_values.PADSTR('per')} |
| END | STM | MEM | AUR |
| {with_values.PADSTR('end')} | {with_values.PADSTR('stm')} | {with_values.PADSTR('mem')} | {with_values.PADSTR('aur')} |
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
| END | STM | MEM | AUR |
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
class Stat:
    """
        A Stat class is a wrapper around the internal data dict
        stat { "bonus":int, "exp":int <= (bonus+1), row: Apsect, col: Aspect }
    """
    def __init__(self,character,key):
        self.parent = character
        self.key    = key
        if not (key in AttributeList):
            raise Exception(f"Not a stat: {key}")
        self._load()
    def __str__(self):
        return self.data.__str__()
    def _load(self):
        self.data = self.parent.attributes.get(self.key,default={"bonus":0,"exp":0},category="stats")
        [self.col,self.row] = AttributeToAspects(self.key) # I love python :)
        
    def _save(self):
        self.parent.attributes.add(self.key,self.data,category="stats")
    
    # Exercising a stat actually either exercises the row or column.
    # When you rest, the exp is distributed randomly.  Full stats improve with sleep.
    def Exercise(self):
        if randint(0,1)==0:
            if self.col.can_exercise:
                self.col.exp += 1
                self.col._save()
                self.parent.msg(f"Your {self.col.name} is more experienced.")
            else:
                self.parent.msg(f"Your {self.col.name} is full.")
        else:
            if self.row.can_exercise:
                self.row.exp += 1
                self.row._save()
                self.parent.msg(f"Your {self.row.name} is more experienced.")
            else:
                self.parent.msg(f"Your {self.row.name} is full.")
    # Attribute exp into bonus increase
    def Improve(self):
        self.exp = 0
        self.bonus += 1
        self._save()
        self.parent.msg(f"Your {self.name} gets better.")
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
    def can_exercise(self):
        return self.exp < (self.bonus + 1)
    @property
    def can_improve(self):
        return self.exp == (self.bonus+1) and self.bonus < (self.col.bonus + self.row.bonus + 1)

class Aspect:
    """
        Handler/wrapper for aspect rows/columns
    """
    key=None
    type=None # row or col
    related=[] # stats
    data=None # { bonus:int,exp:int }
    def __init__(self,character,key):
        self.parent=character
        self.key=key
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
        self.data = self.parent.attributes.get(self.key,category="stats",default={"bonus":0,"exp":0})
    def _save(self):
        self.parent.attributes.add(self.key,self.data,category="stats")
    
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
    def exp(self):
        return self.data["exp"]
    @exp.setter
    def exp(self,e):
        self.data["exp"]=e
    @property
    def can_exercise(self):
        return self.exp < (self.bonus + 1)
    @property
    def name(self):
        return StatNames[self.key]
    @property
    def Stats(self):
        for i in self.related:
            yield self.parent.stats[i]
