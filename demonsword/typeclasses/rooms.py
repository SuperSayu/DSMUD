"""
Room

Rooms are simple containers that has no location of their own.

"""

from evennia.objects.objects import DefaultRoom

from .objects import ObjectParent


class Room(ObjectParent, DefaultRoom):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See examples/object.py for a list of
    properties and methods available on all Objects.
    """
    container=True
    
    # If you attempt certain resource actions, you may generate a resource node
    # These are prototype name 
    resourceNodes = {"forage":["berrybush"],"mine":[]}
    # Availability of stuff for reasons
    trainingTags = {"rest":False,"train":False,"Meditate":False}
    pass
