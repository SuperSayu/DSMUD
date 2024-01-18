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
    container=True # not sure this is exactly used or anything
    
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
        if not isinstance(other,SceneObject): # this could be expanded if we knew another type with .priority
            return True
        return other.priority >= 0 # zero is the canonical location of the room description
    
    def get_background_desc(self,looker,state=None,**kwargs):
        return self.db.desc or ""
    
    def get_display_desc(self, looker,**kwargs):
        background = [ so for so in self.contents_get(content_type="scene") if so.display_section(looker,**kwargs) == 'd' ]
        
        if len(background) == 0:
            return self.get_background_desc(looker,self.state,**kwargs) or "You see nothing special."
        if len(background) == 1:
            so = background[0]
            if so.priority < 0:
                return f"{background[0].get_background_desc(looker,**kwargs)} " + self.get_background_desc(looker,**kwargs)
            else:
                return self.get_background_desc(looker,self.state,**kwargs) + f" {background[0].get_background_desc(looker,**kwargs)}"
        background.append(self)
        background = [*map(lambda s:s.get_background_desc(looker,self.state,**kwargs), sorted(background) )]
        while "" in background:        
            background.remove("")
        return " ".join(background)

    def get_display_things(self,looker,**kwargs):
        def _filter_visible(obj_list):
            return (obj for obj in obj_list if obj != looker and obj.display_section(looker,**kwargs) == 't' and obj.access(looker, "view"))

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
    def get_display_exits(self,looker,**kwargs):    
        """
        Get the 'exits' component of the object description. Called by `return_appearance`.

        Args:
            looker (Object): Object doing the looking.
            **kwargs: Arbitrary data for use when overriding.
        Returns:
            str: The exits display data.

        """

        def _filter_visible(obj_list):
            return (obj for obj in obj_list if obj != looker and obj.display_section(looker,**kwargs) == 'e' and obj.access(looker, "view"))

        exits = _filter_visible(self.contents_get(content_type="exit"))
        exit_names = iter_to_str(exi.get_display_name(looker, **kwargs) for exi in exits)

        return f"|wExits:|n {exit_names}" if exit_names else ""
    def get_display_footer(self,looker,**kwargs):
        background = [ so for so in self.contents_get(content_type="scene") if so.display_section(looker,**kwargs) == 'f' ]
        if len(background) == 0:
            return ""
        background = [*map(lambda s:s.get_background_desc(looker,**kwargs), sorted(background) )]
        while "" in background:        
            background.remove("")
        return " ".join(background)
    pass
