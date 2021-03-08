import matplotlib.pyplot as plt
import os

def loadData(file,type):
    info = {}
    data = {}
    dat = open(file).read().replace("\r\n","\n").strip("\n").split("\n")
    for da in dat[1:]:
        da = da.split("\t")
        da = [d.strip(" ") for d in da]
        spe = da[2]
        info[spe] = [da[0],da[1]]
        if type == "old":
            data[spe] = int(da[3])
        elif type == "new":
            data[spe] = [int(d) for d in da[3:6]]
    return(info,data)

def makeCat(infoN):
    large = {}
    sub = {}
    for spe,inf in infoN.items():
        o = large.get(inf[0],[])
        o.append(spe)
        large[inf[0]] = o
        o = sub.get(inf[1],[])
        if inf[1] != "":
            o.append(spe)
            sub[inf[1]] = o
    return(large,sub)

def getOvVals(dict,data,lim):
    res = {}
    for type,specs in dict.items():
        vals = [len(specs),0,0,0]
        for sp in specs:
            n = data.get(sp,[0,0,0])
            if type == "Brachiopoda":
                print(n,vals)
            if n[0] >= lim:
                vals[1] += 1
            elif n[0] + n[1] >= lim:
                vals[2] += 1
            elif sum(n) >= lim:
                vals[3] += 1
        res[type] = vals
    return(res)

def getOld(group,data,lim):
    resO = {}
    for gr,specs in group.items():
        wd = 0
        tot = len(specs)
        for sp in specs:
            v = data.get(sp,0)
            if v >= lim:
                wd += 1
        resO[gr] = [wd,tot]
    return(resO)




def GroupswChanges(info,dataN,dataO,folder1,name,lim):
    large,sub = makeCat(info)
    #pubn,pub+prin,alln
    resLO = getOld(large,dataO,lim)
    resL = getOvVals(large,dataN,lim)
    resSO = getOld(sub,dataO,lim)
    resS = getOvVals(sub,dataN,lim)


    print(resL)
    print(resS)
    print(resLO)
    print(resSO)

    out = open(folder1  + "/" + name + "_lim" + str(lim) + ".txt","w")
    out.write("Group\tTotal\tPublic\tBold\tAll\tAllOld")
    for gr,da in resL.items():
        o = resLO.get(gr)
        out.write("\n" + gr + "\t" + "\t".join([str(d) for d in da]) + "\t" + str(o[0]))
    for gr,da in resS.items():
        o = resSO.get(gr)
        out.write("\n" + gr + "\t" + "\t".join([str(d) for d in da]) + "\t" + str(o[0]))
    out.close()




old = "OldData/MaEr_GapOld.txt"
new = "NewData/MaEr_Gap.txt"

if not os.path.exists("plots"):
    os.mkdir("plots")
if not os.path.exists("results"):
    os.mkdir("results")


infoO,dataO = loadData(old,"old")
infoN,dataN = loadData(new,"new")
GroupswChanges(infoN,dataN,dataO,"results","MaEr_DataGroups",1)
#GroupswChanges(infoN,dataN,dataO,"results","MaEr_DataGroups",5)
