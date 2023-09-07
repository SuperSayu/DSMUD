"""
    The StatCore is intended to be a mixin that applies to player characters
    and contains attributes and aspects.  This is a lot to simulate,
    and NPCs only really need some basic values, so they get a fake version.
"""

from util.random import roll

from .attr_aspect import AttributeList,AspectList,ValidStatIndex,AttributeToAspects,Stat,Aspect
from typing import Union,Generator
# Increment when revised
STAT_VERSION = 0.1




class StatCore:
    """
        The StatCore implements indexing[] for stat indexes, both aspects and attributes
    """
    def __init__(self,parent):
        self.parent=parent
        self._load()
    
    def __getitem__(self, index:str) -> Aspect|Stat:
        """
            If the index matches a valid two or three character code, return the associated object.
            If not, raises an IndexError.  Valid codes are lowercase and found in attr_aspect.py
        """
        if not (index in ValidStatIndex):
            raise IndexError(f"'{index}' is not an Aspect or Stat code")
        if index in self.stats:
            return self.stats[index]
        if index in AspectList:
            temp = Aspect(self.parent,index)
            self.stats[index]=temp
            return temp
        temp = Stat(self.parent,index)
        self.stats[index]=temp
        return temp
    
    def PADSTR(self,x:str,width:int=3) -> str:
        """makes the number x padded to 3 characters, sorta"""
        n = self[x].value.__str__()
        return n.center(width,' ')
    
    def __str__(self) -> str:
        return f"""| |wXP:|n{self.exp.__str__().rjust(6)} | |wLV:|n{self.level.__str__().rjust(6)} |
| |wLUC|n | |wBOD|n | |wMND|n | |wSPR|n |
| {self.PADSTR('luc')} | {self.PADSTR('bod')} | {self.PADSTR('mnd')} | {self.PADSTR('spr')} |
| |wPOW|n | STR | INT | WIL |
| {self.PADSTR('pow')} | {self.PADSTR('str')} | {self.PADSTR('int')} | {self.PADSTR('wil')} |
| |wFIN|n | DEX | WIT | PER |
| {self.PADSTR('fin')} | {self.PADSTR('dex')} | {self.PADSTR('wit')} | {self.PADSTR('per')} |
| |wCAP|n | STM | MEM | AUR |
| {self.PADSTR('cap')} | {self.PADSTR('stm')} | {self.PADSTR('mem')} | {self.PADSTR('aur')} |
| |wRES|n | CON | STB | WIS |
| {self.PADSTR('res')} | {self.PADSTR('con')} | {self.PADSTR('stb')} | {self.PADSTR('wis')} |
| |wAES|n | BEA | SAN | GRA |
| {self.PADSTR('aes')} | {self.PADSTR('bea')} | {self.PADSTR('san')} | {self.PADSTR('gra')} |
| |wHEA|n |  HP |  MP |  SP |
| {self.PADSTR('hea')} | {self.PADSTR('hp')} | {self.PADSTR('mp')} | {self.PADSTR('sp')} |"""
    
    def show(self) -> None:
        self.parent.msg(self.__str__())
        
    def _load(self) -> None:
        """
            Internal: Import data from Evennia attributes
        """
        self.stats = self.parent.attributes.get(
            "stats",
            default={})
        self.exp = self.parent.attributes.get( "exp", default=0 )
        self.level = self.parent.attributes.get( "lvl", default=0 )
        
    def _save(self) -> None:
        """
            Internal: Save data to Evennia attributes
        """
        self.parent.db.add("stats",self.stats)
        self.parent.attributes.add("exp",self.exp)
        self.parent.attributes.add("lvl",self.level)
        
    def _reset(self) -> None:
        """
            Debug: Removes all character stats to return to base state
        """
        self.parent.attributes.clear(category="stats")
        self.parent.attributes.remove("exp") 
        while len(self.stats):
            (k,o) = self.stats.popitem()
            del o
        self.exp=0
        
    
    def Check(self,attribute) -> int:
        """
            Attempts an Attribute check.
        """
        pass

    @property
    def Aspects(self) -> Generator[Aspect,None,None]:
        """
            Returns all character Aspects (as the data structure Aspect)
        """
        for i in AspectList:
            yield self[i]
            
    @property
    def Stats(self) -> Generator[Stat,None,None]:
        """
            Returns all character Stats (as the data structure Stat)
        """
        for i in AttributeList:
            yield self[i]

    def Exercise(self, attr:str,skill, diff:int) -> None:
        """
            Attempts to give stress and experience to a stat.
        """
        stat = self[attr]
        stat.Exercise(skill,diff)
        
    def Rest(self) -> None:
        """
            Rest all stats and Aspects.
        """
        for A in self.Aspects:
            A.Rest()
            
    def Sleep(self) -> None:
        """
            Advanced rest for all stats and aspects.
        """
        for A in self.Aspects:
            A.Sleep()

