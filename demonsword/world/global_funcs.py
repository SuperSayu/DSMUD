from evennia.utils import repeat
from evennia.utils.search import search_objects_by_typeclass

cooldown_ticker = None
def setup_cooldowns():
    global cooldown_ticker
    if cooldown_ticker == None:
        cooldown_ticker = repeat(20,SkillCooldown,False)

def SkillCooldown():
    for char in search_objects_by_typeclass("typeclasses.characters.Character"):
#    for char in Character.objects.All():
        char.Cooldown()
    pass
