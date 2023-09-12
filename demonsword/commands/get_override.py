from evennia import Command
from typeclasses.characters import Character

class GetCommand(Command):
   """
   Put an item into your hands, like an asshole.
   """
   key="get"
   aliases=["pickup"]
   def parse(self):
      self.object = self.caller.search(self.args.lstrip(),quiet=True)      
      if isinstance(self.object,list):
        self.object = self.object[0]
   def func(self):
      if not self.object:
         self.caller.msg("Pick up what?")
         return
      if isinstance(self.caller,Character):
         self.caller.items.pickup(self.object)
      else:
         item.move_to(self.caller)
class DropCommand(Command):
   """
   Put an item on the ground, like an asshole.
   """
   key="drop"
   def parse(self):
      self.object = self.caller.search(self.args.lstrip(),quiet=True)      
      if isinstance(self.object,list):
        self.object = self.object[0]
   def func(self):
      if not self.object:
         self.caller.msg("That's not a thing you have.")
         return
      if isinstance(self.caller,Character):
         self.caller.items.drop(self.object)
      elif item.location == self.caller:
         item.move_to(self.caller.location)
class SwapHandsCommand(Command):
   key="swap"
   def func(self):
      self.caller.items.swap_hands()
class InventoryCommand(Command):
   key="inventory"
   aliases=["inv"]
   def func(self):
      self.caller.items.show()