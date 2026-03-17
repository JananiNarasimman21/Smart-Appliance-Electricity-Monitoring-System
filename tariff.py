def slab_tariff(units): 
    if units <= 100:
        return units * 3
    elif units <= 200:
        return (100 * 3) + ((units - 100) * 5)
    elif units <= 500:
        return (100 * 3) + (100 * 5) + ((units - 200) * 7)
    else:
        return (100 * 3) + (100 * 5) + (300 * 7) + ((units - 500) * 9)