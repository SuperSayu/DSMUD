"""
    The StatCore is intended to be a mixin that applies to player characters
    and contains attributes and aspects.  This is a lot to simulate,
    and NPCs only really need some basic values, so they get a fake version.
"""

from .dice import roll

AspectList = [
    "bod","mnd","spr",
    "pow","fin","end","res","aes","hea",
    "luc"
]
AttributeList = [
    "str","dex","stm","con","bea","hp",
    "int","wit","mem","stb","san","mp",
    "wil","per","aur","wis","gra","sp"
]
ValidStatIndex = AspectList + AttributeList

# Increment when revised
STAT_VERSION = 0.1

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

class StatCore:
    """
        The StatCore implements indexing[] for stat indexes, both aspects and attributes
    """
    def __init__(self,parent):
        self.parent=parent
        self._load()
    def __getitem__(self, index):
        if not (index in ValidStatIndex):
            return 0
        try:
            return self.stats[index]
        except:
            self.stats[index]=0
            return 0 # Uninitialized means zero
    def PADSTR(self,x,width=3):
        """makes the number x padded to 3 characters, sorta"""
        n = self[x].__str__()
        return n.center(width,' ')
    def __str__(self):
        return f"""| XP:{self.exp.__str__().rjust(6)} | LV:{self.level.__str__().rjust(6)} |
| LUC | BOD | MND | SPR |
| {self.PADSTR('luc')} | {self.PADSTR('bod')} | {self.PADSTR('mnd')} | {self.PADSTR('spr')} |
| POW | STR | INT | WIL |
| {self.PADSTR('pow')} | {self.PADSTR('str')} | {self.PADSTR('int')} | {self.PADSTR('wil')} |
| FIN | DEX | WIT | PER |
| {self.PADSTR('fin')} | {self.PADSTR('dex')} | {self.PADSTR('wit')} | {self.PADSTR('per')} |
| END | STM | MEM | AUR |
| {self.PADSTR('end')} | {self.PADSTR('stm')} | {self.PADSTR('mem')} | {self.PADSTR('aur')} |
| RES | CON | STB | WIS |
| {self.PADSTR('res')} | {self.PADSTR('con')} | {self.PADSTR('stb')} | {self.PADSTR('wis')} |
| AES | BEA | SAN | GRA |
| {self.PADSTR('aes')} | {self.PADSTR('bea')} | {self.PADSTR('san')} | {self.PADSTR('gra')} |
| HEA |  HP |  MP |  SP |
| {self.PADSTR('hea')} | {self.PADSTR('hp')} | {self.PADSTR('mp')} | {self.PADSTR('sp')} |"""
        
        
    def _load(self):
        """
        """
        self.stats = self.parent.attributes.get(
            "stats",
            default={})
        self.exp = self.parent.attributes.get( "exp", default=0 )
        self.level = self.parent.attributes.get( "lvl", default=0 )
    def _save(self):
        self.parent.db.add("stats",self.stats)

    def Check(self,attribute) -> int:
        pass

    def getAspect(self, asp:str ) -> int:
        if asp in AspectList:
            return self.parent.db.stats.get(asp)
        return 0
    def getAttribute(self,attr:str) -> int:
        if attr in AttributeList:
            asps = AttributeToAspects(attr)
            bonus = self.parent.db.stats.get(attr) + self.parent.db.stats.get(asps[0]) + self.parent.db.stats.get(asps[1])
            return bonus
        # Todo log failure
        return 0
    def exercise(self, attr:str, diff:int) -> int:
        attrVal = self.getAttr(attr)
        if diff >= attrVal:
            self.exp += 1
            self.parent.db.exp = self.exp
        pass
    pass
