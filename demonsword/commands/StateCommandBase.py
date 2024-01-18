"""
    State commands put the character in a State
    and take some amount of time to execute, updating
    periodically.
    
    Instead of func, please use define state_start, state_continue, state_cancel, and state_finish.
    Call cancel or finish to interrupt the state.
    While running, the character's busy state will be set to this command.
    Characters cannot be busy with two things at once, and commands will refuse to start while busy.
    Running the same command while busy will cancel it.
"""
from evennia import Command
from evennia.utils import delay
from sys import exc_info
from random import randint
from traceback import format_tb

class StopCommand(Command):
    """
        Stops any command that is currently keeping you Busy.
    """
    key="stop"
    def func(self):
        if self.caller.busy:
            b=self.caller.busy
            self.caller.msg(f"You force yourself to stop {self.caller.busy.doing}.")
            self.caller.busy.cancel() # Try to be nice
            if self.caller.busy == b: # did not stop
                self.caller.busy = None
        else:
            self.caller.msg("You aren't busy.")


class StateCommand(Command):
    tick_secs = 1
    skip_ticks = 0
    running = False
    doing = "doing" # This word will be used to describe what you're doing in an ongoing manner, eg, walking, thinking, breathing,
    
    def at_pre_cmd(self):
        """
            Command refuses to run if the character is already busy.
            Running the command while already in this state will cancel it.
        """
        if self.caller.busy:
            if type(self.caller.busy) == type(self):
                self.caller.busy.at_pre_state_cancel()
                return True
            else:
                self.caller.msg(f"You are already busy |y{self.caller.busy.doing}|n.")
                return True
        return None
    def func(self):
        """
            When the command starts, run the state_start() command tree
            Either pre or start can cancel the command by returning true
            These are blocking functions, so state_start cannot yield or request input.
            If not cancelled, begin polling the state_continue tree every [tick_secs] seconds.
            This will continue until you either cancel or finish the state.
            If the character ceases to be busy with us, we will also immediately cancel.
        """
        if self.at_pre_state_start():
            return
        if self.state_start():
            return
        self.at_post_state_start()
        delay(self.tick_secs,self.at_pre_state_continue)
        self.at_post_state_start()
    
    def sleep(self,ticks:int = 0):
        """
            A built-in sleep timer using tick_secs as a base (default: 1)
            Note that this does not suspend execution at the moment sleep is called.
            Instead this does not call state_continue until so many ticks have passed.
            The state can be cancelled or finished before the next continue.
            This relies on the base functionality of pre_state_continue.
        """
        if ticks == None:
            ticks = 0
        elif not (type(ticks) in [int,float]):
            raise TypeError("StateCommand.sleep() takes one integer argument.")
        self.skip_ticks = int(ticks)
    def sleep_rand(self,min_ticks:int,max_ticks:int):
        """
            Variant of sleep that sets the built-in sleep timer randomly
            between min_ticks and max_ticks (inclusive).
        """
        self.skip_ticks = randint(min_ticks,max_ticks)
    
    def cancel(self):
        self.at_pre_state_cancel()
        self.state_cancel()
        self.at_post_state_cancel()
    def finish(self):
        self.at_pre_state_finish()
        self.state_finish()
        self.at_post_state_finish()
        
    def at_pre_state_cancel(self):
        self.running = False
    def state_cancel(self):
        pass
    def at_post_state_cancel(self):
        if self.caller.busy == self:
            self.caller.busy = None
        pass
    def at_pre_state_finish(self):
        self.running = False
    def state_finish(self):
        pass
    def at_post_state_finish(self):
        if self.caller.busy == self:
            self.caller.busy = None
        pass    
    
    def at_pre_state_start(self):
        return None
    def state_start(self):
        return None
    def at_post_state_start(self):
        self.running = True
        self.caller.busy = self
    
    def at_pre_state_continue(self):
        try:
            if not self.running or self.caller.busy != self:
                if self.running: # canceled by mucking with caller.busy
                    self.cancel()
                    self.running = False
                if self.caller.busy == self:
                    self.caller.busy = None
                return
            if self.skip_ticks > 0:
                self.skip_ticks -= 1
                self.state_skipped() # In case you have background tasks
                self.at_post_state_skipped()
                return
            self.state_continue()
            if self.running and self.caller.busy == self:
                self.at_post_state_continue()
            else:
                self.running = False
                if self.caller.busy == self:
                    self.caller.busy = None
        except:
            [_, err, tb] = exc_info()
            self.caller.log_error(err,"".join(format_tb(tb)))
            del tb # According to the docs storing the trace here creates a memory leak
    def state_continue(self):
        # If nothing is requested just immediately stop
        self.finish()
    def at_post_state_continue(self):
        delay(self.tick_secs,self.at_pre_state_continue)
    
    # Skipped state means you called a sleep and it has yet to resolve
    # Use this if you need to do background checks
    def state_skipped(self):
        pass
    def at_post_state_skipped(self):
        delay(self.tick_secs,self.at_pre_state_continue)
