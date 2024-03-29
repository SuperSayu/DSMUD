"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""
from evennia.objects.objects import DefaultCharacter
from evennia.utils.utils import lazy_property
from evennia.utils.create import create_object

from .objects import ObjectParent
from .item import Item
from .statcore import StatCore
from .skillcore import SkillCore
from .equipcore import EquipmentCore


class Character(ObjectParent, DefaultCharacter):
    """
    The Character defaults to reimplementing some of base Object's hook methods with the
    following functionality:

    at_basetype_setup - always assigns the DefaultCmdSet to this object type
                    (important!)sets locks so character cannot be picked up
                    and its commands only be called by itself, not anyone else.
                    (to change things, use at_object_creation() instead).
    at_post_move(source_location) - Launches the "look" command after every move.
    at_post_unpuppet(account) -  when Account disconnects from the Character, we
                    store the current location in the pre_logout_location Attribute and
                    move it to a None-location so the "unpuppeted" character
                    object does not need to stay on grid. Echoes "Account has disconnected"
                    to the room.
    at_pre_puppet - Just before Account re-connects, retrieves the character's
                    pre_logout_location Attribute and move it back on the grid.
    at_post_puppet - Echoes "AccountName has entered the game" to the room.

    """
    def at_init(self):
        self.skills.normalize(fast=True)
        
    def contents_get(self, exclude=None, content_type=None):
        return self.items.contents
#region handlers
    @lazy_property
    def stats(self):
        if self.db.statcore == None:
            self.db.statcore = create_object("statcore.StatCore", key=f"({self.key}.statcore)", location=self, home=self)
        return self.db.statcore
        #return StatCore(self)
    @lazy_property
    def skills(self):
        return SkillCore(self)
    @lazy_property
    def items(self):
        return EquipmentCore(self)
    
    @property
    def internals(self):
        """
        Returns a list of any Evennia objects carried by a character
        which will not show up in inventory but which should not
        be ejected from the character if detected.
        """
        return [self.stats]
#endregion
    def display_section(self,looker,**kwargs):
        return "c"
    exceptions=[]
    def log_error(self,err:Exception, traceback):
        self.msg(f"Exception: {err}")
        self.msg(f"{traceback}")
        self.msg()
        self.exceptions.append([err,traceback])
    
    @property
    def busy(self):
        return self.ndb.busy
    @busy.setter
    def busy(self,b):
        self.ndb.busy = b

    def Cooldown(self):
        self.skills.Cooldown()