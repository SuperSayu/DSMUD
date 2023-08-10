from random import randint
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