from random import randint


def show_roll(caller,skillName,challenge=0,d4=0,d6=0,d8=0,d10=0,d12=0,d16=0,d20=0, slip=0):
    
    def d(*args): # Inline pretty-print function for dice
        _ = []
        for a in args:
            [n,s] = a
            if n > 0:
                _.append(f"{n}{s}")
        return ", ".join(_)
    # I am not happy with all of these unicode symbols for various dices.  8 and below are fine, but 8+ are too similar.
    dice = d([d4,'\u25b3'],[d6,'25a2'],[d8,'\u25ca'],[d10,'\u25c8'],[d12,'\u25cc'],[d16,'\u25cb'],[d20,'\u25ce'],[slip,'slip'])
    
    r = roll(d4,d6,d8,d10,d12,d16,d20,slip)
    
    c = f" vs CR{challenge}: {r-c}" if challenge>0 else ""
    
    caller.msg(f"Skill check for {skillName} ({dice}): {r}{c}")
    
    return r
    
def roll(d4=0,d6=0,d8=0,d10=0,d12=0,d16=0,d20=0, slip=0):
    result = 0
    while d4 > 0:
        d4 -= 1
        result += randint(1,4)//4
    while d6 > 0:
        d6 -= 1
        result += randint(1,6)//4
    while d8 > 0:
        d8 -= 1
        result += randint(1,8)//4
    while d10 > 0:
        d10 -= 1
        result += randint(1,10)//4
    while d12 > 0:
        d12 -= 1
        result += randint(1,12)//4
    while d16 > 0:
        d16 -= 1
        result += randint(1,16)//4
    while d20 > 0:
        d20 -= 1
        result += randint(1,20)//4
    
    while slip > 0: # Slip dice: zeroes count as -1, so 3/10 -1, 4/10 +1, 3/10 +2
        slip -= 1
        temp = randint(1,10) // 4
        if temp > 0:
            result += temp
        else:
            result -= 1
    return result