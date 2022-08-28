class userdata:
    userid: str
    mode: str
    
datalist = []
def adddata(id,mod):
    use = userdata()
    use.userid = id
    use.mode = mod
    datalist.append(use)
    return use

def getdata(id):
    for ele in datalist:
        if ele.userid == id:
            return ele.mode
    adddata(id,"D")
    return 'D'

def swap(id):
    temp = getdata(id)
    for ele in datalist:
        if ele.userid == id:
            break
    if temp == "V":
        ele.mode = "D"
        return "D"
    else:
        ele.mode = "V"
        return "V"

