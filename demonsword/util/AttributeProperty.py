"""

    Sub properties access an index in a dict or array
    as though that index was a separate variable.
    This is used with Attribute Properties, which
    actually expose SaverDict/SaverArray structures
    that automatically save when altered.
    
    If you are working with nested trees, you should
    only expose one layer at a time, so that defaults
    can work sanely.
"""
from copy import copy

class AttributeProperty:
    """
    AttributeProperty variant intended for all of the specific hoops I need them to jump through.
    This is meant to be overridden such that the attribute handler need not be on the same object,
    the key need not be the field name, and indeed the key may be set by the object.

    This is mostly so that I can have data handler objects which contain a packed data object
    in a predictable way, which SubProperties will index out of, eg
    SkillObject.data = AttributeProperty(...,
        _attr_get_source = lambda _,instance: instance.parent,
        _get_key = lambda _,instance: instance.skillName)
    SkillObject.level = SubProperty() # automatically maps to the value at self.data["level"]
    """
    # These defaults are from AttributeProperty:
    _category = None
    _strattr = False
    _lockstring = ""
    _autocreate = True
    
    # Field name: Automatically set to variable member name in parent object
    _field_name = None # This will be set to the name of the field    
    def __set_name__(self, cls, name):
        """
        Called when descriptor is first assigned to the class. It is called with
        the name of the field.
        """
        self._field_name = name

    # this is a helper because I'm using lambdas
    def _raise(self,ex):
        raise ex
    
    # Attribute source: Should connect to an AttributeHandler on some Evennia object.
    _attr_get_source = lambda _,parent: parent.attributes
    
    def attributes(self,parent):
        return self._attr_get_source(parent)
    
    # Key management: in the default case this is the field name of the property.
    # In any case it is the attribute we are designed to fetch.
    _key = None    
    _key_get = None # lambda self, parent 
    _key_default = lambda self,parent: self._field_name
    def key(self,parent):
        if callable(self._key_get):
            return self._key_get(parent)
        if callable(self._key):
            return self._key(parent)
        if self._key != None:
            return self._key
        if callable(self._key_default):
            return self._key_default(parent)
        if self._key_default != None:
            return self._key_default
        raise ValueError(f"{parent}/{self._field_name}: No explicit and no default key set")
    
    # Data management: Should get/set/del the resulting data from the attribute source
    _data_get = lambda self,parent,attributes,key,default: attributes.get(
                    key=key,
                    default=default,
                    category=self._category_get(parent,attributes,key),
                    strattr=self._strattr,
                    raise_exception=self._autocreate)
    _data_set = lambda self,parent,attributes,key,data: attributes.add(
                key,
                data,
                category=self._category_get(parent,attributes,key),
                lockstring=self._lockstring,
                strattr=self._strattr)
    _data_del = lambda self,parent,attributes,key: attributes.remove(key=key, category=self._category_get(parent,attributes,key))

    _data_validate = lambda self,parent,attributes,key,data,setting: True # setting: true if in set, false if in get
    _data_get_invalid = lambda self,parent,attributes,key,data: self._raise(ValueError(f"{parent}/{key}: data get invalid: '{data}'"))
    _data_set_invalid = lambda self,parent,attributes,key,data: self._raise(ValueError(f"{parent}/{key}: data set invalid: '{data}'"))
    _data_default = None # default value or lambda self,parent,attributes,key
    _data_at_get = lambda self,parent,attributes,key,data: data
    _data_at_set = lambda self,parent,attributes,key,data: data
    _category_get = lambda self,parent,attributes,key: self._category
    
    def _get_default(self,parent,attributes,key):
        if callable(self._data_default):
            return self._data_default(parent,attributes,key)
        return self._data_default
    def set_default(self,data):
        self._data_default = data

    def __get__(self, parent, owner):
        if parent == None:
            return self # This allows us to get the instance of AttributeProperty, for setting/calling stuff
            
        key = self.key(parent)
        attr = self.attributes(parent)
        if not attr:
            return None
        default = self._get_default(parent,attr,key)
        try:
            data = self._data_get(parent,attr,key,default)
            if callable(self._data_validate) and not self._data_validate(parent,attr,key,data,False):
                if callable(self._data_get_invalid):
                    return self._data_get_invalid(parent,attr,key,data)
                return default
            if callable(self._data_at_get):
                data = self._data_at_get(parent,attr,key,data)
            return data
        
        except AttributeError:
            if self._autocreate:
                data = default
                if callable(self._data_at_get):
                    data = self._data_at_get(parent,attr,key,data)
                save_data=data
                if callable(self._data_at_set):
                    save_data = self._data_at_set(parent,attr,key,data)
                if save_data == None:
                    return save_data
                # attribute didn't exist and autocreate is set
                self.__set__(parent, save_data)
                data = self._data_get(parent,attr,key,default)
                if callable(self._data_at_get):
                    data = self._data_at_get(parent,attr,key,data)
                return data
            else:
                raise
    def __set__(self, instance, value):
        """
        Called when assigning to the property (and when auto-creating an Attribute).

        """
        key = self.key(instance)
        attrs = self.attributes(instance)
        if callable(self._data_validate) and not self._data_validate(instance,attrs,key,value,True):
            if not callable(self._data_set_invalid) or (value := self._data_set_invalid(instance,attrs,key,value)) == None:
                raise ValueError(f"{instance}/{key}: data set invalid: '{value}'")
        if callable(self._data_at_set):
            value = self._data_at_set(instance,attrs,key,value)
            
        self._data_set(instance,attrs,key,value)        

    def __delete__(self, instance):
        """
        Called when running `del` on the property. Will remove/clear the Attribute. Note that
        the Attribute will be recreated next retrieval unless the AttributeProperty is also
        removed in code!

        """
        key = self.key(instance)
        attrs = self.attributes(instance)

        self._data_del(instance,attrs,key)


    def __init__(self, default=None, key=None,**kwargs):
        """
        Keyword Args:
            key (str or callable(AP,Instance)): get the key string given the current instance
            default (any): A default value if the attr is not set. If a callable, this will be
                run as default(AttributeProperty, ObjectInstance, AttributeHandler, AttributeKey)
            category (str): The attribute's category. If unset, use class default.
            strattr (bool): If set, this Attribute *must* be a simple string, and will be
                stored more efficiently.
            lockstring (str): This is not itself useful with the property, but only if
                using the full AttributeHandler.get(accessing_obj=...) to access the
                Attribute.
            autocreate (bool): True by default; this means Evennia makes sure to create a new
                copy of the Attribute (with the default value) whenever a new object with this
                property is created. If `False`, no Attribute will be created until the property
                is explicitly assigned a value. This makes it more efficient while it retains
                its default (there's no db access).

        """
        if key != None:
            self._key = key
        if default != None:
            self._data_default = default
        overridable = [
            "category","strattr","lockstring","autocreate",
            "attr_get_source","key_get",
            "data_validate","data_get_invalid","data_set_invalid","data_at_set","data_at_get"]
        for kw,val in kwargs.items():
            if kw in overridable:
                setattr(self,f"_{kw}",val)

