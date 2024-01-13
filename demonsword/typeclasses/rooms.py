"""
Room

Rooms are simple containers that has no location of their own.

"""

from util.AttributeProperty import AttributeProperty
from evennia.objects.objects import DefaultRoom
from collections import defaultdict
from .objects import ObjectParent
#from util.PQueue import iPriorityQueue
from evennia.utils.utils import iter_to_str
from .SceneObject import SceneObject

class Room(ObjectParent, DefaultRoom):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See examples/object.py for a list of
    properties and methods available on all Objects.
    """
    # from ObjectParent
    container=True
    
    # New APs
    state = AttributeProperty({})
    resourceNodes = AttributeProperty({None:5}) # None:difficulty to find non-event, forage_skillkey:[possible_prototype_key,...]
    restTags = AttributeProperty({"rest":False,"train":False,"meditate":False,"sleep":False})

    def get_resource_node(self,skill,skillCheck):
        """
        Called when the player attempts to find resources with a harvesting skill, but has not yet
        found a node.  If there is no resource node for that skill in this room, you must pass a
        basic check (determined by the None index in resourceNodes) to be told specifically that
        nothing exists.  If a skill index exists but is only a number, that is the check to be sure
        that specific skill has no result (for example, searching in a dungeon where searching is
        often correct).  This allows you to differentiate between checks that make no sense
        (mining in a house) versus "correct skill, wrong room" checks.
        """
        return None
    
    def __lt__(self,other):
        if not isinstance(other,SceneObject):
            return True
        return other.priority >= 0 # zero is the canonical location of the room description
    def get_background_desc(self,looker,**kwargs):
        return self.db.desc or ""
    
    def get_display_desc(self, looker, **kwargs):
        background = self.contents_get(content_type="scene")
        if len(background) == 0:
            return self.get_background_desc(looker,**kwargs) or "You see nothing special."
        if len(background) == 1:
            so = background[0]
            if so.priority < 0:
                return f"{background[0].get_background_desc(looker,**kwargs)} " + self.get_background_desc(looker,**kwargs)
            else:
                return self.get_background_desc(looker,**kwargs) + f" {background[0].get_background_desc(looker,**kwargs)}"
        background.append(self)
        background.sort()
        background = [*map(lambda s:s.get_background_desc(looker,**kwargs),background)]
        while "" in background:        
            background.remove("")
        return " ".join(background)

    def get_display_things(self,looker,**kwargs):
        def _filter_visible(obj_list):
            return (obj for obj in obj_list if obj != looker and not ("scene" in obj._content_types) and obj.access(looker, "view"))

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
        return f"\n|wYou see:|n {thing_names}" if thing_names else ""
    pass
