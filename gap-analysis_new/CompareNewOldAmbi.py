import matplotlib.pyplot as plt
import os

def loadData(file):
    info = {}
    data = {}
    dat = open(file).read().replace("\r\n","\n").strip("\n").split("\n")
    for da in dat[1:]:
        da = da.split("\t")
        da = [d.strip(" ") for d in da]
        spe = da[2]
        info[spe] = [da[0],da[1],da[6]]
        data[spe] = [int(d) for d in da[3:6]]
    return(info,data)

def compareBC(dataO,dataN):
    cha = {}
    for spe,new in dataN.items():
        old = dataO.get(spe,[0,0,0])
        if old != new:
            cha[spe] = [new[0]-old[0],new[1]-old[1],new[2]-old[2]]
    return(cha)

def plotAllChanges(cha,folder,name):
    total = [0,0,0,0,0,0]
    spec = [0,0,0,0,0,0]
    for spe,val in cha.items():
        if val[0] > 0:
            total[0] += val[0]
            spec[0] += 1
        elif val[0] < 0:
            total[1] += val[0]
            spec[1] -= 1
        if val[1] > 0:
            total[2] += val[1]
            spec[2] += 1
        elif val[1] < 0:
            total[3] += val[1]
            spec[3] -= 1
        if val[2] > 0:
            total[4] += val[2]
            spec[4] += 1
        elif val[2] < 0:
            total[5] += val[2]
            spec[5] -= 1

    fig = plt.figure()
    ax = plt.subplot(111)
    ax.bar(range(3), [total[1],total[3],total[5]], color='r',width=0.95)
    ax.bar(range(3), [total[0],total[2],total[4]], color='b',width=0.95)
    plt.savefig(folder + "/" + name + "_allChanges.svg")
    plt.savefig(folder + "/" + name + "_allChanges.png")
    plt.close()

    fig = plt.figure()
    ax = plt.subplot(111)
    ax.bar(range(3), [spec[1],spec[3],spec[5]], color='r',width=0.95)
    ax.bar(range(3), [spec[0],spec[2],spec[4]], color='b',width=0.95)
    plt.savefig(folder + "/" + name + "_speChanges.svg")
    plt.savefig(folder + "/" + name + "_speChanges.png")
    plt.close()

def makeCat(infoN):
    large = {}
    sub = {}
    eco = {}
    for spe,inf in infoN.items():
        if inf[0] == "":
            inf[0] = "no"
        o = large.get(inf[0],[])
        o.append(spe)
        large[inf[0]] = o
        o = sub.get(inf[1],[])
        if inf[1] != "":
            o.append(spe)
            sub[inf[1]] = o
        o = eco.get(inf[2],[])
        o.append(spe)
        eco[inf[2]] = o
    return(large,sub,eco)

def getOvVals(dict,data,lim):
    res = {}
    for type,specs in dict.items():
        vals = [len(specs),0,0,0]
        for sp in specs:
            n = data.get(sp,[0,0,0])
            if n[0] >= lim:
                vals[1] += 1
            elif n[0] + n[1] >= lim:
                vals[2] += 1
            elif sum(n) >= lim:
                vals[3] += 1
        res[type] = vals
    return(res)

def GroupswChanges(info,dataN,dataO,folder1,name,lim):
    large,sub,eco = makeCat(info)

    #pubn,pub+prin,alln
    resLN = getOvVals(large,dataN,lim)
    resLO = getOvVals(large,dataO,lim)
    resSN = getOvVals(sub,dataN,lim)
    resSO = getOvVals(sub,dataO,lim)
    resEN = getOvVals(eco,dataN,lim)
    resEO = getOvVals(eco,dataO,lim)


    out = open(folder1  + "/" + name + "_lim" + str(lim) + ".txt","w")
    out.write("Type\tGroup\tTotal\tPublic\tBold\tAll")
    for gr,da in resLO.items():
        out.write("\n" + "Old" +"\t" + gr + "\t" + "\t".join([str(d) for d in da]))
        out.write("\n" + "New" +"\t" + gr + "\t" + "\t".join([str(d) for d in resLN.get(gr)]))

    for gr,da in resSO.items():
        out.write("\n" + "Old" +"\t" + gr + "\t" + "\t".join([str(d) for d in da]))
        out.write("\n" + "New" +"\t" + gr + "\t" + "\t".join([str(d) for d in resSN.get(gr)]))

    for gr,da in resEO.items():
        out.write("\n" + "Old" +"\t" + gr + "\t" + "\t".join([str(d) for d in da]))
        out.write("\n" + "New" +"\t" + gr + "\t" + "\t".join([str(d) for d in resEN.get(gr)]))

    out.close()




old = "OldData/MaAm_GapOld.txt"
new = "NewData/MaAm_Gap.txt"

if not os.path.exists("plots"):
    os.mkdir("plots")
if not os.path.exists("results"):
    os.mkdir("results")


infoO,dataO = loadData(old)
infoN,dataN = loadData(new)
cha = compareBC(dataO,dataN)
plotAllChanges(cha,"plots","MaAm")
GroupswChanges(infoN,dataN,dataO,"results","MaAm",1)
GroupswChanges(infoN,dataN,dataO,"results","MaAm",5)
