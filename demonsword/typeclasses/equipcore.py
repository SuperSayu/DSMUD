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
    def show(self):
        """
        Display inventory to self.  Called by inventory command.
        """
        r=self.hand_r
        l=self.hand_l
        self.parent.msg("You are carrying:")
        if r == None and l == None:
           self.parent.msg("Nothing.")
           return
        if r != None:
           self.parent.msg(f"In your right hand, a {r}.")
        if l != None:
           self.parent.msg(f"In your left hand, a {l}.")
        pass
    def pickup(self,item):
        if not isinstance(item,Item) or not item.portable:
            self.parent.msg(f"You can't get the {item}.")
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
    def drop(self,item):
        if item == self.main_hand:
           self.main_hand = None
           item.move_to(self.parent.location,quiet=True)
           self.parent.msg(f"You drop the |w{item}|n.")
           self.parent.location.msg_contents("|w{person}|n drops a |w{item}|n.",mapping={"person":self.parent,"item":item},exclude=(self.parent) )
           return True
        elif item == self.off_hand:
           self.off_hand = None
           item.move_to(self.parent.location,quiet=True)
           self.parent.msg(f"You drop the |w{item}|n.")
           self.parent.location.msg_contents("|w{person}|n drops a |w{item}|n.",mapping={"person":self.parent,"item":item},exclude=(self.parent) )
           return True
        else:
           self.parent.msg("You aren't carrying that.")
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
    def swap_hands(self):
       l,r = self.hand_l, self.hand_r
       if l:
          if r:
             self.parent.attributes.add("hand_l",r,category="equip")
             r.at_reequip(self.parent,"hand_l")
          else:
            self.parent.attributes.add("hand_l",None,category="equip")
          self.parent.attributes.add("hand_r",l,category="equip")
          l.at_reequip(self.parent,"hand_r")
       elif r:
          self.parent.attributes.add("hand_l",r,category="equip")
          r.at_reequip(self.parent,"hand_l")
          self.parent.attributes.add("hand_r",None,category="equip")
       else:
          self.parent.msg("Your hands are empty!")
          return
       self.parent.msg("You swap the items in your hands around.")
    
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
            if item == None:
               self.hand_l.at_unequip(self.parent)
               self.parent.attributes.add("hand_l",None,category="equip")
            return
        if not isinstance(item,Item) or not item.portable:
            return
        if item.db.slot != None:
            item.at_unequip(self.parent)
        ol = item.location
        item.move_to(self.parent,quiet=True)
        self.parent.attributes.add("hand_l",item,category="equip")
        item.at_equip(self.parent,"hand_l")
        self.parent.msg(f"You pick up the |w{item}|n with your |wleft|n hand.")
        if ol != self.parent:
           ol.msg_contents("|w{person}|n picks up the |w{item}|n",mapping={"person":self.parent,"item":item},exclude=(self.parent) )
# Right hand
    @property
    def hand_r(self):
        return self.parent.attributes.get("hand_r",category="equip",default=None)
    @hand_r.setter
    def hand_r(self,item):
        if self.hand_r != None:
            if item == None:
                 self.hand_r.at_unequip(self.parent)
                 self.parent.attributes.add("hand_r",None,category="equip")
            return
        if not isinstance(item,Item) or not item.portable:
            return
        if item.db.slot != None:
            item.at_unequip(self.parent)
        ol = item.location
        item.move_to(self.parent,quiet=True)
        self.parent.attributes.add("hand_r",item,category="equip")
        item.at_equip(self.parent,"hand_r")
        self.parent.msg(f"You pick up the |w{item}|n with your |wright|n hand.")
        if ol != self.parent:
           ol.msg_contents("|w{person}|n picks up the |w{item}|n.",mapping={"person":self.parent,"item":item},exclude=(self.parent) )
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
        if item.db.slot != None:
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
        if item.db.slot != None:
            item.at_unequip(self.parent)
        item.move_to(self.parent)
        self.parent.attributes.add("belt",item,category="equip")
        item.at_equip(self.parent,"belt")
#endregion