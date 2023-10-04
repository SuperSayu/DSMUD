from evennia.prototypes import spawner as ev_spawner

def spawn(*prototypes,**kwargs):
    #objs=spawner.spawn(*prototypes, caller=caller, **kwargs)
    if prototypes == None or prototypes == 0 or prototypes == "":
        return []
    print(f"{prototypes}>{prototypes[0]}({type(prototypes[0])})")
    if isinstance(prototypes,str):
        objs = ev_spawner.spawn([prototypes],**kwargs)
    elif isinstance(prototypes,tuple):
        objs = ev_spawner.spawn(*(prototypes[0]),**kwargs)
    elif isinstance(prototypes,list):
        objs = ev_spawner.spawn(*prototypes,**kwargs)
    else:
        raise ValueError(f"util.spawn: prototypes is {prototypes}({type(prototypes)})")
    if not kwargs.get("only_validate"):
        caller=kwargs.get("caller")
        spawner=kwargs.get("spawner")
        l = kwargs.get("location") 
        for o in objs:
            if l != None and o.location == None:
                o.location = l
            if spawner != None:
                spawner.spawn_success(o,caller)
                o.at_spawned_by(spawner,caller)
            o.at_post_spawn(caller,spawner)
    return objs
