"""
Exits

Exits are connectors between Rooms. An exit always has a destination property
set and has a single command defined on itself with the same name as its key,
for allowing Characters to traverse the exit to its destination.

"""
from evennia.objects.objects import DefaultExit
from .objects import ObjectParent
from .SceneObject import SceneObject

class Exit(ObjectParent, DefaultExit):
    """
    Exits are connectors between rooms. Exits are normal Objects except
    they defines the `destination` property. It also does work in the
    following methods:

     basetype_setup() - sets default exit locks (to change, use `at_object_creation` instead).
     at_cmdset_get(**kwargs) - this is called when the cmdset is accessed and should
                              rebuild the Exit cmdset along with a command matching the name
                              of the Exit object. Conventionally, a kwarg `force_init`
                              should force a rebuild of the cmdset, this is triggered
                              by the `@alias` command when aliases are changed.
     at_failed_traverse() - gives a default error message ("You cannot
                            go there") if exit traversal fails and an
                            attribute `err_traverse` is not defined.

    Relevant hooks to overload (compared to other types of Objects):
        at_traverse(traveller, target_loc) - called to do the actual traversal and calling of the other hooks.
                                            If overloading this, consider using super() to use the default
                                            movement implementation (and hook-calling).
        at_post_traverse(traveller, source_loc) - called by at_traverse just after traversing.
        at_failed_traverse(traveller) - called by at_traverse if traversal failed for some reason. Will
                                        not be called if the attribute `err_traverse` is
                                        defined, in which case that will simply be echoed.
    """
    def display_section(self,looker,**kwargs):
        return "e"
    def get_display_footer(self, looker, **kwargs):
        std_names={"e":"east","w":"west","n":"north","s":"south","i":"in","o":"out","u":"up","d":"down","ne":"northeast","nw":"northwest","se":"southeast","sw":"southwest"}
        offer_aliases=[]
        for x in self.aliases.all():
            if len(x) <= 2 and x in std_names and self.name != std_names[x]:
                offer_aliases.append(std_names[x])
        if len(offer_aliases) > 0:
            return f"This exit will take you |y{'|n/|y'.join(offer_aliases)}|n."
        else:
            return "" 
        
    def get_display_name(self, looker=None, **kwargs):
        """
        Displays the name of the object in a viewer-aware manner.

        Args:
            looker (TypedObject): The object or account that is looking
                at/getting inforamtion for this object. If not given, `.name` will be
                returned, which can in turn be used to display colored data.

        Returns:
            str: A name to display for this object. This can contain color codes and may
                be customized based on `looker`. By default this contains the `.key` of the object,
                followed by the DBREF if this user is privileged to control said object.

        Notes:
            This function could be extended to change how object names appear to users in character,
            but be wary. This function does not change an object's keys or aliases when searching,
            and is expected to produce something useful for builders.

        """
        offer_aliases=[]
        std_names={"e":"east","w":"west","n":"north","s":"south","i":"in","o":"out","u":"up","d":"down","ne":"northeast","nw":"northwest","se":"southeast","sw":"southwest"}
        for x in self.aliases.all():
            if len(x) <= 2 and x in std_names and self.name != std_names[x]:
                offer_aliases.append(x)
        append=""
        if len(offer_aliases)>0:
            append=f"|n (|y{'|n,|y'.join(offer_aliases)}|n)"
        if looker and self.locks.check_lockstring(looker, "perm(Builder)"):
            return f"{self.name}{append}(#{self.id})"
        return f"{self.name}{append}"
    pass
class SceneExit(SceneObject,Exit):
    """
    SceneExits are normally hidden and teased in the room's descriptive text rather than explicitly listed.
    """
    _content_types=("exit","scene",)
    