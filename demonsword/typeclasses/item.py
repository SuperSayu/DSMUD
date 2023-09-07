"""
    Items are a subclass of objects expected to be picked up.
    Equipment are a subclass of items designed to fit in slots.
    
    Ultiumately I want loot to be generated by tables that specify
    item families and quality levels, eg,
    
    * When foraging in a certain spot, generate one of the following:
        * Flower A at quality between 1-3
        * Plant B at quality 2-4
        * Mushroom C at quality 1-4 where quality 4 is a different subtype
        * Low chance of variants, only when quality is max
"""
from .objects import Object

class Item(Object):
    portable=True   # Overrides object/portable
    size = 0        # Determines what containers this can be stored in
    slot = None     # In case this item is currently held/worn, store where
    
    def at_equip(self,character, slot): # includes 
        self.slot = slot
    def at_unequip(self,character):
        self.slot = None
 
    
class Equipment(Item):
    pass