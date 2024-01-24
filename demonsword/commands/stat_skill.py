"""
	Commands for viewing your stats and skills
"""
from evennia import Command
from typeclasses.attr_aspect import AspectList,AttributeList,StatNames,AttributeToAspectsIndex
from evennia.utils.evtable import EvTable
from util.strings import fract
class SkillsCommand(Command):
    """
        Your skills will be checked when you attempt anything useful.
        Your skill's effort, training, affinity, and mastery will provide
        increasing value.  When you cannot gain any more experience, rest.
        When your effort is maxed, train.  When your training is maxed,
        meditate.  Your maximum of each goes up when stats above it raise.
        
        When you first train, you will associate skills with an attribute.
        Later, you will associate skills with an aspect.
        I hate your face.
    """
    key="skill"
    aliases=["skills"]
    cols = [
        ("|wSkill Name (Stat)|n", lambda s: f"|w{s.name}({s.stat})|n"),
        ("|wActive|n",lambda s:"None" if s.active == None else f"|w{s.parent.skills.stance.key}|n stance" if s.active == True else f"|w{(s.parent.skills.role or s.parent.skills.job).ident()}|n"),
        ("|wEXP|n",lambda s: fract(s.exp)),
        ("|wEV|n", lambda s: s.EV), # already a formatted string
        ("|wStat|n", lambda s: s.statValue),
        ("|wEffort|n", lambda s:f"{s.streak_str()}/{s.effort}"),
        ("|wTraining|n",lambda s:s.training),
        ("|wAffinity|n",lambda s:s.affinity),
        ("|wMastery|n",lambda s:s.mastery),

        ]
    def SkillGrid(self,skill=None):
        # zip(*cols) produces rows, and vice versa
        headers, funcs = zip(*self.cols)
        data = None
        if skill != None and skill in self.caller.skills:
            skillObj = self.caller.skills[skill]
            data = [*map(lambda func: func(skillObj), funcs)] # rows of data
            data = [*map(lambda val: [val], data)] # cols of data
            self.caller.msg(EvTable(*headers, table=data,pad_width=0,pad_left=1,pad_right=1,align='c',border='incols'))
            self.caller.msg(f"|/|w{skillObj.name}|n: {skillObj.desc}|/|/")
            return
        data = []
        for skillObj in self.caller.skills:
            data.append( [*map(lambda func: func(skillObj), funcs)] )
        data = [*map(lambda tup: list(tup), zip(*data))] # cols of data # [rows] -> [cols]
        self.caller.msg(EvTable(*headers, table=data,pad_width=0,pad_left=1,pad_right=1,align='c',border='incols'))
    def parse(self):
        if self.args == "//debug/reset":
            self.caller.skills._reset()
            self.caller.msg("|r---= Debug: Resetting all skills =---|n")
            self.args = ""
            return
        self.args = self.args.strip().lower()
        self.raw = self.args.startswith("/raw")
        if self.raw:
            self.args = self.args[4:].strip()
        
    def func(self):
        target=self.args.strip().lower()
        if len(target):
            if not target in self.caller.skills:
                self.caller.msg(f"You do not currently have the |w{target}|n skill")
                return
            if self.raw:
                s = self.caller.skills[target]
                self.caller.msg(f"{str(s.data)}")
            else:
                self.SkillGrid(target)#self.caller.skills.show(target)
        else:
            self.SkillGrid()#self.caller.skills.show()

class StatsCommand(Command):
    """
    The Stat command shows your character Stats and Aspects.
    Your Stats are the basic character values such as Strength and Intelligence.
    They are grouped into rows and columns called Aspects; you can understand what
    a Stat is used for based on the Aspects, for example, Strength is Power of Body.
    Your stats are used for related skills and will gain experience and advance
    as they are used.
    
    When specifying stats and aspects, always use the three-letter code.
    """
    key="stat"
    aliases=["stats","aspect","aspects"]
    def parse(self):
        if self.args == "//debug/reset": # I already had this but had to run it with py, this should never be found by users
            self.caller.msg("|r---= Debug: Resetting all stats =---|n")
            self.caller.stats._reset()
            self.selected=None
            return
        self.args = self.args.lower().strip()
        self.raw = self.args.startswith("/raw")
        if self.raw:
            self.args = self.args[4:].strip()
        # I am aware how inefficient these list/string operations are, but whatever
        if len(self.args)==3 and self.args in StatNames:
            self.selected = self.args
        else:
            self.selected=None
    def StatGrid(self,with_values=True) -> EvTable:
        table=[]
        cols=[['luc','pow','fin','cap','res','aes','hea'],['bod','str','dex','stm','con','bea','hp'],['mnd','int','wit','mem','stb','san','mp'],['spr','wil','per','aur','wis','gra','sp']]
        if self.selected != None:
            selected_row = None
            selected_col = None
            if self.selected in AspectList:
                i = AspectList.index(self.selected)
                if i < 3:
                    selected_col = i+1
                else:
                    selected_row = i - 2
            else:
                selected_col,selected_row = AttributeToAspectsIndex(self.selected)
                selected_col += 1
                selected_row -= 2
            if selected_col != None:
                cols = [ cols[0], cols[selected_col] ]
            if selected_row != None:
                for i in range(0,len(cols)):
                    cols[i] = [ cols[i][0], cols[i][selected_row]]
        if not with_values:
            table = cols
        else:
            for col in cols:
                c = []
                for r in col:
                    if r in AspectList:
                        c.extend( [f"|w{StatNames[r]} ({r.upper()})|n", f"|c{self.caller.stats[r].value}|n" ] )
                    else:
                        s = self.caller.stats[r]
                        c.extend( [f"{StatNames[r]} ({r.upper()})", f"|y+{s.value}|n ({fract(s.exp)}XP)" ] )
                table.append( c )
        return EvTable(table=table,pad_width=0,pad_left=1,pad_right=1,align='c',border='incols')
    def func(self):
        self.caller.msg("Your stats:")
#        self.caller.msg(self.caller.stats.show())
        if not self.selected:
            t = self.StatGrid()
            self.caller.msg(str(t))
        else:
            if not self.raw:
                self.caller.msg(self.StatGrid())
            else:
                s = self.caller.stats[self.selected]
                self.caller.msg(str(s.data))