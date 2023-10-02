from evennia import Command
from typeclasses.characters import Character
from typeclasses.objects import Object

# Still needed: give

class GetCommand(Command):
    """
    Put an item into your hands, like an asshole.
    """
    key="get"
    aliases=["pickup"]
    def parse(self):
        # This is needed to search in containers on our person
        locs = [self.caller.location,self.caller]
        locs.extend(self.caller.items.containers)
        self.object = self.caller.search(self.args.lstrip(),quiet=True,
            location = locs)
        if hasattr(self.object,"__iter__"):
            self.object = [*self.object]
            for x in self.caller.items.slots:            
                if x in self.object:
                    self.object.remove(x)
        if isinstance(self.object,list):
            if len(self.object) > 0:
                self.object = self.object[0]
            else:
                self.object = None
    def func(self):
        if not self.object:
            self.caller.msg("Pick up what?")
            return
        if isinstance(self.caller,Character):
            self.caller.items.pickup(self.object)
        else:
            if item.at_before_get(self.caller):
                item.move_to(self.caller)
                item.at_get(self.caller)

class DropCommand(Command):
    """
    Put an item on the ground, like an asshole.
    """
    key="drop"
    def parse(self):
        # Debug/admin: Drop items not in inventory
        if self.args == "":
            c = self.caller.contents
            s = self.caller.items.slots
            s.extend(self.caller.internals)
            self.object=0
            for i in c:
                if i in s:
                    continue
                self.object += 1
                i.move_to(self.caller.location)
            if self.object == 0:
                self.object = None
            return
        self.object = self.caller.items.require(itemKey=self.args.lstrip(),manual=True)      
        if isinstance(self.object,list):
            if len(self.object) > 0:
                self.object = self.object[0]
            else:
                self.object = None
    def func(self):
        if isinstance(self.object,int): # debug/admin
            self.caller.msg(f"Dropped {self.object} objects.")
            return
        if not self.object:
            self.caller.msg("That's not a thing you have.")
            return
        if isinstance(self.caller,Character):
            self.caller.items.drop(self.object)
        elif item.location == self.caller:
            if item.at_before_drop(self.caller):
                item.move_to(self.caller.location)
                item.at_drop(self.caller)

class PutCommand(Command):
    """
    Put one item inside a storage item or object, like an asshole.
    But not like putting an item in your asshole.  That's would be the 'wear' command.
    Only not, because this isn't that kind of game.
    """
    key="put"
    def parse(self):
        parsed = self.args.lstrip().split(" in ")
        if len(parsed) != 2:
            self.object = None
            self.dest = None
        else:
            self.object = self.caller.items.require(itemKey=parsed[0],hands_only=True)
            self.dest = [*self.caller.search(parsed[1],quiet=True)]
            self.dest.extend(self.caller.items.require(itemKey=parsed[1],manual=False))
            if isinstance(self.object,list):
                if len(self.object) > 0:
                    self.object = self.object[0]
                else:
                    self.object = None
            if isinstance(self.dest,list):
                if len(self.dest) > 0:
                    self.dest = self.dest[0]
                else:
                    self.dest = None
    def func(self):
        o,d = isinstance(self.object,Object),isinstance(self.dest,Object)
        if not o or not d:
            self.caller.msg(f"Put {self.object if o else 'what'} in {self.dest if d else 'where'}?")
            return
        if not self.object.portable:
            self.caller.msg(f"You can't let go of |w{self.object}|n.")
            return
        if not self.dest.container:
            self.caller.msg(f"You can't put anything in |w{self.dest}|n.")
            return
        if not self.dest.at_pre_item_receive(self.object):
            self.caller.msg(f"You can't put that in |w{self.dest}|n.")
            return
        self.caller.attributes.add(self.object.db.slot,None,category="equip")
        self.object.at_unequip(self.caller)
        self.object.move_to(self.dest,quiet=True)
        self.caller.msg(f"You put |w{self.object}|n in the |w{self.dest}|n.")
        self.caller.location.msg_contents("|w{person}|n puts their |w{item}|n in the |w{place}|n.",mapping={"person":self.caller,"item":self.object,"place":self.dest},exclude=(self.caller) )

class WearCommand(Command):
    """
    Put one item on yourself, like an asshole.
    """
    key="wear"
    aliases=["equip"]
    def parse(self):
        # This is needed to search in containers on our person
        self.object = self.caller.items.require(itemKey=self.args.lstrip(),manual=True)
        if isinstance(self.object,list):
            if len(self.object) > 0:
                self.object = self.object[0]
            else:
                self.object = None
    def func(self):
        if self.object != None:
            self.caller.items.equip(self.object)
        else:
            self.caller.msg("Equip what?")

class RemoveCommand(Command):
    """
    Remove one item from your equipment and put it in your hand, like an asshole.
    """
    key="remove"
    aliases=["unequip","take off"]
    def parse(self):
        # This is needed to search in containers on our person
        self.object = self.caller.items.require(itemKey=self.args.lstrip(),manual=False)
        if isinstance(self.object,list):
            if len(self.object) > 0:
                self.object = self.object[0]
            else:
                self.object = None
    def func(self):
        if self.object != None:
            self.caller.items.unequip(self.object)
        else:
            self.caller.msg("Remove what?")

class SwapHandsCommand(Command):
    """
    Move items between your hands, like an asshole.
    """
    key="swap"
    def func(self):
        r=self.caller.items.swap_slots("hand_l","hand_r")
        if r == True:
            self.caller.msg("You swap the items in your hands around.")
        elif r == 0:
            self.caller.msg("You have nothing in your hands!")
        elif r == None:
            self.caller.msg("Error")

class InventoryCommand(Command):
    """
    Check what's in your hands and equipment, like an asshole.
    """
    key="inventory"
    aliases=["inv"]
    def func(self):
        self.caller.items.show()

class LookInCommand(Command):
    """
    Look inside something, like an asshole.
    (Please do not look inside an asshole.)
    """
    key="look in"
    def parse(self):
        locs = [self.caller.location,self.caller]
        locs.extend(self.caller.items.containers)
        self.object = self.caller.search(self.args.lstrip(),quiet=True,
            location = locs)
        if hasattr(self.object,"__iter__"):
            self.object = [*self.object]
        if isinstance(self.object,list):
            if len(self.object) > 0:
                self.object = self.object[0]
            else:
                self.object = None
    def func(self):
        if self.object == None:
            self.caller.msg("Look in what?")
            return
        if (not isinstance(self.object,Object)) or (not self.object.container):
            self.caller.msg(f"The |w{self.object}|n is not a container of any kind.")
            return
        self.object.describe_contents(self.caller)
        