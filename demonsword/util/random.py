from random import randint,random,choice

def randfloat(min,max,grain=0.001):
    """
    Random bounded floating point number with maximum precision
    (not counting floating point errors)
    """
    return ((min + random() * (max-min)) // grain) * grain

def madlib(text,*args,**kwargs):
    if args != None:
        args = [*args]
        for i in range(0, len(args)):
            if isinstance(args[i],list):
                args[i] = choice(args[i])
    if kwargs != None:
        for k,v in kwargs.items():
            if isinstance(v,list):
                kwargs[k] = choice(v)
    return text.format(*tuple(args),**kwargs)

def prob(prob_num):
    """
        Returns true (prob_num / 100)% of the time
    """
    return (randint(0,9999)/100.) < prob_num

def show_roll(caller,skillName,challenge=0,*,d4=0,d6=0,d8=0,d10=0,d12=0,d16=0,d20=0,d80=1, brute=0,slip=0):
    
    def d(*args): # Inline pretty-print function for dice
        _ = []
        for a in args:
            [n,s] = a
            if n > 0:
                _.append(f"{n}{s}")
        return ", ".join(_)
    # I am not happy with all of these unicode symbols for various dices.  8 and below are fine, but 8+ are too similar.
    dice = d([d80,'*'],[d4,'\u25b3'],[d6,'\u25a2'],[brute,'\u25A7'],[d8,'\u25ca'],[d10,'\u25c8'],[d12,'\u25cc'],[d16,'\u25cb'],[d20,'\u25ce'],[slip,'slip'])
    
    r = roll(d4=d4,d6=d6,d8=d8,d10=d10,d12=d12,d16=d16,d20=d20,d80=d80,brute=brute,slip=slip)
    tier = (r - 1)//2
    c = f" vs CR {challenge}: {r-challenge}" if challenge>0 else ""
    t = f" (Tier {tier})"
    caller.msg(f"|gSkill check|n for |w{skillName}|n ({dice}): {r}|g{t}|n{c}")
    return r
    
def roll(*,d4=0,d6=0,d8=0,d10=0,d12=0,d16=0,d20=0,d80=1,brute=0,slip=0):
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
    while d80 > 0:
        d80 -= 1
        result += randint(1,80)//4
    while brute > 0: # Brute dice: d6 where zeroes count as -1, so 3/6 -1, 3/6 +1, average 0.  This is a penalty for having stats above your skills.
        brute -= 1
        temp = randint(1,6) // 4
        if temp > 0:
            result += temp
        else:
            result -= 1
    while slip > 0: # Slip dice: d10 where zeroes count as -1, so 3/10 -1, 4/10 +1, 3/10 +2 average 0.7
        slip -= 1
        temp = randint(1,10) // 4
        if temp > 0:
            result += temp
        else:
            result -= 1
    return result