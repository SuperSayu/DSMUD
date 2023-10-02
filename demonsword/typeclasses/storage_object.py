"""
    Storage mixin: Facilities for one Object storing others
"""
from .item import Item,Equipment
from util.AttrProperty import AttributeProperty

class Storage(Equipment):
    # old properties
    container=True  # ObjectParent
    size = 2        # Item 
    # new properties
    open     = AttributeProperty("open",True)
    max_size = AttributeProperty("max_size",1)
    
    def open_container(self):
        self.open = True
    def close_container(self):
        self.open = False
    
    def fit_check(self,incoming):
        if incoming.size > self.max_size:
            return False
        return True
    def at_pre_item_receive(self,incoming):
        """
            This is specifically meant for Storage-type items.
        """
        if not self.container or not self.open or not incoming.portable:
            return False
        return self.fit_check(incoming)

class Destroyer(Storage):
    max_size = 999
    def at_init(self):
        for obj in self.contents:
            obj.delete()
    def at_object_receive(self,incoming,user,**kwargs):
        user.msg(f"What {incoming}?")
        incoming.delete()

class Backpack(Storage):
    wear_slot="back"
    max_size = 2
    size = 3

class Belt(Storage):
    """
    Belts are intended to hold a number of different storage accessories.
    They do not store generic items; you can add pouches, sheathes, etc to them.
    """
    wear_slot="belt"
    max_size = 2
    size = 2
    max_slots = AttributeProperty("max_slots",5)
    def fit_check(self,incoming):
        if len(self.contents) >= self.max_slots:
            return False
        if incoming.size > self.max_size:
            return False
        if not incoming.belt_attach:
            return False
        return True
    @property
    def fast_contents(self):
        c=[]
        for i in self.contents:
            c.extend(i.fast_contents)
            if i.fast_remove:
                c.append(i)
        return c
    @property
    def sub_containers(self):
        c=[]
        for i in self.contents:
            if isinstance(i,Storage):
                c.append(i)
        return c
class BeltStorage(Storage):
    belt_attach=True
    max_size = 1
    size = 2
    @property
    def fast_contents(self):
        return self.contents

# Comes with its own belt as well as attachments
class FannyPack(BeltStorage):
    wear_slot="belt"

class BeltScabbard(Storage):
    belt_attach=True
    max_size=3
    size=2
    def fit_check(self,incoming):
        if len(self.contents) > 1:
            return False
        if incoming.size > self.max_size:
            return False
        # todo: item type check: is sword
        return True
