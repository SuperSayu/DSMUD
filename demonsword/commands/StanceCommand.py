"""
    Stance commands are used to manage your skillsets: Stance, Role (Class), and job.
    They need to show your skillset status, list alternatives, load a predefined skillset,
    create a new skillset, and modify a skillset. 
"""
#from .command import MuxCommand
#pass
from evennia.commands.default.muxcommand import MuxCommand
from world.skills import SkillDB
SkillDB = SkillDB()

class StanceCommand(MuxCommand):
    """
    Stance: View and manage your current Stance skillset.  Every skillset has a number of slots
    based on its level, and every slot can be associated with a character Aspect.
    
    Unimplemented:
    Stance[/Set] [Stance Name] :: Set current stance or View current stance    
    Stance/View [Stance Name][:Aspect] :: Show current stance, or more information on the skills in a stance, or all stances 
    Stance/List :: List available stances
    Stance/Create Stance Name :: Create new stance
    Stance/Remove Stance Name :: Delete existing stnace
    Stance/Edit [Stance Name:]Aspect=Skill :: Set skill to aspect slot on current or other skill set
    Stance/Lock [Stance Name][:Aspect] or [Stance Name][=Skill] :: Lock a skill in a skillset so it cannot be overridden.
    """
    key="stance"
    aliases=["stances"]
    sstype = "stance"
    valid_commands = ["create","edit","remove","view","list","set","lock","rename"]
    command=None
    lhs_sections=[]
    rhs_sections=[]
    fieldlen = 15
    fieldsep = " |C|||n "
    seplen = 4 # don't take into consideration any formatting.  4 instead of 3 by default is not a typo, idk lol it works
    nFields = 4
    
    def parse(self):
        super().parse()
        self.fault = None
        if len(self.switches) > 1:
            self.fault = "Too many switches"
            return
        self.command = self.switches[0].lower() if len(self.switches) > 0 else "set"
        if not self.command in self.valid_commands:
            self.fault = f"Unknown command switch {self.command}"
            return
        if len(self.lhs) > 0:
            self.lhs_sections = [*map(str.strip,self.lhs.split(":"))] if ':' in self.lhs else None
        if len(self.rhs or "") > 0:
            self.rhs_sections = [*map(str.strip,self.rhs.split(":"))] if ':' in self.rhs else None

    def func(self):
        if self.fault != None:
            self.caller.msg(f"Fault: {self.fault}")
            return
        match self.command:
            case "set":
                self.DoSet(self.lhs)
            case "view":
                self.View(self.args)
            case "create":
                self.Create(self.lhs)
            case "edit":
                self.Edit(self.lhs_sections or [self.lhs],self.rhs)
            case "remove":
                self.Remove(self.lhs)
            case "rename":
                self.Rename(self.lhs,self.rhs)
            case "list":
                self.List()
                
            case _:
                self.caller.msg(f"Unimplemented Command {self.command}")
    def validate_skillname(self,incoming):
        if not isinstance(incoming,str) or len(incoming) == 0:
            return False
        invalid_chars=[":","#","!","/","\\"]
        for x in invalid_chars:
            if x in incoming:
                return False
        return True
    def Create(self,lhs):
        if self.caller.skills.skillset_exists(lhs,self.sstype):
            self.caller.msg(f"Create Skillset: {lhs} already exists")
            return
        _=self.caller.skills.get_skillset(lhs,self.sstype)
        self.caller.msg(f"Created skillset {_.key}")
    def Rename(self,lhs,rhs):
        if len(lhs) and rhs != None:
            self.caller.skills.rename_skillset(lhs,rhs,self.sstype)
        else:
            self.caller.msg("{self.key}/rename old_key=new_key")
        return
    def DoSet(self,lhs):
        if lhs == "":
            self.View(lhs)
            return
        self.caller.skills.activate_skillset(self.lhs,self.sstype)
    def Edit(self,lhs_sections, rhs):
        helptext="Stance/Edit [Stance Name:]Aspect=Skill :: Set skill to aspect slot on current or other skill set"
        aspect = None
        skill = rhs
        skillset = self.caller.skills.active_skillset(self.sstype)
        if self.rhs == None or len(self.lhs) < 3:
            self.caller.msg(helptext)
            return
        if len(lhs_sections) == 1:
            aspect = lhs_sections[0] 
        elif len(lhs_sections) == 2:
            if not self.caller.skills.skillset_exists(lhs_sections[0]):
                self.caller.msg(f"{self.sstype.capitalize()} does not exist: {lhs_sections[0]}")
                return
            skillset = self.caller.skills.get_skillset(lhs_sections[0])
            aspect=lhs_sections[1]
        if rhs == "":
            skillset.SetSkill(aspect,None)
        else:
            skillset.SetSkill(aspect,rhs)
    def ViewLine(self,title,x):
        return f"* {title}: {x.data if x != None else 'None'}"
    def View(self,lhs):
        self.caller.msg(f"Your currently slotted skillsets are:")
        self.caller.msg(self.ViewLine('stance',self.caller.skills.stance))
        self.caller.msg(self.ViewLine('job',self.caller.skills.job))
        self.caller.msg(self.ViewLine('role',self.caller.skills.role))
        self.caller.msg("You currently have these skills active:")
        act = set(self.caller.skills.stance.loaded.values())
        act.union( set(self.caller.skills.job.loaded.values()) if self.caller.skills.job != None else set() )
        act.union( set(self.caller.skills.role.loaded.values()) if self.caller.skills.role != None else set() )
        self.caller.msg(", ".join(act))
        
    def List(self):
        self.caller.msg(f"These are your existant {self.sstype}s:")
        for ss in self.caller.attributes.all(category=self.sstype):
            self.caller.msg(str(ss.key))
    def Remove(self,lhs):
        if lhs != "":
            self.caller.skills.del_skillset(lhs,self.sstype)
            
class JobCommand(StanceCommand):
    sstype="job"
    key="job"
    aliases=[]
class RoleCommand(StanceCommand):
    sstype="role"
    key="role"
    aliases=[]