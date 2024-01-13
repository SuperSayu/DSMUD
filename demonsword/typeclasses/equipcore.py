"""
"""
from .item import Item
from evennia.utils.search import search_object
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
        worn = self.equip_slots
        not_worn = worn.count(None)
        self.parent.msg("|/You are |ywearing|n:")
        if not_worn == len(worn):
            self.parent.msg("* |yNothing.|n")
        else:
            for i in worn:
                if i == None:
                    continue
                if i.container:
                    def sub_show(item, lead="> ", allow_sub=True,):
                        sub = item.sub_containers
                        fast = item.fast_contents
                        more = len(sub) or len(fast)
                        withblock = ", with:" if more else ""
                        onblock = f"* On your |y{item.slot}|n, a" if item.slot else f"{lead}A"
                        self.parent.msg(f"{onblock} |w{item.get_display_name()}|n{withblock}")
                        if more:
                            if allow_sub:
                                for s in sub:
                                    sub_show(s,"- "+lead,allow_sub=False)
                            for f in fast:
                                if f in sub and allow_sub:
                                    continue
                                if f.location != item:
                                    continue
                                self.parent.msg(f"- {lead} A |w{f.get_display_name()}|n")
                    sub_show(i)
                    
                else:
                    self.parent.msg(f"* On your |y{i.db.slot}|n, a |w{i.get_display_name()}|n")
        self.parent.msg("|/")
        r=self.hand_r
        l=self.hand_l
        self.parent.msg("You are |ycarrying|n:")
        if r == None and l == None:
           self.parent.msg("* |yNothing.|n")
           return
        if r != None:
           self.parent.msg(f"* In your |yright hand|n, a |w{r.get_display_name()}|n.")
        if l != None:
           self.parent.msg(f"* In your |yleft hand|n, a |w{l.get_display_name()}|n.")
        self.parent.msg("|/")
    def pickup(self,item,silent=False):
        if not isinstance(item,Item) or not item.portable:
            if not silent:
                self.parent.msg(f"You can't get the {item}.")
            return False
        if item.location == self:
            return False
        if not item.access(self,access_type="get",default=True):
            return False
        if not item.at_before_get(self.parent):
            return False
        if not self.main_hand:
            self.main_hand = item
            item.at_get(self.parent)
            return True
        if not self.off_hand:
            self.off_hand = item
            item.at_get(self.parent)
            return True
        if not silent:
            self.parent.msg("Your hands are full.")
        return False
    def drop(self,item):
        if item == self.main_hand:
           if not item.at_before_drop(self.parent):
              return
           self.main_hand = None
           item.move_to(self.parent.location,quiet=True)
           item.at_drop(self.parent)
           self.parent.msg(f"You drop the |w{item}|n.")
           self.parent.location.msg_contents("|w{person}|n drops a |w{item}|n.",mapping={"person":self.parent,"item":item},exclude=(self.parent) )
           return True
        elif item == self.off_hand:
           if not item.at_before_drop(self.parent):
              return
           self.off_hand = None
           item.move_to(self.parent.location,quiet=True)
           item.at_drop(self.parent)
           self.parent.msg(f"You drop the |w{item}|n.")
           self.parent.location.msg_contents("|w{person}|n drops a |w{item}|n.",mapping={"person":self.parent,"item":item},exclude=(self.parent) )
           return True
        else:
           self.parent.msg("You aren't carrying that.")
    def require(self,itemClass=None,itemKey=None,itemTags=[],manual=True,ignore_hands=False,hands_only=False,swap=False):
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
        if hands_only:
            candidates = self.hands
        elif manual:
            candidates=self.fast_contents
        else:
            candidates = self.slots
            for item in self.containers:
                candidates.extend(item.contents)
        if ignore_hands:
            candidates.remove(self.main_hand)
            candidates.remove(self.off_hand)
        result= search_object(itemKey,typeclass=itemClass,candidates=candidates)
        if hasattr(result,"__iter__"):
            result = [*result]
        return result
        
    def swap_slots(self,slot_a="hand_l",slot_b="hand_r"):
        s = self.slot_names
        if (not slot_a in s) or (not slot_b in s):
            return None
        a,b = self.parent.attributes.get(slot_a,category="equip"),self.parent.attributes.get(slot_b,category="equip")
        if a:
            if b:
                self.parent.attributes.add(slot_a,b,category="equip")
                b.at_reequip(self.parent,slot_a)
            else:
                self.parent.attributes.add(slot_a,None,category="equip")
            self.parent.attributes.add(slot_b,a,category="equip")
            a.at_reequip(self.parent,slot_b)
        elif b:
            self.parent.attributes.add(slot_a,b,category="equip")
            b.at_reequip(self.parent,slot_a)
            self.parent.attributes.add(slot_b,None,category="equip")
        else:
            return 0
        return True
    def equip(self,item):
        if not item in [self.main_hand,self.off_hand]:
            self.parent.msg("You must be holding that.")
            return
        if item.wear_slot == None or item.wear_slot == []:
            self.parent.msg("You cannot equip that.")
            return
        options=item.wear_slot
        if not isinstance(options,list):
            options = [options]
        for slot in options:
            if self.get_slot(slot) == None:
                self.swap_slots(item.db.slot, slot)
                self.parent.msg(f"You equip the |w{item}|n to your |y{slot}|n.")
                return
        self.parent.msg("You cannot equip another item of that type.")
    def unequip(self,item):
        if (not item in self.slots) or (item.db.slot in ["hand_l","hand_r"]):
            self.parent.msg("You aren't wearing that.")
            return
        if not self.main_hand:
            to_hand = "right hand" if self.default_hand == "r" else "left hand"
            self.swap_slots(item.db.slot,self.main_hand_slot)
            self.parent.msg(f"You remove your |w{item}|n with your |y{to_hand}|n.")
            return
        if not self.off_hand:
            to_hand = "left hand" if self.default_hand == "r" else "right hand"
            self.swap_slots(item.db.slot,self.off_hand_slot)
            self.parent.msg(f"You remove your |w{item}|n with your |y{to_hand}|n.")
            return
        self.parent.msg("You need a free hand.")
        return
        
