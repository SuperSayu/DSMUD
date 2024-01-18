from evennia.commands.default.muxcommand import MuxCommand

class SceneCommand(MuxCommand):
    """
    The Scene command is used to create, examine, and modify the SceneObjects in a room.
    SceneObjects do not show up as normal objects, and are included in the room description.
    
    Scene[/View] [ObjName] : Shows a list of scene objects, or details on one.    
    Scene/Tag EventTag[:type][=Value]

    Unimplemented:    
    Scene/Create ObjName[:Class][:Priority] [=BGDesc]
    Scene/Edit ObjName=Field:Value
    Scene/Remove ObjName
    
    # SUBTOPICS
    ## view
    Lists the scene objects in the current room, or more detail about a given
    SceneCbject in the current room.
    Scene[/view]: List scene objects
    Scene[/view] ObjName: Show Scene Object variables, including look description
                          and scene description.
    
    Only variables shown in this list should be edited using the Scene/Edit verb.
    ## tag
    Show, set, edit, or unset scene tags on a room.  Scene tags are used by some
    scene objects to react to events.  Not all scene objects can use them.
    Scene/tag tagname[:type][=value]
    
    The type should be one of str, int, or bool.  To unset (remove) a tag,
    give '=' with no value, eg, 'Scene/tag toRemove='
    """
    key="Scene"
    locks="cmd:perm(Builder)"    
    
    fault=None
    valid_commands = ["create","edit","remove","view","tag"]
    command=None
    fieldlen = 15
    fieldsep = " |C|||n "
    seplen = 4 # don't take into consideration any formatting.  4 instead of 3 by default is not a typo, idk lol it works
    nFields = 4
    lhs_sections=[]
    rhs_sections=[]
    
    def parse(self):
        super().parse()
        self.fault = None
        if len(self.switches) > 1:
            self.fault = "Too many switches"
            return
        self.command = self.switches[0].lower() if len(self.switches) > 0 else "view"
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
            case "view":
                self.View(self.args)
            case "create":
                self.Create(self.lhs_sections or [self.lhs],self.rhs)
            case "edit":
                pass
            case "remove":
                pass
            case "tag":
                self.Tag(self.lhs_sections or [self.lhs],self.rhs)
            case _:
                self.caller.msg(f"Fault: Unknown Command '{self.command}'")
    
    def SceneList(self,filter=None):
        "Get all scene objects in this location, or the named scene object if it exists"
        result = self.caller.location.contents_get(content_type="scene")
        if len(filter) > 0:
            if filter[0]=="#":
                for x in result:
                    if x.dbref == filter:
                        return [x]
            else:
                for x in result:
                    if x.key == filter:
                        return [x]
        return result             

    def TotalLen(self):
        "Approximate length of the table, based on number of fields and separator"
        return self.fieldlen * self.nFields + self.seplen * (self.nFields-1)
    def SepLine(self):
        "Create a separator line"
        return f"|C{'-' * self.TotalLen()}|n"
    def Field(self,txt):
        "Normalize the length of table fields"
        return str(txt).center(self.fieldlen)
    def ViewTableHeader(self):
        "Print the table header"
        headers = ["Priority","dbref","Key","Class"]
        return self.fieldsep.join([*map(self.Field,headers)]) + f"|/{self.SepLine()}"
    def ViewTableRow(self,SceneObject,extended=False):
        "Print a table row.  If only one scene object is given, add extra data."
        values=[SceneObject.priority,SceneObject.dbref,SceneObject.name,SceneObject.__class__.__name__]
        line=self.fieldsep.join([*map(self.Field,values)])
        if extended:
            line += f"|/{self.SepLine()}"
            for v in SceneObject.LongSceneVars:
                line += f"|/{self.Field(v)}{self.fieldsep}{SceneObject.attributes.get(v)}"
        return line
        
    def ViewTableMsg(self,msg):
        "Print a single line centered on the table, for errors etc."
        return str(msg).center(self.TotalLen())
    def ViewTableBody(self,objects):
        "The whole body of the table"
        if len(objects) == 0:
            return self.ViewTableMsg("There are no scene objects in this location.")
        if len(objects) == 1:
            return self.ViewTableRow(objects[0],True)
        return "|/".join([*map(self.ViewTableRow,objects)])
        
    def View(self,selected=None):
        "View a list of scene objects currently in the room, or get details on one in particular."
        show=self.SceneList(selected)
        show.sort()
        self.caller.msg(f"|/Scene objects in |w{self.caller.location}({self.caller.location.dbref})|n")
        self.caller.msg(f"{self.ViewTableHeader()}|/{self.ViewTableBody(show)}|/|/")
    
    def Create(self,lhs,rhs):
        "My ass"
        pass
    def Tag(self,lhs_sections,rhs):
        "Tag"
        if lhs_sections[0]=="": # no arguments given
            self.caller.msg(f"|/|w{self.caller.location}({self.caller.location.dbref})|n state: ")
            s = self.caller.location.state
            if len(s) == 0:
                self.caller.msg("* There are no scene state tags set.")
                return
            for k,v in s.items():
                t = type(v).__name__
                self.caller.msg(f"{self.Field(k)} = {t}({v})")
            return
        if len(lhs_sections) > 2:
            self.caller.msg(f"|rScene/Tag: Too many ':' in lhs|n")
            return
        force_type = bool
        if len(lhs_sections) == 2:
            match lhs_sections[1].lower():
                case "int":
                    force_type=int
                case "bool":
                    pass
                case "str":
                    force_type=str
                case "_":
                    self.caller.msg(f"|rType should be in list: (int,bool,str)|n")
                    return
        tagname = lhs_sections[0]
        if rhs != None:
            if rhs == "":
                del self.caller.location.state[tagname]
                self.caller.msg(f"|/|yUnset|n scene state tag |w{tagname}|n")
                return
            v = force_type(rhs)
            t = type(v).__name__
            self.caller.location.state[tagname]=v
            self.caller.msg(f"|/|ySet |w{self.caller.location}({self.caller.location.dbref})|n scene state |w{tagname}|n to {t}({v})")
        else:
            if tagname in self.caller.location.state:
                v = self.caller.location.state[tagname]
                t = type(v).__name__
                self.caller.msg(f"|/|w{self.caller.location}({self.caller.location.dbref})|n: Scene state tag |w{tagname}|n is {t}({v})")
            else:
                self.caller.msg(f"|/|w{self.caller.location}({self.caller.location.dbref})|n: Scene state tag |w{tagname}|n is unset.")