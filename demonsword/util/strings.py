def fract(f):
    if not isinstance(f,float|int|str):
        return f
    f = float(f)
    n = int(f)
    if f == n:
        return n
    f -= n
    simple={1:"⅞",7/8:"¾",3/4:"⅝",5/8:"½",1/2:"⅜",3/8:"¼",1/4:"⅛",1/8:""}
    while len(simple):
        (i,s) = simple.popitem()
        if f < i:
            return f"{n}{s}"
    return "?"
