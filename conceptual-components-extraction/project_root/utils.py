def getID(u):
    last = u.rfind("#")
    if last<0:
        last = u.rfind("/")
    return u[last+1:]

