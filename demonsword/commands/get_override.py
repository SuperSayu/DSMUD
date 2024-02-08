from evennia import Command
from typeclasses.characters import Character
from typeclasses.objects import Object

# Still needed: give

class GetCommand(Command):
    """
    Put an item into your hands, like an asshole.
    Syntax: Get [my|other] item [from [my|other] container] (or [from floor])
    
    The "other" keyword will ignore your current inventory,
    and the "my" keyword will only select among your inventory.
    The "floor" specifier (also "ground" and "here") will only
    look at objects in the room, ignoring your inventory.
    """
    key="get"
    aliases=["pickup"]
    err_msg = None
    debug=False
    def parse_from(self) -> list: # returns locs list
        locs = [self.caller.location,self.caller]
        locs.extend(self.caller.items.containers)
        mine = False
        if self.args.startswith("my "):
            self.args = self.args[3:]
            locs = locs[1:] # your things are on your person, ignore location        
            mine = True
        elif self.args.startswith("other "):
            self.args = self.args[6:]
            locs = locs[0:1]
            mine=True
        split = self.args.split(" from ")
        if len(split) == 1:
            return locs
        if len(split) > 2:
            self.err_msg = "Too many |rfrom|ns in that request, please try again."
            self.args=""
            self.object = None
            return
        self.args = split[0] # remove from clause so that the rest can be parsed
        from_clause = split[1].strip()
        from_locs = locs.copy()
        if from_clause.startswith("my "):
            if not mine:
                from_locs = from_locs[1:]
                mine = True
            from_clause = from_clause[3:].strip()
        elif from_clause.startswith("other "):
            from_clause=from_clause[6:].strip()
            if not mine:
                from_locs = from_locs[0:1]
                mine = True
        elif from_clause.lower() in ["here","ground","floor","the ground", "the floor"]:
            return [self.caller.location]
        if self.debug:
            self.caller.msg("Looking in (from):")
            for l in from_locs:
                self.caller.msg(f"> {l}{l.dbref}")
        from_obj = self.caller.search(from_clause,quiet=True,
            location = from_locs)
        if hasattr(from_obj,"__iter__"):
            from_obj = [*from_obj]
        if len(from_obj) == 0:
            self.caller.msg(f"You don't see a '{split[1]}' to get any '{self.args}'from.")
            self.args = ""
            locs = [] 
        return from_obj or locs
    
    def parse(self):
        if self.args.startswith("/?"):
            self.debug =  True
            self.args = self.args[2:]
        else:
            self.debug = False
        self.err_msg = None
        self.args = self.args.strip()
        locs = self.parse_from()
        if self.debug:
            self.caller.msg("Looking in:")
            for l in locs:
                self.caller.msg(f"> {l}{l.dbref}")
        # This is needed to search in containers on our person
        self.object = self.caller.search(self.args,quiet=True,
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
            self.caller.msg(self.err_msg or "Pick up what?")
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
        self.args = self.args.lstrip()
        if self.args.startswith('my '):
            self.args = self.args[2:]
        self.object = self.caller.items.require(itemKey=self.args,manual=True)      
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
    
    Put item in [my|other] container
    
    The "my" keyword only looks at your inventory to find the container.
    The "other" keyword ignores your inventory and looks in the room.
    """
    key="put"
    def parse(self):
        parsed = self.args.lstrip().split(" in ")
        if len(parsed) != 2:
            self.object = None
            self.dest = None
        else:
            self.object = self.caller.items.require(itemKey=parsed[0],hands_only=True)
            
            dest_clause = parsed[1]
            dest_sources=None
            if dest_clause.startswith("my "):
                self.dest = self.caller.items.require(itemKey=dest_clause[3:],manual=False)
            elif dest_clause.startswith("other "):
                self.dest = [*self.caller.search(dest_clause[6:],location=[self.caller.location],quiet=True)]
            else:  
                self.dest = [*self.caller.search(dest_clause,quiet=True)]
                inv = self.caller.items.require(itemKey=dest_clause,manual=False) or []
                if not isinstance(inv,list):
                    inv = [inv]
                self.dest.extend(inv)
            
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
        spec_add = ""
        spec_start = "your"
        spec_other = "their"
        if self.dest.location == self.caller.location:
            spec_add = " that is on the ground"
            spec_start = "the"
            spec_other = "the"
        self.caller.attributes.add(self.object.db.slot,None,category="equip")
        self.object.at_unequip(self.caller)
        self.object.move_to(self.dest,quiet=True)
        self.caller.msg(f"You put your |w{self.object}|n in {spec_start} |w{self.dest}|n{spec_add}.")
        self.caller.location.msg_contents("|w{person}|n puts their |w{item}|n in {spec_other} |w{place}|n.",mapping={"person":self.caller,"item":self.object,"place":self.dest,"spec_other":spec_other},exclude=(self.caller) )

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
        self.args = self.args.strip()
        locs = [self.caller.location,self.caller]
        locs.extend(self.caller.items.containers)
        if self.args.startswith("my "):
            locs = locs[1:]
            self.args = self.args[3:]
        elif self.args.startswith("other "):
            locs = locs[0:1]
            self.args = self.args[6:]
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
        