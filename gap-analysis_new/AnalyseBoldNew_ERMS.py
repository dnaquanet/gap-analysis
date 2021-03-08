import os

#load Species list and Synonyms from Table
def loadOldGap(OldGap):
    info = {}
    total = {}
    data = open(OldGap).read().replace("\r\n","\n").strip("\n").split("\n")
    for da in data[1:]:
        da = da.split("\t")
        da = [d.strip(" ") for d in da]
        info[da[2]] = [da[0],da[1]]
        total[da[2]] = int(da[3])
    return(info,total)

#Load single Progress Report
def loadSingleProg(data,info,proData,Kingdom):
    for da in data:
        da = da.strip(" ").split("\t")
        if len(da) > 6:
            if da[2] == "Species" and da[1] == Kingdom:
                if da[0] in info.keys():
                    spe = da[0]
                    c = 0
                    if da[7] != "":
                        c += int(da[7])
                    if da[8] != "":
                        c += int(da[8])
                    proData[spe] = c
    return(proData)


#Load Progress Report
def loadProgress(ProgFolder,info,Kingdom):
    files = os.listdir(ProgFolder)
    proData = {}
    for f in files:
        data = open(ProgFolder + "/" + f).read().split("\n")
        proData = loadSingleProg(data,info,proData,Kingdom)
    return(proData)

def updateBpData(bpdata,da,rtTerms,rtnew,rtcount):
    da = da.split("\t")
    sp = da[0]
    old = bpdata.get(sp,[0,0,0])
    #public,genbank,rt
    if da[1] == "y":
        old[1] += 1
    elif da[2] != "":
        rt = da[2]
        if rt.count("(") > 0:
            rt = rt[0:rt.find("(")] + rt[rt.find(")")+1:]
        rt = rt.strip(" ").lower()
        if rt in rtTerms:
            old[2] += 1
            c = rtcount.get(rt,0)
            c += 1
            rtcount[rt] = c
        else:
            old[0] += 1
            rtnew.append(rt)
            rtnew = list(set(rtnew))
    else:
        old[0] += 1
    bpdata[sp] = old
    return(bpdata,rtnew,rtcount)

#Load data from ApiBOLD
def loadBoldpub(BoldDaset,info,rtTerms):
    files = os.listdir(BoldDaset)
    bpdata = {}
    rtnew = []
    rtcount = {}
    for f in files:
        data = open(BoldDaset + "/" + f).read().replace("\r\n","\n").split("\n")
        if len(data) > 1:
            data = data[1:]
            for da in data:
                bpdata,rtnew,rtcount = updateBpData(bpdata,da,rtTerms,rtnew,rtcount)
    return(bpdata,rtnew,rtcount)

#calculate public, private, genbank
def calcPPG(pro,bp,rt):
    #pro = all data
    #bp: public,genbank,rt
    #rt: True = calculate without RT; False: RT = public
    pu = bp[0]
    if rt == False:
        pu += bp[2]
    gb = bp[1]
    pr = max(0,pro - sum(bp))
    return([pu,pr,gb])

#Calculate overlap w/wo RT => new RT tacks? => make overview RT tacks/counts
def makeOutputGap(info,proData,bpData,outputGap,outputRT):
    outGap = open(outputGap,"w")
    outRT = open(outputRT,"w")

    outGap.write("Taxonomic group\tTaxonomic subgroup\tSpecies\tPublic\tPrivate\tGenBank")
    outRT.write("Taxonomic group\tTaxonomic subgroup\tSpecies\tPublic\tPrivate\tGenBank")

    specs = sorted(list(info.keys()))
    for sp in specs:
        inf = info.get(sp)
        outGap.write("\n{}\t{}\t{}\t".format(inf[0],inf[1],sp))
        outRT.write("\n{}\t{}\t{}\t".format(inf[0],inf[1],sp))

        ppg = calcPPG(proData.get(sp,0),bpData.get(sp,[0,0,0]),False)
        ppgRT = calcPPG(proData.get(sp,0),bpData.get(sp,[0,0,0]),True)
        outGap.write("\t".join([str(v) for v in ppg]))
        outRT.write("\t".join([str(v) for v in ppgRT]))

    outGap.close()
    outRT.close()

def makeOutputRT(outputRTT,rtcount):
    out = open(outputRTT, "w")
    out.write("Term\tCount")
    for rt in sorted(list(rtcount.keys())):
        c = rtcount.get(rt,0)
        if c != 0:
            out.write("\n" + rt + "\t" + str(c))
    out.close()


OldGap = "OldData/MaEr_GapOld.txt"
ProgFolder = "progressReports"
Kingdom = "Animals"
BoldDaset = "rawdata/MaEr"

outputGap = "NewData/MaEr_Gap.txt"
outputRT = "NewData/MaEr_Gap_RT.txt"
outputRTT = "RT/MaEr_RT_Overview.txt"

if not os.path.exists("NewData"):
    os.mkdir("NewData")

if not os.path.exists("RT"):
    os.mkdir("RT")

#Take tacks for RT
rtTerms = ["bin rep tree identification","bold identification engine","molecular using","bold id engine","bold id engine, november 2012","bold:aaa9475","bold:aab1628","bold:acf5706","bold:aaa9710","tree based identification june 2016","barcoding/bold","barcode","dna barcode 100%","bold-id engine","bold engine","bold id-engine","bold id engine manual","molecular data","tree based identification","tree-based identification","genbank blast","bold id engine","molecular coi barcode","molecular co1 barcode","bin taxonomy match","dna barcoding","dna barcode","bin match","bold database","dna","its2 and coi barcoding region","bold barcode library","by its2","dna sequence analysis","tree base identification","bold id_engine","bold id engine / taxonomy match","molecular coi","bold","identifikation ber sequenz, auftrennung larval nicht mglich","identifikation ber sequenz","dna-barcoding","dna sequence","coi blast","revers","bin taxonomy match |tree based identification","identifikation ber sequenz, limnius volckmari bildet zwergformen aus, die mit l. opacus verwechselt werden knnen","bold id","nj tree","revers bestimmt","bin taxonomy match below phylum","bold id engine manual below phylum","identifikation ueber sequenz","dna barcode match","dna barcode 99.54%","bin taxonomy match |tree based identification (nov 2018)","coi barcode",
"molecular approach","dna barcode 99.69% match","by dna sequence","dna barcode blast","dna barcode 100% match","bold id engine and genbank","bin taxonomy match and specimen image","molecular identification","molecular: coi","barcoding"]

syns = {}

info,total = loadOldGap(OldGap)
proData = loadProgress(ProgFolder,info,Kingdom)
bpData,rtnew,rtcount = loadBoldpub(BoldDaset,info,rtTerms)
makeOutputGap(info,proData,bpData,outputGap,outputRT)
makeOutputRT(outputRTT,rtcount)
