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
from evennia.utils.dbserialize import _SaverDict as saverdict

class SceneObject(Object):
    _content_types = ("object","scene",)
    SceneVars=["desc","scene_desc","invisible"] # this can be edited with the scene command
    LongSceneVars=["desc","scene_desc"] # these are used by the Scene verb for viewing and editing
    priority = AttributeProperty(100)
    scene_desc = AttributeProperty(None)
    invisible = AttributeProperty(False) # disable viewing
    footer_display = AttributeProperty(False)
    during = AttributeProperty({}) # during {tag: { variable:replacement,... },... }

    def current_during(self,varlist=None):
        ""
        if varlist == None:
            varlist = self.SceneVars
        if len(varlist) == 0:
            return {}
        results={}
        for x in varlist:
            results[x] = self.attributes.get(x)
        if not self.during:
            return results
        state = self.location.state
        for x in state.keys():
            if not x in self.during:
                continue
            sdict = self.during[x]
            for y in sdict.keys():
                if y in varlist:
                    results[y]=sdict[y]
                    
        return results
        
    def set_during(self,tag,var,replacement,caller=None):
        if tag == None or len(tag) == 0:
            if caller:
                caller.msg("No tag given")
            return        
        if not tag in self.during:
            self.during[tag] = {}
        d = self.during[tag]
        if replacement == None:
            if not var in d:
                caller.msg("set_during: Attempting to remove nonexistent var")
                return
            del d[var]
            if len(d) == 0:
                del self.during[tag]
                if caller:
                    caller.msg(f"Removed {self.name}/{tag}/{var}.  {tag} is now empty, removing.")
            else:
                if caller:
                    caller.msg(f"Removed {self.name}/{tag}/{var}.")
            return
        d[var]=replacement
        if caller:
            caller.msg(f"Set {self.name}/{tag}/{var}={replacement}.")
    
    def display_section(self,looker,**kwargs):
        # I'd like to add the invisible here but that needs to be during-checked right now
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
    def get_display_desc(self, looker,**kwargs):
        x=self.current_during(["desc","invisible"])
        d,i = x["desc"],x["invisible"]
        if d == None: # allow explicit empty strings
            d =  "You see nothing special."
        if not self.access(looker,"view") or i:
            return ""
        return d
    def get_background_desc(self, looker, state=None, **kwargs):
        x=self.current_during(["scene_desc","invisible"])
        sd,i = x["scene_desc"],x["invisible"]
        if not self.access(looker,"bgview") or i:
            return ""
        return sd or self.get_display_desc(looker,**kwargs)

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