class NAttributeProperty(AttributeProperty):
    _attr_get_source = lambda _,instance: instance.nattributes
class RemoteAttributeProperty(AttributeProperty):
    _attr_get_source = lambda _,instance: instance.parent.attributes
class RemoteNAttributeProperty(RemoteAttributeProperty):
    _attr_get_source = lambda _,instance: instance.parent.nattributes

class SubProperty:
    """
        A SubProperty is a member descriptor that uses
        a set of accessor and handler functions
        to point transparently to a sub-element of another
        data structure.
        
        By default, this works on parentObject.data[self.key] 
    """
    # We need to support the instance telling us what our key is
    # in order to support things like stat classes etc
    _get_key = None
    _default_key = None # callable(self,instance) or constant.  If not specified at class level, set to _field_name.
    _field_name = None # this WILL be set by set_name, even if default_key is not
    
    # data is parent object structure
    _data_exists = None # _de(sP, inst) => bool, if not present, skip check
    _data_access = None # _da(sP, inst) => data
    _data_validate = None # _dv(sP, inst) => true or raise
    _data_missing = None # _dm(sP, inst) => data or raise, called if data null
    # res is result/return value
    _res_exists = None # _re(sP, inst), if not present, skip check
    _res_get = None # return _rg(sP, inst, data) unless null and default
    _res_set = None # _rs(sP, inst, data, value)
    _res_del = None # _rd(sP, inst, data)
    _res_get_default    = None # _rgd(sP, inst, data)
    _res_set_missing    = None # _rsm(sP, inst, data, value), only if exists func exists and returns false
    
    _res_at_get = lambda sP,inst,data,result: result
    _res_at_set = lambda sP,inst,data,value: value
    
    # name to disambiguate errors
    get_name = lambda self,instance: f"{instance}[{self.key(instance)}]"
    
    _default_data = lambda _,instance: instance.data
    _default_get = lambda self,instance,data: data[self.key(instance)]
    def _default_set(self, instance, data, value):
        data[self.key(instance)]=value
    def _default_del(self,instance,data):
        del data[self.key(instance)]
    
    def __init__(self, **kwargs):
        valid_kwargs = [
            "_data_exists","_data_access","_data_validate","_data_missing",
            "_res_exists","_res_get","_res_set","_res_del","_res_get_default","_res_set_missing","_default",
            "_default_key","_get_key","get_name"
        ]
        for kw,val in kwargs.items():
            if kw in valid_kwargs:
                setattr(self,kw,val)
            if kw == "key":
                setattr(self,"_get_key",val)
        
    def __set_name__(self,cls,name):
        self._field_name = name
        if self._default_key == None:
            self._default_key = name
    
    def key(self,instance):
        if callable(self._get_key):
            return self._get_key(instance)
        if isinstance(self._get_key,str) and len(self._get_key) > 0:
            return self._get_key
        if callable(self._default_key):
            return self._default_key(instance)
        return self._default_key
    
    # I am setting this up so that my script can use this equivalently to an attributeproperty
    @property
    def _default(self):
        return self._res_get_default
    @_default.setter
    def _default(self,value):
        self._res_get_default = value
    
    def get_default(self,instance, data):
        if callable(self._res_get_default):
            return self._res_get_default(instance,data)
        return self._res_get_default
    def set_default(self,data):
        self._res_get_default = data
    def _data(self,instance):
        """
            Gets the parent data structure, or throw on error.
            This will only return null if _data_validate() exists
            and accepts null responses.
            
            The _get tree will all receive the result of this function
            as a parameter.
        """
        
        # If data_exists callable is specified, run check first:
        if callable(self._data_exists) and not self.data_exists(instance):
            if callable(self._data_missing):
                return self._data_missing(instance)
            raise ValueError(f"SubProperty {self.get_name(instance)}: No data")
        
        # Get data (parent structure):
        data = self._data_access(instance) if self._data_access else self._default_data(instance)
        
        # Handle missing or invalid data (otherwise, this will likely error later)
        if callable(self._data_validate):
            if not self._data_validate(instance,data):
                if callable(self._data_missing):
                    return self._data_missing(instance)
                raise ValueError(f"SubProperty {self.get_name(instance)}: Invalid data")
        elif data == None:
            if callable(self._data_missing):
                return self._data_missing(instance)
            raise ValueError(f"SubProperty {self.get_name(instance)}: No data")
        
        # Otherwise, return
        return data
    
    def __get__(self, instance, cls):
        data = self._data(instance)
    
        # Assume at this point data is a valid structure, whatever that means
        if callable(self._res_exists) and not self._res_exists(instance,data):
            if self._res_get_default != None:
                return self.get_default(instance,data)
            raise ValueError(f"SubProperty {self.get_name(instance)}: Result missing")
        
        # get result
        value = self._res_get(instance,data) if callable(self._res_get) else self._default_get(instance,data)
        
        if value == None and self._res_get_default != None:
            value = self.get_default(instance,data)
            if value != None:
                self.__set__(instance,value)
        
        return value
        
    def __set__(self,instance,value):
        data = self._data(instance)
        
        if callable(self._res_exists) and not self._res_exists(instance,data) and callable(self._res_set_missing):
            self._res_set_missing(instance,data,value)
            return
        
        if callable(self._res_set):
            self._res_set(instance,data,value)
        else:
            self._default_set(instance,data,value)
        
    def __delete__(self,instance):
        data = self._data(instance)
        
        if callable(self._res_exists) and not self._res_exists(instance,data):
            return
        
        if callable(self._res_del):
            self._res_del(instance,data)
        else:
            self._default_del(instance,data)

class RemoteProperty(SubProperty):
    _default_data = lambda _,instance: instance.parent.data
    _default_key = lambda _,instance: instance.key


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
    keeper = lambda val: isinstance(val,AttributeProperty) or isinstance(val,SubProperty)
    for var in newClass.__dict__:
        # only care about variables inherited from old class
        if not var in oldClass.__dict__:
            continue
            
        # only care if the variable WAS a property implemented as AttributeProperty or SubProperty,
        # and the new variable with the same name is some other value.
        oldVal, newVal = getattr(oldClass,var), getattr(newClass,var)
        if not keeper(oldVal) or keeper(newVal):
            continue
        
        # We now assume whatever we overwrite the property with is the new default
        new_ap = copy(oldVal)
        new_ap.set_default(newVal)
        setattr(newClass, var, new_ap)
