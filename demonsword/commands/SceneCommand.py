from evennia.commands.default.muxcommand import MuxCommand
from evennia.utils import create

class SceneCommand(MuxCommand):
    """
    The Scene command is used to create, examine, and modify the SceneObjects in a room.
    SceneObjects do not show up as normal objects, and are included in the room description.
    
    Scene[/View] [ObjName] : Shows a list of scene objects, or details on one.    
    Scene/Tag EventTag[:type][=Value]

    Unimplemented:    
    Scene/Create ObjName[:Class][:Priority] [=scene_desc]
    Scene/Set ObjName[:event]=Field:[Value]
    Scene/Remove ObjName
    
    # SUBTOPICS
    ## view
    Lists the scene objects in the current room, or more detail about a given
    SceneObject in the current room.
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
    valid_commands = ["create","set","remove","view","tag"]
    command=None
    fieldlen = 15
    fieldsep = " |C|||n "
    seplen = 4 # don't take into consideration any formatting.  4 instead of 3 by default is not a typo, idk lol it works
    nFields = 5
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
            s,e = self.rhs[0],self.rhs[-1]
            if s == e and (s == '"' or s == "'"):
                self.rhs=self.rhs[1:-1]
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
            case "set":
                self.Set(self.lhs_sections or [self.lhs], self.rhs_sections or [self.rhs])
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
        headers = ["Priority","dbref","Key","Class","Invisible"]
        return self.fieldsep.join([*map(self.Field,headers)]) + f"|/{self.SepLine()}"
    def ViewTableRow(self,SceneObject,extended=False):
        "Print a table row.  If only one scene object is given, add extra data."
        i = SceneObject.current_during(["invisible"])["invisible"]
        if i != SceneObject.invisible:
            i = f"Currently {i}"
        values=[SceneObject.priority,SceneObject.dbref,SceneObject.name,SceneObject.__class__.__name__,i]
        line=self.fieldsep.join([*map(self.Field,values)])
        if extended:
            line += f"|/{self.SepLine()}|/|CDescription vars:|n"
            for v in SceneObject.LongSceneVars:
                line += f"|/{self.Field(v)}{self.fieldsep}{SceneObject.attributes.get(v)}"
            if len(SceneObject.during):
                for tag,repl in SceneObject.during.items():
                    line += f"|/|CDuring event tag |y{tag}|C:|n"
                    for varn,val in repl.items():
                        line += f"|/{self.Field(varn)}{self.fieldsep}{val}"
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
    
    def Create(self,lhs_sections,rhs): # scene/create name:class:priority=scene_desc
        """     obj = create.create_object(
                typeclass,
                name,
                loc,
                home=loc,
                report_to=caller,
        """
        helpstr="Scene/Create ObjName[:Class][:Priority] [=scene_desc]"
        if lhs_sections == [""]:
            self.caller.msg(helpstr)
            return
        cls = "SceneObject.SceneObject"
        clsbrief="SceneObject"
        prior=100
        objname = lhs_sections[0]
        loc=self.caller.location
        for x in lhs_sections[1:]:
            if x.isnumeric():
                prior = int(x)
            else:
                cls=x
                clsbrief=cls.split(".")[-1]
        obj = create.create_object(cls, objname,loc,home=loc,report_to=self.caller)
        obj.db.priority = prior
        if rhs != None:
            obj.db.scene_desc = rhs
        else:
            obj.db.scene_desc = f"There is a {objname} here, being {objname}y."
        self.caller.msg(f"Created a {objname}({clsbrief}) in {loc}")
        
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
    def Set(self,lhs_sections,rhs_sections):
        helpstr="Scene/Set ObjectName[:EventTag]=Field[:Value]"
        if len(lhs_sections) > 2 or len(rhs_sections) > 2:
            self.caller.msg(f"Too many :sections|/{helpstr}")
            return
        if lhs_sections == [""]:
            self.caller.msg(f"Scene/Set requires an object|/{helpstr}")
            return
        if rhs_sections == [None] or rhs_sections == [""]:
            self.caller.msg(f"Scene/Set requires a field|/{helpstr}")
            return
        objname = lhs_sections[0]
        event = lhs_sections[1] if len(lhs_sections) == 2 else None
        field = rhs_sections[0]
        value = rhs_sections[1] if len(rhs_sections) == 2 else None
        if value != None and len(value)>0:
            if value == "True":
                value=True
            elif value == "False":
                value=False
            elif value.isnumeric():
                value = int(value)
            elif len(value) > 1:
                s,e = value[0],value[-1]
                if s==e and (s=='"' or s=="'"):
                    value = value[1:-1]
        obj = self.SceneList(objname)[0]
        if obj == None:
            self.caller.msg(f"No scene object {objname}")
            return
        if event != None:
            obj.set_during(event,field,value,caller=self.caller)
            return
        # Todo: detect/set type
        if field in obj.SceneVars:
            obj.attributes.add(field,value)
            self.caller.msg(f"Set {objname}/{field}={value}")