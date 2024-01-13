"""
    A SceneObject is meant to be a background item that is pulled from to
    produce a room description, also providing an object that can be Looked at.
    A SceneObject may have different descriptions based on time of day and
    based on events such as weather.  SceneObjects otherwise should not be
    interacted with using normal verbs (but may have their own, for shops, etc).
"""

from .objects import Object
from .characters import Character
from util.AttributeProperty import AttributeProperty

class SceneObject(Object):
    _content_types = ("object","scene",)
    LongSceneVars=["desc","scene_desc"] # these are used by the Scene verb for viewing and editing
    priority = AttributeProperty(100)
    scene_desc = AttributeProperty(None)
    invisible = AttributeProperty(False) # disable viewing
    
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.locks.add("view:so_seen();bgview:so_seen()")
        
    def __lt__(self,other):
        return self.priority < other.priority
    def Seen(self,other):
        """
        Returns true if this screen object has been found by a user.
        This is intended for hiding screen objects behind a skill check.
        Use with: 
            locks.add("view:so_seen();bgview:so_seen()")
        """
        return not self.invisible 
    def get_background_desc(self, looker, **kwargs):
        if not self.access(looker,"bgview") or self.invisible:
            return ""
        return self.scene_desc or self.get_display_desc(looker,**kwargs)

class SpawnerObject(SceneObject):
    """
    SpawnerObjects are meant to simplify spawning stuff
    """
    giver = AttributeProperty(False,key="spawn_giver")

    def spawn_success(self,obj,caller):
        #obj.location = self.location
        if self.giver and isinstance(caller,Character):
            check=caller.items.pickup(obj,silent=True)
            if check:
                caller.msg(f"You find a |w{obj}|n!  You pick it up.")
            else:
                caller.msg(f"You find a |w{obj}|n")
            return
        if caller:
            caller.msg(f"You see a |w{obj}|n laying around.")