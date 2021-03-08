import matplotlib.pyplot as plt
import os

def loadData(file):
    data = {}
    dat = open(file).read().replace("\r\n","\n").strip("\n").split("\n")
    for da in dat[1:]:
        da = da.split("\t")
        da = [d.strip(" ") for d in da]
        spe = da[0]
        data[spe] = [int(d) for d in da[1:4]]
    return(data)

def compareNrtRt(dataNRT,dataRT):
    couRT = {}
    for sp,cnrt in dataNRT.items():
        crt = dataRT.get(sp)
        cr = cnrt[0]-crt[0]
        couRT[sp] = [cnrt[0],cr]
    return(couRT)

def makeSingleOut(couRT,output):
    out = open(output,"w")
    out.write("Species\tBOLD public\tRT count\tComment")
    for sp,cou in couRT.items():
        out.write("\n" + sp + "\t" + str(cou[0]) + "\t" + str(cou[1]) + "\t")
        if cou[0] > 0:
            if cou[0] == cou[1]:
                out.write("All public data originate from rt")
            elif cou[0] < 5 and cou[1] > 0:
                out.write("Less than 5 public barcodes and rt")
            elif cou[0] > 5 and cou[0] - cou[1] < 5:
                out.write("Rt resulted increased the number of public barcodes above 5")
            elif cou[1] * 2 > cou[0]:
                out.write("More than half of the data originating from rt")
    out.close()

def getValsAll(couRT,dataNRT):
    #allSpecs,allSpecswithBp,allSpecswithRT,AllRT,<5RT,RT>5,RT>1/2
    allSp = [0,0,0,0,0,0,0]
    #allBC,allBp,allRT
    allBC = [0,0,0]
    for sp, da in dataNRT.items():
        co = couRT.get(sp,[0,0])
        allSp[0] += 1
        if co[0] > 0:
            allSp[1] += 1
            allBC[1] += co[0]
            if co[1] > 0:
                allSp[2] += 1
                allBC[2] += co[1]
                if co[0] == co[1]:
                    allSp[3] += 1
                elif co[0] < 5 and co[1] > 0:
                    allSp[4] += 1
                elif co[0] and co[0] - co[1] < 5:
                    allSp[5] += 1
                elif co[1] * 2 > co[0]:
                    allSp[6] += 1
        allBC[0] += sum(da)
    return(allSp,allBC)

def makeAllOut(dataNRT,couRT,output):
    allSP,allBC = getValsAll(couRT,dataNRT)

    out = open(output,"w")
    out.write("#Barcodes\t#BC-BOLDpub\tBC-RT\t#Species\t#Spec-BOLDpub\t#RT\t")
    out.write("All public data originate from rt\tLess than 5 public barcodes and rt\tRt resulted increased the number of public barcodes above 5\tMore than half of the data originating from rt")
    out.write("\n" + "\t".join([str(v) for v in allBC]) + "\t")
    out.write("\t".join([str(v) for v in allSP]))
    out.close()

nrt = "NewData/FwVp_Gap.txt"
rt = "NewData/FwVp_Gap_RT.txt"
outsingle = "RT/FwVp_RT_Species.txt"
outall = "RT/FwVp_RT_All.txt"

if not os.path.exists("RT"):
    os.mkdir("RT")

dataNRT = loadData(nrt)
dataRT = loadData(rt)
couRT = compareNrtRt(dataNRT,dataRT)
makeSingleOut(couRT,outsingle)
makeAllOut(dataNRT,couRT,outall)
