"""
    Storage mixin: Facilities for one Object storing others
"""
from .item import Item,Equipment
from util.AttributeProperty import AttributeProperty
from .SceneObject import SceneObject
from collections import defaultdict
from evennia.utils.utils import iter_to_str

class Storage(Equipment):
    _content_types = ("object","item","equip","storage",) 
    # old properties
    container=True  # ObjectParent
    size = 2        # Item 
    # new properties
    open     = AttributeProperty(True)
    max_size = AttributeProperty(1)
    
    def open_container(self):
        self.open = True
    def close_container(self):
        self.open = False
    def get_display_things(self, looker, **kwargs):
        if not self.open:
            return "|/It is |wclosed|n."
        def _filter_visible(obj_list):
            return (obj for obj in obj_list if obj != looker and obj.access(looker, "view"))

        # sort and handle same-named things
        things = _filter_visible(self.contents_get(content_type="object"))

        grouped_things = defaultdict(list)
        for thing in things:
            grouped_things[thing.get_display_name(looker, **kwargs)].append(thing)

        thing_names = []
        for thingname, thinglist in sorted(grouped_things.items()):
            nthings = len(thinglist)
            thing = thinglist[0]
            singular, plural = thing.get_numbered_name(nthings, looker, key=thingname)
            thing_names.append(singular if nthings == 1 else plural)
        thing_names = iter_to_str(thing_names)
        return f"|/|wIt contains:|n {thing_names}" if thing_names else "|/It is |wempty|n."
    
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
    def at_item_receive(self,incoming,slot=""):
        """
        You got a thing in me.
        """
        incoming.last_container = self

class Destroyer(SceneObject,Storage):
    _content_types = ("object","scene",)
    max_size = 999
    portable = False
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
    max_slots = AttributeProperty(5)
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
