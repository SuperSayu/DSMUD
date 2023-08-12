"""
    The StatCore is intended to be a mixin that applies to player characters
    and contains attributes and aspects.  This is a lot to simulate,
    and NPCs only really need some basic values, so they get a fake version.
"""

from .dice import roll

from .attr_aspect import AttributeList,AspectList,ValidStatIndex,AttributeToAspects,Stat,Aspect
# Increment when revised
STAT_VERSION = 0.1




class StatCore:
    """
        The StatCore implements indexing[] for stat indexes, both aspects and attributes
    """
    def __init__(self,parent):
        self.parent=parent
        self._load()
    def __getitem__(self, index):
        if not (index in ValidStatIndex):
            return self['luc']
        if index in self.stats:
            return self.stats[index]
        if index in AspectList:
            temp = Aspect(self.parent,index)
            self.stats[index]=temp
            return temp
        temp = Stat(self.parent,index)
        self.stats[index]=temp
        return temp
    def PADSTR(self,x,width=3):
        """makes the number x padded to 3 characters, sorta"""
        n = self[x].bonus.__str__()
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
        self.parent.attributes.add("exp",self.exp)

    def Check(self,attribute) -> int:
        pass

    @property
    def Aspects(self):
        for i in AspectList:
            yield self[i]
    @property
    def Stats(self):
        for i in AttributeList:
            yield self[i]

    def getAspect(self, asp:str ) -> int:
        if asp in AspectList:
            return self.parent.db.stats.get(asp)
        return 0
    def getAttribute(self,attr:str) -> int:
        if attr in AttributeList:
            return self[attr].value
        # Todo log failure
        return 0
    def Exercise(self, attr:str, diff:int) -> int:
        if attr == None:
            return
        stat = self[attr]
        
        if diff >= stat.value:
            self.exp += 1
            self.parent.attributes.add("exp",self.exp)
            stat.Exercise()
    def Rest(self):
        for A in self.Aspects:
            A.Rest()
    def Sleep(self):
        for A in self.Aspects:
            A.Sleep()
    pass
