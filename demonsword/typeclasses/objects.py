"""
Object

The Object is the "naked" base class for things in the game world.

Note that the default Character, Room and Exit does not inherit from
this Object, but from their respective default implementations in the
evennia library. If you want to use this class as a parent to change
the other types, you can do so by adding this as a multiple
inheritance.

"""
from evennia.objects.objects import DefaultObject
from util.AttributeProperty import AttributeProperty,UpdateDefaults
#from evennia.prototypes.spawner import spawn
from util.spawn import spawn
#from .characters import Character

class ObjectParent:
    """
    This is a mixin that can be used to override *all* entities inheriting at
    some distance from DefaultObject (Objects, Exits, Characters and Rooms).

    Just add any method that exists on `DefaultObject` to this class. If one
    of the derived classes has itself defined that same hook already, that will
    take precedence.

    """
    container       = AttributeProperty(False)  # Property: this can hold portable things
    portable        = AttributeProperty(False)  # Property: this can be picked up
    newlocks        = AttributeProperty({})     # Property:  
    invisible       = AttributeProperty(False) # disable viewing
    
    def at_pre_item_receive(self,incoming,slot=""):
        """
            This is specifically meant for Storage-type items, and will be overridden there.
        """
        if not self.container or not incoming.portable:
            return False
        return True
    def at_item_receive(self,incoming,slot=""):
        """
        You got a thing in me.
        """
        return
    def at_post_spawn(self,caller=None,spawner=None):
        """
        Called after an object is fully spawned by util.spawn.spawn()
        or the overridden spawn command.  If a spawner object is passed
        to spawn, this will be called after at_spawned_by().  This will
        not be called if using the native evennia spawner func.
        """
        #print(f"Spawned {self}({self.__class__.__name__})")
        return
    
    def at_spawned_by(self,spawner=None,user=None):
        """
        Called when spawned by another object.  If spawned with an
        admin spawn command, or if the spawner keyword is not set in
        a call to utils.spawn, or if the evennia spawner is used
        instead, this will not be called.
        """
        return
    def spawn_success(self,obj,caller=None):
        """
        Called if this object spawns another using util.spawn.spawn()
        using the spawner keyword.  This is called before the object
        receives at_spawned_by() and at_post_spawn().  This is called
        individually per object spawned, not per batch.
        """
        return
        
    def describe_contents(self, looker):
        """
        Report contents as though someone was looking inside
        """
        looker.msg(f"Inside of the |w{self}|n, you see:")
        if len(self.contents) == 0:
            looker.msg("* |yNothing|n.")
        def report(item):
            looker.msg(f"* A |w{item}|n.")
        self.for_contents(report)
    def display_section(self,looker,**kwargs):
        """
        Returns a code determining which section in a room display this should be.
        This should be t(hings), c(haracters), e(xits), d(escription), or f(ooter),
        or "" for none.
        """
        return "t" if not self.invisible else ""
    def get_background_desc(self, looker, state=None, **kwargs):
        return self.get_display_desc(looker,**kwargs)
    
    def __init_subclass__(cls):
        """
        This function override handles AttributeProperty objects.
        If you redefine a class member where the original member
        was an AttributeProperty and the new member is not,
        the new member will be replaced with an AttributeProperty
        and the value that would have overridden it is stored as
        the default (used when no attribute exists).
        
        See util/AttrProperty.py for details.
        """
        UpdateDefaults(super())
        
#    def at_pre_move(self,destination,move_type="move",**kwargs):
#        """
#            Override to call at_pre_object_receive on destination
#        """
#        return destination.at_pre_object_receive(self)


