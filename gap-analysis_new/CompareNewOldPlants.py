import matplotlib.pyplot as plt
import os

def loadData(file):
    data = {}
    info = {}
    dat = open(file).read().replace("\r\n","\n").strip("\n").split("\n")
    for da in dat[1:]:
        da = da.split("\t")
        da = [d.strip(" ") for d in da]
        spe = da[0]
        #pub,pri,gen,rB,mB,rG,mG
        info[spe] = [int(da[8]),da[9]]
        data[spe] = [int(d) for d in da[1:8]]
    return(info,data)

def compareBC(dataO,dataN):
    cha = {}
    for spe,new in dataN.items():
        old = dataO.get(spe,[0,0,0,0,0,0,0])
        if old != new:
            cha[spe] = [new[p]-old[p] for p in range(7)]
    return(cha)

def chanVal(pos1,pos2,val,total,spec):
    if val[pos1] > 0:
        total[pos2] += val[pos1]
        spec[pos2] += 1
    elif val[pos1] < 0:
        total[pos2+1] += val[pos1]
        spec[pos2+1] -= 1
    return(total,spec)

def plotAllChanges(cha,folder):
    total = [0 for x in range(14)]
    spec = [0 for x in range(14)]
    for spe,val in cha.items():
        for x in range(7):
            total,spec = chanVal(x,2*x,val,total,spec)

    print(total)
    print(spec)
    fig = plt.figure()
    ax = plt.subplot(111)

    ax.bar(range(7), [total[x] for x in range(1,14,2)], color='r',width=0.95)
    ax.bar(range(7), [total[x] for x in range(0,13,2)], color='b',width=0.95)

    plt.savefig(folder + "/" + "FwVpAllChanges.svg")
    plt.savefig(folder + "/" + "FwVpAllChanges.png")
    plt.close()

    fig = plt.figure()
    ax = plt.subplot(111)
    ax.bar(range(7), [spec[x] for x in range(1,14,2)], color='r',width=0.95)
    ax.bar(range(7), [spec[x] for x in range(0,13,2)], color='b',width=0.95)
    plt.savefig(folder + "/" + "FwVpSpeChanges.svg")
    plt.savefig(folder + "/" + "FwVpSpeChanges.png")
    plt.close()

def makeDataPie(data):
    numbersb = [0,0,0,0,0]
    numbersg = [0,0,0,0,0]

    for spec,vals in data.items():
        if vals[0] == 0:
            if vals[1] == 0:
                numbersb[0] += 1
            else:
                numbersb[1] += 1
        else:
            if vals[3] > 0:
                if vals[4] > 0:
                    numbersb[4] += 1
                else:
                    numbersb[2] += 1
            else:
                if vals[4] > 0:
                    numbersb[3] += 1
                else:
                    print(spec,vals)

    for spec,vals in data.items():
        if vals[0]+vals[2] == 0:
            if vals[1] == 0:
                numbersg[0] += 1
            else:
                numbersg[1] += 1
        else:
            if vals[3] + vals[5] > 0:
                if vals[4] + vals[6] > 0:
                    numbersg[4] += 1
                else:
                    numbersg[2] += 1
            else:
                if vals[4] + vals[6] > 0:
                    numbersg[3] += 1
                else:
                    print(spec,vals)

    return(numbersb,numbersg)


def makePiePlot(data,output):
    #generate data
    #numbers = [no data, private data, only rbcL,only matK,both]
    numbersb,numbersg = makeDataPie(data)
    print(numbersb)
    print(numbersg)


    labels = ['no barcodes','private barcodes','rbcl','matk','both']
    colors = ['white','grey','cadetblue', 'c', 'darkslategray']

    fig = plt.figure()
    ax1 = plt.subplot(121)
    ax2 = plt.subplot(122)

    sizes = numbersb
    sizes2 = numbersg

    patches, texts = ax1.pie(sizes, colors=colors, shadow=False, startangle=90)
    patches2, texts2 = ax2.pie(sizes2, colors=colors, shadow=False, startangle=90)

    for p in patches:
        p.set_linewidth(1)
        p.set_edgecolor("black")

    for p in patches2:
        p.set_linewidth(1)
        p.set_edgecolor("black")

    ax1.legend(patches, labels, loc="best")
    ax2.legend(patches2, labels, loc="best")

    ax1.set_title("Bold Public")
    ax2.set_title("All Public")

    ax1.axis('equal')
    ax2.axis('equal')
    plt.tight_layout()
    plt.savefig(output + "_marker.pdf")
    plt.savefig(output + "_marker.svg")
    plt.savefig(output + "_marker.png")
    plt.close()


def makeCountryDataMarker(info,data,output):
    # countrydata per #country = no data, private data, only rbcL,only matK,both
    countryb = {}
    countryg = {}

    for spec,inf in info.items():
        vals = data.get(spec,[0,0,0,0,0])
        cts = inf[0]
        nb = countryb.get(cts,[0,0,0,0,0,0])
        ng = countryg.get(cts,[0,0,0,0,0,0])
        nb[5] += 1
        ng[5] += 1
        if vals[0] == 0:
            if vals[1] == 0:
                nb[0] += 1
            else:
                nb[1] += 1
        else:
            if vals[3] > 0:
                if vals[4] > 0:
                    nb[4] += 1
                else:
                    nb[2] += 1
            else:
                if vals[4] > 0:
                    nb[3] += 1
        countryb[cts] = nb

        if vals[0]+vals[2] == 0:
            if vals[1] == 0:
                ng[0] += 1
            else:
                ng[1] += 1
        else:
            if vals[3] + vals[5] > 0:
                if vals[4] + vals[6] > 0:
                    ng[4] += 1
                else:
                    ng[2] += 1
            else:
                if vals[4] + vals[6] > 0:
                    ng[3] += 1
        countryg[cts] = ng

    print(countryg)
    print(countryb)


    out = open(output,"w")
    #no data, private data, only rbcL,only matK,both
    out.write("#Countries\t#Species\t")
    out.write("%PBNoData\t%PBprivat\t%PBrbcl\t%PBmatK\t%PBboth\t")
    out.write("%GNoData\t%Gprivat\t%Grbcl\t%GmatK\t%Gboth")
    for k,vb in countryb.items():
        vg = countryg.get(k)
        out.write("\n" + str(k) + "\t" + str(vb[-1]))
        out.write("\t" + "\t".join([str(v/vb[-1]) for v in vb[:-1]]))
        out.write("\t" + "\t".join([str(v/vg[-1]) for v in vg[:-1]]))
    out.close()


old = "OldData/FwVp_GapOld.txt"
new = "NewData/FwVp_Gap.txt"

if not os.path.exists("plots"):
    os.mkdir("plots")
if not os.path.exists("results"):
    os.mkdir("results")


infoO,dataO = loadData(old)
infoN,dataN = loadData(new)
print(dataO)
print(dataN)
cha = compareBC(dataO,dataN)
plotAllChanges(cha,"plots")
makePiePlot(dataO,"plots/FwVpPieChartsOld")
makePiePlot(dataN,"plots/FwVpPieChartsNew")
makeCountryDataMarker(infoO,dataO,"results/FwVpDataByCountryCountOld.txt")
makeCountryDataMarker(infoO,dataN,"results/FwVpDataByCountryCountNew.txt")
