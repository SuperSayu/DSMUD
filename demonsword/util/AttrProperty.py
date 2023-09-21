"""
    Implements the AttributeProperty and UpdateDefaults functions.
    The purpose of this helper is to create "Attribute property" objects.
    These are properties with a per-class default that can be overridden
    by redefining the same variable on child classes with a basic object.
    
    For example,
    class A:
        a = AttributeProperty("key","A-style default value')
        def __init_subclass__(self):
            UpdateDefaults(super())
    class B(A):
        a = "B-style default value"
        
    The result of this is that A.a and B.a are both properties
    that read from and write to the same Evennia attribute,
    but which report different default values when unset.
    This should help uncomplicate inheritance trees
    (though I come from SS13/BYONDcode, so I may be biased)
    
    With multiple inheritence, it is possible for the DefaultUpdate
    mechanism to be disrupted.  Be sure that the base (first) class
    has the properties and init mechanism.
"""
from copy import copy
def AttributeGetter(key,cat=None):
    "Helper returns anonymous member function (?) getting specific evennia attribute"
    return lambda self: self.attributes.get(key,category=cat)
def AttributeSetter(key,cat=None,default=None):
    "Helper returns anonymous member function (?) setting specific evennia attribute"
    return lambda self,value: self.attributes.add(key,value,category=cat)# if value != default else self.attributes.remove(key,category=cat)
def AttributeDeller(key,cat=None):
    "Helper returns anonymous member function (?) deleting specific evennia attribute"
    return lambda self: self.attributes.remove(key,category=cat)

def NAttributeGetter(key,cat=None):
    "Helper returns anonymous member function (?) getting specific evennia non-persistent attribute"
    return lambda self: self.nattributes.get(key,category=cat)
def NAttributeSetter(key,cat=None,default=None):
    "Helper returns anonymous member function (?) setting specific evennia non-persistent attribute"
    return lambda self,value: self.nattributes.add(key,value,category=cat)# if value != default else self.attributes.remove(key,category=cat)
def NAttributeDeller(key,cat=None):
    "Helper returns anonymous member function (?) deleting specific evennia non-persistent attribute"
    return lambda self: self.nattributes.remove(key,category=cat)

class AttrDict:
    owner   = None # owning object
    proper  = None # Property to save/load to
    cached  = None # Already saved data
    def __init__(self,owner,key,data):
        self.cached = data
        self.owner=owner
        self.proper = getattr(owner.__class__,key)
    def __getitem__(self,index):
        return self.cached[index]
    def __setitem__(self,index,value):
        self.cached[index]=value
        setter=self.proper.fset # don't automatically set self
        setter(self.owner,self.cached)

class AttrProperty:
    """
    Property getter intended for Evennia attributes, with default values.
    Pass in a getter and a default in the initialization.  If the getter
    returns None (this can be accepted) or an AttributeError, returns
    the default instead.
    
    This is stored as a class so that the UpdateDefaults script can detect
    changes to the class structure and update the stored default per type.
    """
    getter          = None
    key             = None
    cached          = None
    default         = None
    default_cache   = None
    accept_none     = False
    cache_dicts     = True
    def __init__(self,getter,default,accept_none=False,cache_dicts=True):
        self.getter=getter
        self.default=default
        self.accept_none = accept_none or (default==None)
        self.cache_dicts = cache_dicts
    def __call__(self,other):
        try:
            if self.cached: # dict thing
                return self.cached
            _ = self.getter(self=other)
            if _ == None:
                if self.accept_none:
                    return _
                if isinstance(self.default,dict):
                    if self.default_cache == None:
                        handler = AttrDict(other,self.key,self.default)
                        if self.cache_dicts:
                            self.default_cache = handler
                        return handler
                    return self.default_cache
                return self.default
            if isinstance(_,dict):
                handler = AttrDict(other,self.key,_)
                if self.cache_dicts:
                    self.cached = handler
                return handler
            return _
        except AttributeError:
            return self.default

def AttributeProperty(key,default=None,category=None,fget=None,fset=None,fdel=None):
    """
    Returns a property that calls anonymous member functions
    to translate gets/sets on this property to the same on
    the requested evennia attribute
    """
    getter=fget or AttributeGetter(key,category)
    setter=fset or AttributeSetter(key,category,default)
    deller=fdel or AttributeDeller(key,category)
    return property(AttrProperty(getter,default),setter,deller)
def NAttributeProperty(key,default=None,category=None,fget=None,fset=None,fdel=None):
    """
    Returns a property that calls anonymous member functions
    to translate gets/sets on this property to the same on
    the requested evennia non-persistent attribute
    """
    getter=fget or NAttributeGetter(key,category)
    setter=fset or NAttributeSetter(key,category)
    deller=fdel or NAttributeDeller(key,category)
    return property(AttrProperty(getter,default),setter,deller)
    
def UpdateDefaults(superObject):
    """
    Detects when subclasses overwrite an AttrProperty with any other value,
    and use that value to update the AttrProperty's default value.
    This allows AttrProperty fields to act like normal class members,
    with a per-class default that can be overridden on members,
    while the actual value is transparently stored in Evennia attributes.
    
    This function should be placed in __init_subclass__ on base objects only.
    You do not need to redefine this function on children, as it is the parent's 
    __init_subclass__ that is called.  Note that method is called when
    the class is defined, not when an instance of it is instantiated.
    This should add to startup time but not runtime slowness.
    """
    # We are using the super object (passed in) to compare the current and base classes.
    oldClass, newClass = superObject.__thisclass__, superObject.__self_class__
    for var in newClass.__dict__:
        # only care about variables inherited from old class
        if not var in oldClass.__dict__:
            continue
            
        # only care if the variable WAS a property implemented with the AttrProperty class,
        # and the new variable with the same name is some other value.
        oldVal, newVal = getattr(oldClass,var), getattr(newClass,var)
        if not isinstance(oldVal, property) or not isinstance(oldVal.fget,AttrProperty) or isinstance(newVal, property):
            continue
        
        # We now assume whatever we overwrite the property with is the new default
        new_dp = copy(oldVal.fget)
        new_dp.default = newVal
        setattr(newClass, var,
            property( fget = new_dp, fset = oldVal.fset, fdel=oldVal.fdel, doc=oldVal.__doc__ )
        )
