"""
"""
from .item import Item
class EquipmentCore:
    parent=None
    default_hand = "r"
    def __init__(self,character):
        self.parent = character
        self.default_hand = character.attributes.get("default_hand",default="r")
        self.non_default_hand = "l" if self.default_hand == "r" else "r"
        
    def pickup(self,item):
        if not isinstance(item,Item) or not item.portable:
            return False
        if item.location == self:
            return False
        if not item.access(self,access_tye="get",default=True):
            return False
        if not self.main_hand:
            self.main_hand = item
            return True
        if not self.off_hand:
            self.off_hand = item
            return True
        self.parent.msg("Your hands are full.")
        return
    def require(self,itemClass=Item,itemTags=[],manual=True,swap=False):
        """
            Finds an item in your equipment, hands, or quick item slots.
            Returns that item or None.
            The item must be of the selected class and have the selected tags.
            
            If Manual is True, you must have it in your hands or be able to
            immediately place it in your hands.
            
            If Swap is true and the item is immediately accessible
            place it in your hands, swapping out a currently held item instead.
        """
        
        candidates=[]
        if manual:
            candidates=[self.main_hand,self.off_hand]
        else:
            candidates = self.slots
        for c in candidates:
            if not isInstance(c,itemClass):
                continue
            
        return None
    
#region slots
    @property
    def slots(self):
        return [ self.main_hand, self.off_hand, self.belt, self.back ]
# Hand shortcuts
    @property
    def main_hand(self):
        if self.default_hand == "r":
            return self.hand_r
        return self.hand_l
    @main_hand.setter
    def main_hand(self,item):
        if self.default_hand == "r":
            self.hand_r=item
        else:
            self.hand_l=item
    @property
    def off_hand(self):
        if self.default_hand == "r":
            return self.hand_l
        return self.hand_r
    @off_hand.setter
    def off_hand(self,item):
        if self.default_hand == "r":
            self.hand_l=item
        else:
            self.hand_r=item
    @property
    def free_hand(self):
        """
            Returns true if either hand is unoccupied.  Todo: injuries?
        """
        return not self.hand_r or not self.hand_l
        
# Left hand
    @property
    def hand_l(self):
        return self.parent.attributes.get("hand_l",category="equip",default=None)
        pass
    @hand_l.setter
    def hand_l(self,item):
        # These safety checks should be redundant
        if self.hand_l != None:
            return
        if not isinstance(item,Item) or not item.portable:
            return
        if item.slot != None:
            item.at_unequip(self.parent)
        item.move_to(self.parent)
        self.parent.attributes.add("hand_l",item,category="equip")
        item.at_equip(self.parent,"hand_l")
# Right hand
    @property
    def hand_r(self):
        return self.parent.attributes.get("hand_r",category="equip",default=None)
    @hand_r.setter
    def hand_r(self,item):
        if self.hand_r != None:
            return
        if not isinstance(item,Item) or not item.portable:
            return
        if item.slot != None:
            item.at_unequip(self.parent)
        item.move_to(self.parent)
        self.parent.attributes.add("hand_r",item,category="equip")
        item.at_equip(self.parent,"hand_r")
# Backpack        
    @property
    def back(self):
        return self.parent.attributes.get("back",category="equip",default=None)
    @back.setter
    def back(self,item):
        if self.back != None:
            return
        if not isinstance(item,Item) or not item.portable:
            return
        if item.slot != None:
            item.at_unequip(self.parent)
        item.move_to(self.parent)
        self.parent.attributes.add("back",item,category="equip")
        item.at_equip(self.parent,"back")
# Belt
    @property
    def belt(self):
        return self.parent.attributes.get("belt",category="equip",default=None)
    @belt.setter
    def belt(self,item):
        if self.belt != None:
            return
        if not isinstance(item,Item) or not item.portable:
            return
        if item.slot != None:
            item.at_unequip(self.parent)
        item.move_to(self.parent)
        self.parent.attributes.add("belt",item,category="equip")
        item.at_equip(self.parent,"belt")
#endregion