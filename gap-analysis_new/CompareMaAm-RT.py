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

def compareNrtRt(dataNRT,dataRT):
    couRT = {}
    for sp,cnrt in dataNRT.items():
        crt = dataRT.get(sp)
        cr = cnrt[0]-crt[0]
        couRT[sp] = [cnrt[0],cr]
    return(couRT)

def makeSingleOut(info,couRT,output):
    out = open(output,"w")
    out.write("Taxonomic Group\tTaxonomic Subgroup\tSpecies\tBOLD public\tRT count\tComment")
    for sp,inf in info.items():
        cou = couRT.get(sp,[0,0])
        out.write("\n" + "\t".join(inf[0:2]) + "\t" + sp)
        out.write("\t" + str(cou[0]) + "\t" + str(cou[1]) + "\t")
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

def makeCat(info):
    large = {}
    sub = {}
    for spe,inf in info.items():
        o = large.get(inf[0],[])
        o.append(spe)
        large[inf[0]] = o
        o = sub.get(inf[1],[])
        if inf[1] != "":
            o.append(spe)
            sub[inf[1]] = o
    return(large,sub)

def getValsCat(dict,couRT,dataNRT):
    catreSp = {}
    catreBC = {}
    for cat,specs in dict.items():
        #allSpecs,allSpecswithBp,allSpecswithRT,AllRT,<5RT,RT>5,RT>1/2
        rS= [0,0,0,0,0,0,0]
        #allBC,allBp,allRT
        rBC = [0,0,0]
        for sp in specs:
            co = couRT.get(sp,[0,0])
            da = dataNRT.get(sp,[0,0,0])
            rS[0] += 1
            if co[0] > 0:
                rS[1] += 1
                rBC[1] += co[0]
                if co[1] > 0:
                    rS[2] += 1
                    rBC[2] += co[1]
                    if co[0] == co[1]:
                        rS[3] += 1
                    elif co[0] < 5 and co[1] > 0:
                        rS[4] += 1
                    elif co[0] and co[0] - co[1] < 5:
                        rS[5] += 1
                    elif co[1] * 2 > co[0]:
                        rS[6] += 1
            rBC[0] += sum(da)
        catreSp[cat] = rS
        catreBC[cat] = rBC
    return(catreSp,catreBC)

def makeCatOut(info,dataNRT,couRT,output):
    large,sub = makeCat(info)
    catreSPL,catreBCL = getValsCat(large,couRT,dataNRT)
    catreSPS,catreBCS = getValsCat(sub,couRT,dataNRT)

    out = open(output,"w")
    out.write("Category\t#Barcodes\t#BC-BOLDpub\tBC-RT\t#Species\t#Spec-BOLDpub\t#RT\t")
    out.write("All public data originate from rt\tLess than 5 public barcodes and rt\tRt resulted increased the number of public barcodes above 5\tMore than half of the data originating from rt")
    for cat,valSP in catreSPL.items():
        valBC = catreBCL.get(cat)
        out.write("\n" + cat + "\t" + "\t".join([str(v) for v in valBC]) + "\t")
        out.write("\t".join([str(v) for v in valSP]))

    for cat,valSP in catreSPS.items():
        valBC = catreBCS.get(cat)
        out.write("\n" + cat + "\t" + "\t".join([str(v) for v in valBC]) + "\t")
        out.write("\t".join([str(v) for v in valSP]))

    out.close()

nrt = "NewData/MaAm_Gap.txt"
rt = "NewData/MaAm_Gap_RT.txt"
outsingle = "RT/MaAm_RT_Species.txt"
outcat = "RT/MaAm_RT_Category.txt"

if not os.path.exists("RT"):
    os.mkdir("RT")

infoNRT,dataNRT = loadData(nrt)
infoRT,dataRT = loadData(rt)
couRT = compareNrtRt(dataNRT,dataRT)
makeSingleOut(infoRT,couRT,outsingle)
makeCatOut(infoRT,dataNRT,couRT,outcat)
