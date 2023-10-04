from evennia.prototypes import spawner

def spawn(*prototypes, caller=None, **kwargs):
    objs=spawner.spawn(*prototypes, caller=caller, **kwargs)
    if kwargs.get("only_validate"):
        return objs
    for o in objs:
        o.at_post_spawn(caller)
    return objs