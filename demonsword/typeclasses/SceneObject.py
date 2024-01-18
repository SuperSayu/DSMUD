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
    footer_display = AttributeProperty(False)
    
    def display_section(self,looker,**kwargs):
        if self.invisible:
            return ""
        if self.footer_display:
            return "f"
        return "d"
    def basetype_setup(self):
        super().basetype_setup()
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
    def get_background_desc(self, looker, state=None, **kwargs):
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

class ZoneScene(SceneObject):
    """
    A ZoneScene is intended to be consistent across a region, possibly with some random variation.
    Zones are logical collections of rooms, such as within the same building, or outside under the same sky.
    This is mostly used so that a region has tonal consistency, especially regarding weather, etc.
    
    Generally a zone description will be a couple sentences, reacting to tags and events.
    Tags are for things like busy vs quiet streets, while events include time of day and weather.
    It may be wise to create a number of hand crafted combinations of time, weather, and tags for a zone.
    
    Usage:
        key | (tuple,of,keys) : description | [array,of,possible,descriptions] | {probabilistic:25,array:15,as:35,dict:25}
       
    
    This is all todo, mostly because I want to support !not_tag and that's not as elegant to do as I originally thought
    """
    early_descs = AttributeProperty({})
    descs = AttributeProperty({})
    late_descs = AttributeProperty({})
    
    def tags_and_events(self):
        return ()
    def check(self,haystack,needles):
        if isinstance(needles,str):
            if needles[0]=="!":
                return not needles[1:] in haystack
            return needles in haystack
        if isinstance(needles,list|tuple):
            for x in needles:
                if not isinstance(x,str):
                    raise ValueError("ZoneScene.check: Non-string key in set")
                # Specified not but is, or specified is but is not
                if (x[0]=="!" and x[1:] in haystack) or (x not in haystack):
                    return False
        return False
    def find_matches(self):
        taglist = set(self.tags_and_events())
        if len(t) == 0:
            return
        e = [ k for k in early_descs.keys() if self.check(taglist,k) ]
        d = [ k for k in descs.keys() if self.check(taglist,k) ]
        l = [ k for k in late_descs.keys() if self.check(taglist,k) ]
        

    def get_background_desc(self, looker, **kwargs):
        return ""