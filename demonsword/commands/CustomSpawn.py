from evennia.prototypes import menus as olc_menus
from evennia.prototypes import prototypes as protlib
from evennia.prototypes import spawner
from evennia.utils.utils import list_to_string
from evennia.commands.default.building import CmdSpawn,CmdCreate
from evennia.utils import create


# I could wish simplify this further
# I only need to insert one thing
class SpawnCommand(CmdSpawn):
    def func(self):
        """Implements the spawner"""

        caller = self.caller
        noloc = "noloc" in self.switches

        # run the menu/olc
        if (
            self.cmdstring == "olc"
            or "menu" in self.switches
            or "olc" in self.switches
            or "edit" in self.switches
        ):
            # OLC menu mode
            prototype = None
            if self.lhs:
                prototype_key = self.lhs
                prototype = self._search_prototype(prototype_key)
                if not prototype:
                    return
            olc_menus.start_olc(caller, session=self.session, prototype=prototype)
            return

        if "search" in self.switches:
            # query for a key match. The arg is a search query or nothing.

            if not self.args:
                # an empty search returns the full list
                self._list_prototypes()
                return

            # search for key;tag combinations
            key, _, tags = self._parse_key_desc_tags(self.args, desc=False)
            self._list_prototypes(key, tags)
            return

        if "raw" in self.switches:
            # query for key match and return the prototype as a safe one-liner string.
            if not self.args:
                caller.msg("You need to specify a prototype-key to get the raw data for.")
            prototype = self._search_prototype(self.args)
            if not prototype:
                return
            caller.msg(str(prototype))
            return

        if "show" in self.switches or "examine" in self.switches:
            # show a specific prot detail. The argument is a search query or empty.
            if not self.args:
                # we don't show the list of all details, that's too spammy.
                caller.msg("You need to specify a prototype-key to show.")
                return

            detail_string = self._get_prototype_detail(self.args)
            if not detail_string:
                return
            caller.msg(detail_string)
            return

        if "list" in self.switches:
            # for list, all optional arguments are tags.
            tags = self.lhslist
            err = self._list_prototypes(tags=tags)
            if err:
                caller.msg(
                    "No prototypes found with prototype-tag(s): {}".format(
                        list_to_string(tags, "or")
                    )
                )
            return

        if "save" in self.switches:
            # store a prototype to the database store
            if not self.args:
                caller.msg(
                    "Usage: spawn/save [<key>[;desc[;tag,tag[,...][;lockstring]]]] ="
                    " <prototype_dict>"
                )
                return
            if self.rhs:
                # input on the form key = prototype
                prototype_key, prototype_desc, prototype_tags = self._parse_key_desc_tags(self.lhs)
                prototype_key = None if not prototype_key else prototype_key
                prototype_desc = None if not prototype_desc else prototype_desc
                prototype_tags = None if not prototype_tags else prototype_tags
                prototype_input = self.rhs.strip()
            else:
                prototype_key = prototype_desc = None
                prototype_tags = None
                prototype_input = self.lhs.strip()

            # handle parsing
            prototype = self._parse_prototype(prototype_input)
            if not prototype:
                return

            prot_prototype_key = prototype.get("prototype_key")

            if not (prototype_key or prot_prototype_key):
                caller.msg(
                    "A prototype_key must be given, either as `prototype_key = <prototype>` "
                    "or as a key 'prototype_key' inside the prototype structure."
                )
                return

            if prototype_key is None:
                prototype_key = prot_prototype_key

            if prot_prototype_key != prototype_key:
                caller.msg("(Replacing `prototype_key` in prototype with given key.)")
                prototype["prototype_key"] = prototype_key

            if prototype_desc is not None and prot_prototype_key != prototype_desc:
                caller.msg("(Replacing `prototype_desc` in prototype with given desc.)")
                prototype["prototype_desc"] = prototype_desc
            if prototype_tags is not None and prototype.get("prototype_tags") != prototype_tags:
                caller.msg("(Replacing `prototype_tags` in prototype with given tag(s))")
                prototype["prototype_tags"] = prototype_tags

            string = ""
            # check for existing prototype (exact match)
            old_prototype = self._search_prototype(prototype_key, quiet=True)

            diff = spawner.prototype_diff(old_prototype, prototype, homogenize=True)
            diffstr = spawner.format_diff(diff)
            new_prototype_detail = self._get_prototype_detail(prototypes=[prototype])

            if old_prototype:
                if not diffstr:
                    string = f"|yAlready existing Prototype:|n\n{new_prototype_detail}\n"
                    question = (
                        "\nThere seems to be no changes. Do you still want to (re)save? [Y]/N"
                    )
                else:
                    string = (
                        f'|yExisting prototype "{prototype_key}" found. Change:|n\n{diffstr}\n'
                        f"|yNew changed prototype:|n\n{new_prototype_detail}"
                    )
                    question = (
                        "\n|yDo you want to apply the change to the existing prototype?|n [Y]/N"
                    )
            else:
                string = f"|yCreating new prototype:|n\n{new_prototype_detail}"
                question = "\nDo you want to continue saving? [Y]/N"

            answer = yield (string + question)
            if answer.lower() in ["n", "no"]:
                caller.msg("|rSave cancelled.|n")
                return

            # all seems ok. Try to save.
            try:
                prot = protlib.save_prototype(prototype)
                if not prot:
                    caller.msg("|rError saving:|R {}.|n".format(prototype_key))
                    return
            except protlib.PermissionError as err:
                caller.msg("|rError saving:|R {}|n".format(err))
                return
            caller.msg("|gSaved prototype:|n {}".format(prototype_key))

            # check if we want to update existing objects

            self._update_existing_objects(self.caller, prototype_key, quiet=True)
            return

        if not self.args:
            # all switches beyond this point gets a common non-arg return
            ncount = len(protlib.search_prototype())
            caller.msg(
                "Usage: spawn <prototype-key> or {{key: value, ...}}"
                f"\n ({ncount} existing prototypes. Use /list to inspect)"
            )
            return

        if "delete" in self.switches:
            # remove db-based prototype
            prototype_detail = self._get_prototype_detail(self.args)
            if not prototype_detail:
                return

            string = f"|rDeleting prototype:|n\n{prototype_detail}"
            question = "\nDo you want to continue deleting? [Y]/N"
            answer = yield (string + question)
            if answer.lower() in ["n", "no"]:
                caller.msg("|rDeletion cancelled.|n")
                return

            try:
                success = protlib.delete_prototype(self.args)
            except protlib.PermissionError as err:
                retmsg = f"|rError deleting:|R {err}|n"
            else:
                retmsg = (
                    "Deletion successful"
                    if success
                    else "Deletion failed (does the prototype exist?)"
                )
            caller.msg(retmsg)
            return

        if "update" in self.switches:
            # update existing prototypes
            prototype_key = self.args.strip().lower()
            self._update_existing_objects(self.caller, prototype_key)
            return

        # If we get to this point, we use not switches but are trying a
        # direct creation of an object from a given prototype or -key

        prototype = self._parse_prototype(
            self.args, expect=dict if self.args.strip().startswith("{") else str
        )
        if not prototype:
            # this will only let through dicts or strings
            return

        key = "<unnamed>"
        if isinstance(prototype, str):
            # A prototype key we are looking to apply
            prototype_key = prototype
            prototype = self._search_prototype(prototype_key)

            if not prototype:
                return

        # proceed to spawning
        try:
            for obj in spawner.spawn(prototype, caller=self.caller):
                self.caller.msg("Spawned %s." % obj.get_display_name(self.caller))
                if not prototype.get("location") and not noloc:
                    # we don't hardcode the location in the prototype (unless the user
                    # did so manually) - that would lead to it having to be 'removed' every
                    # time we try to update objects with this prototype in the future.
                    obj.location = caller.location
                obj.at_post_spawn(caller=self.caller)
        except RuntimeError as err:
            caller.msg(err)

