"""
Command sets

All commands in the game must be grouped in a cmdset.  A given command
can be part of any number of cmdsets and cmdsets can be added/removed
and merged onto entities at runtime.

To create new commands to populate the cmdset, see
`commands/command.py`.

This module wraps the default command sets of Evennia; overloads them
to add/remove commands from the default lineup. You can create your
own cmdsets by inheriting from them or directly from `evennia.CmdSet`.

"""

from evennia import default_cmds
from .forage import ForageCommand,MineCommand
from .rest import RestCommand,TrainCommand,MeditateCommand,SleepCommand,ResetStatsCommand
from .stat_skill import StatsCommand,SkillsCommand
from .StateCommandBase import StopCommand
from .get_override import GetCommand,DropCommand,InventoryCommand,SwapHandsCommand,PutCommand,WearCommand,RemoveCommand,LookInCommand
from .CustomSpawn import SpawnCommand,CreateCommand
from .SceneCommand import SceneCommand
from .StanceCommand import StanceCommand,JobCommand,RoleCommand
class CharacterCmdSet(default_cmds.CharacterCmdSet):
    """
    The `CharacterCmdSet` contains general in-game commands like `look`,
    `get`, etc available on in-game Character objects. It is merged with
    the `AccountCmdSet` when an Account puppets a Character.
    """

    key = "DefaultCharacter"

    def at_cmdset_creation(self):
        "Populates the cmdset"
        super().at_cmdset_creation()
        
        # Inventory commands
        self.add(GetCommand())
        self.add(DropCommand())
        self.add(PutCommand())
        self.add(WearCommand())
        self.add(RemoveCommand())
        self.add(InventoryCommand())
        self.add(LookInCommand())
        self.add(SwapHandsCommand())
        
        #
        # Character self-examination
        #
        self.add(StatsCommand())
        self.add(SkillsCommand())
        
        # Stop doing busy things
        self.add(StopCommand())
        
        #
        # These are mostly test commands intended to be the basis for the skill/stat advancements
        #
        self.add(ForageCommand())
        self.add(MineCommand())
        self.add(RestCommand())
        self.add(TrainCommand())
        self.add(MeditateCommand())
        self.add(SleepCommand())
        self.add(ResetStatsCommand())
        
        self.add(SpawnCommand())
        self.add(CreateCommand())
        
        # This is still in testing/creation phase
        self.add(SceneCommand())
        self.add(StanceCommand())


class AccountCmdSet(default_cmds.AccountCmdSet):
    """
    This is the cmdset available to the Account at all times. It is
    combined with the `CharacterCmdSet` when the Account puppets a
    Character. It holds game-account-specific commands, channel
    commands, etc.
    """

    key = "DefaultAccount"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #


class UnloggedinCmdSet(default_cmds.UnloggedinCmdSet):
    """
    Command set available to the Session before being logged in.  This
    holds commands like creating a new account, logging in, etc.
    """

    key = "DefaultUnloggedin"

    def at_cmdset_creation(self):
        """
        Populates the cmdset
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #


class SessionCmdSet(default_cmds.SessionCmdSet):
    """
    This cmdset is made available on Session level once logged in. It
    is empty by default.
    """

    key = "DefaultSession"

    def at_cmdset_creation(self):
        """
        This is the only method defined in a cmdset, called during
        its creation. It should populate the set with command instances.

        As and example we just add the empty base `Command` object.
        It prints some info.
        """
        super().at_cmdset_creation()
        #
        # any commands you add below will overload the default ones.
        #