#region slots
    @property
    def slot_names(self):
        return ["hand_r","hand_l","belt","back","shirt","legs"]
    @property
    def equip_slot_names(self):
        return ["belt","back"]
    @property
    def slots(self):
        return [ self.main_hand, self.off_hand, self.belt, self.back, self.shirt,self.legs ]
    @property
    def equip_slots(self):
        return [self.belt,self.back,self.shirt,self.legs]
    @property
    def fast_contents(self):
        candidates=[self.main_hand,self.off_hand]
        for item in self.slots:
            if item != None and item.fast_remove:
                candidates.append(item)
        for item in self.containers:
            candidates.extend(item.fast_contents)
        return candidates
    @property
    def containers(self):
        result=[]
        for s in self.slots:
            if isinstance(s,Item) and s.container:
                result.append(s)
                result.extend(s.sub_containers)
        return result
    def get_slot(self,slot_name):
        if (not slot_name in self.slot_names):
            return None
        return self.parent.attributes.get(slot_name,category="equip")
    
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
    def main_hand_slot(self):
        if self.default_hand == "r":
            return "hand_r"
        return "hand_l"
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
    def off_hand_slot(self):
        if self.default_hand == "r":
            return "hand_l"
        return "hand_r"
    @property
    def hands(self):
        return [self.main_hand,self.off_hand]
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
        
        get_verb = "pick up"
        get_verb_pub = "picks up"
        from_block = ""
        
        ol = item.location
        if ol != self.parent.location:
            get_verb = "take"
            from_block = f" from the |w{ol}|n"
        
        item.move_to(self.parent,quiet=True)
        self.parent.attributes.add("hand_l",item,category="equip")
        item.at_equip(self.parent,"hand_l")
        self.parent.msg(f"You {get_verb} the |w{item}|n{from_block} with your |yleft hand|n.")
        if ol != self.parent and ol != None:
           ol.msg_contents("|w{person}|n {get_verb_pub} up the |w{item}|n{from_block}",mapping={"person":self.parent,"item":item,"get_verb_pub":get_verb_pub,"from_block":from_block},exclude=(self.parent) )
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
            
        get_verb = "pick up"
        get_verb_pub = "picks up"
        from_block = ""
        
        ol = item.location
        if ol != self.parent.location:
            get_verb = "take"
            from_block = f" from the |w{ol}|n"
        
        item.move_to(self.parent,quiet=True)
        self.parent.attributes.add("hand_r",item,category="equip")
        item.at_equip(self.parent,"hand_r")
        self.parent.msg(f"You {get_verb} the |w{item}|n{from_block} with your |yright hand|n.")
        if ol != self.parent and ol != None:
           ol.msg_contents("|w{person}|n {get_verb_pub} up the |w{item}|n{from_block}",mapping={"person":self.parent,"item":item,"get_verb_pub":get_verb_pub,"from_block":from_block},exclude=(self.parent) )
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
# Chest (shirt)
    @property
    def shirt(self):
        return self.parent.attributes.get("shirt",category="equip",default=None)
    @shirt.setter
    def shirt(self,item):
        if self.shirt != None:
            return
        if not isinstance(item,Item) or not item.portable:
            return
        if item.db.slot != None:
            item.at_unequip(self.parent)
        item.move_to(self.parent)
        self.parent.attributes.add("shirt",item,category="equip")
        item.at_equip(self.parent,"shirt")
# Leggings
    @property
    def legs(self):
        return self.parent.attributes.get("legs",category="equip",default=None)
    @legs.setter
    def legs(self,item):
        if self.legs != None:
            return
        if not isinstance(item,Item) or not item.portable:
            return
        if item.db.slot != None:
            item.at_unequip(self.parent)
        item.move_to(self.parent)
        self.parent.attributes.add("legs",item,category="equip")
        item.at_equip(self.parent,"legs")
#endregion