class Object(ObjectParent, DefaultObject):
    """
    You should never need to re-implement special Python
    methods, such as __init__ and especially never __getattribute__ and
    __setattr__ since these are used heavily by the typeclass system
    of Evennia and messing with them might well break things for you.

    * Base properties defined/available on all Objects

     key (string) - name of object
     name (string)- same as key
     dbref (int, read-only) - unique #id-number. Also "id" can be used.
     date_created (string) - time stamp of object creation

     account (Account) - controlling account (if any, only set together with
                       sessid below)
     sessid (int, read-only) - session id (if any, only set together with
                       account above). Use `sessions` handler to get the
                       Sessions directly.
     location (Object) - current location. Is None if this is a room
     home (Object) - safety start-location
     has_account (bool, read-only)- will only return *connected* accounts
     contents (list of Objects, read-only) - returns all objects inside this
                       object (including exits)
     exits (list of Objects, read-only) - returns all exits from this
                       object, if any
     destination (Object) - only set if this object is an exit.
     is_superuser (bool, read-only) - True/False if this user is a superuser

    * Handlers available

     aliases - alias-handler: use aliases.add/remove/get() to use.
     permissions - permission-handler: use permissions.add/remove() to
                   add/remove new perms.
     locks - lock-handler: use locks.add() to add new lock strings
     scripts - script-handler. Add new scripts to object with scripts.add()
     cmdset - cmdset-handler. Use cmdset.add() to add new cmdsets to object
     nicks - nick-handler. New nicks with nicks.add().
     sessions - sessions-handler. Get Sessions connected to this
                object with sessions.get()
     attributes - attribute-handler. Use attributes.add/remove/get.
     db - attribute-handler: Shortcut for attribute-handler. Store/retrieve
            database attributes using self.db.myattr=val, val=self.db.myattr
     ndb - non-persistent attribute handler: same as db but does not create
            a database entry when storing data

    * Helper methods (see src.objects.objects.py for full headers)

     search(ostring, global_search=False, attribute_name=None,
             use_nicks=False, location=None, ignore_errors=False, account=False)
     execute_cmd(raw_string)
     msg(text=None, **kwargs)
     msg_contents(message, exclude=None, from_obj=None, **kwargs)
     move_to(destination, quiet=False, emit_to_obj=None, use_destination=True)
     copy(new_key=None)
     delete()
     is_typeclass(typeclass, exact=False)
     swap_typeclass(new_typeclass, clean_attributes=False, no_default=True)
     access(accessing_obj, access_type='read', default=False)
     check_permstring(permstring)

    * Hooks (these are class methods, so args should start with self):

     basetype_setup()     - only called once, used for behind-the-scenes
                            setup. Normally not modified.
     basetype_posthook_setup() - customization in basetype, after the object
                            has been created; Normally not modified.

     at_object_creation() - only called once, when object is first created.
                            Object customizations go here.
     at_object_delete() - called just before deleting an object. If returning
                            False, deletion is aborted. Note that all objects
                            inside a deleted object are automatically moved
                            to their <home>, they don't need to be removed here.

     at_init()            - called whenever typeclass is cached from memory,
                            at least once every server restart/reload
     at_cmdset_get(**kwargs) - this is called just before the command handler
                            requests a cmdset from this object. The kwargs are
                            not normally used unless the cmdset is created
                            dynamically (see e.g. Exits).
     at_pre_puppet(account)- (account-controlled objects only) called just
                            before puppeting
     at_post_puppet()     - (account-controlled objects only) called just
                            after completing connection account<->object
     at_pre_unpuppet()    - (account-controlled objects only) called just
                            before un-puppeting
     at_post_unpuppet(account) - (account-controlled objects only) called just
                            after disconnecting account<->object link
     at_server_reload()   - called before server is reloaded
     at_server_shutdown() - called just before server is fully shut down

     at_access(result, accessing_obj, access_type) - called with the result
                            of a lock access check on this object. Return value
                            does not affect check result.

     at_pre_move(destination)             - called just before moving object
                        to the destination. If returns False, move is cancelled.
     announce_move_from(destination)         - called in old location, just
                        before move, if obj.move_to() has quiet=False
     announce_move_to(source_location)       - called in new location, just
                        after move, if obj.move_to() has quiet=False
     at_post_move(source_location)          - always called after a move has
                        been successfully performed.
     at_object_leave(obj, target_location)   - called when an object leaves
                        this object in any fashion
     at_object_receive(obj, source_location) - called when this object receives
                        another object

     at_traverse(traversing_object, source_loc) - (exit-objects only)
                              handles all moving across the exit, including
                              calling the other exit hooks. Use super() to retain
                              the default functionality.
     at_post_traverse(traversing_object, source_location) - (exit-objects only)
                              called just after a traversal has happened.
     at_failed_traverse(traversing_object)      - (exit-objects only) called if
                       traversal fails and property err_traverse is not defined.

     at_msg_receive(self, msg, from_obj=None, **kwargs) - called when a message
                             (via self.msg()) is sent to this obj.
                             If returns false, aborts send.
     at_msg_send(self, msg, to_obj=None, **kwargs) - called when this objects
                             sends a message to someone via self.msg().

     return_appearance(looker) - describes this object. Used by "look"
                                 command by default
     at_desc(looker=None)      - called by 'look' whenever the
                                 appearance is requested.
     at_get(getter)            - called after object has been picked up.
                                 Does not stop pickup.
     at_drop(dropper)          - called when this object has been dropped.
     at_say(speaker, message)  - by default, called if an object inside this
                                 object speaks

    """
    

    
    pass