class CreateCommand(CmdCreate):
    def func(self):
        """
        Creates the object.
        """

        caller = self.caller

        if not self.args:
            string = "Usage: create[/drop] <newname>[;alias;alias...] [:typeclass.path]"
            caller.msg(string)
            return

        # create the objects
        for objdef in self.lhs_objs:
            string = ""
            name = objdef["name"]
            aliases = objdef["aliases"]
            typeclass = objdef["option"]

            # create object (if not a valid typeclass, the default
            # object typeclass will automatically be used)
            lockstring = self.new_obj_lockstring.format(id=caller.id)
            loc = caller.location
            if loc == None:
                loc = caller
            obj = create.create_object(
                typeclass,
                name,
                loc,
                home=loc,
                aliases=aliases,
                locks=lockstring,
                report_to=caller,
            )
            if not obj:
                continue
            if aliases:
                string = (
                    f"|CYou create a new |y{obj.typename}|C: |w{obj.name}|C (aliases: |w{', '.join(aliases)}|C).|n"
                )
            else:
                string = f"|CYou create a new |y{obj.typename}|C: |w{obj.name}|C.|n"
            # set a default desc
            if not obj.db.desc:
                obj.db.desc = "You see nothing special."
            if not "drop" in self.switches:
                caller.items.pickup(obj,silent=True)
        if string:
            caller.msg(string)