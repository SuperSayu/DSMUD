"""
    The StatCore is intended to be a mixin that applies to player characters
    and contains attributes and aspects.  This is a lot to simulate,
    and NPCs only really need some basic values, so they get a fake version.
"""

from util.AttributeProperty import AttributeProperty
from util.random import roll
from .attr_aspect import AttributeList,AspectList,ValidStatIndex,AttributeToAspects,Stat,Aspect,StatGrid
from .objects import Object
from typing import Union,Generator
# Increment when revised
STAT_VERSION = 0.1

class StatCore(Object):
    _content_types = ("internal",) # hide from object indexing
    
    stats   = {}#AttributeProperty({},category="stats")
    exp     = AttributeProperty(0)
    level   = AttributeProperty(0)    

    """
        The StatCore implements indexing[] for stat indexes, both aspects and attributes
    """
    lockstring="control:perm(Admin);view:none();get:none();drop:none();teleport:none();teleport_here:none();puppet:none();tell:none()"
    def at_init(self):
        if self.location != self.home:
            self.location = self.home
        self.parent=self.location
        self.key=f"({self.parent.key}.statcore)"
    def __contains__(self,index) -> bool:
        return index in ValidStatIndex
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
        """makes the number x padded to [width] characters, sorta"""
        n = self[x].value.__str__()
        return n.center(width,' ')
    
    def show(self) -> None:
        self.parent.msg(StatGrid(with_values=self))
    
    def _reset(self) -> None:
        """
            Debug: Removes all character stats to return to base state
        """
        self.attributes.clear(category="stats") 
        while len(self.stats):
            (k,o) = self.stats.popitem()
            del o
        self.exp=0
        self.level = 0
    
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

    def Exercise(self, attr:str, skill, diff:int) -> None:
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

