import os

#load Species list and Synonyms from Table
def loadOldGap(OldGap):
    info = {}
    ppgm = {}
    data = open(OldGap).read().replace("\r\n","\n").strip("\n").split("\n")
    for da in data[1:]:
        da = da.split("\t")
        da = [d.strip(" ") for d in da]
        info[da[0]] = [str(da[8]),da[9]]
        ppgm[da[0]] = [int(d) for d in da[1:8]]
    return(info,ppgm)

#Load single Progress Report
def loadSingleProg(data,info,proData,Kingdom):
    for da in data:
        da = da.strip(" ").split("\t")
        if len(da) > 6:
            if da[2] == "Species" and da[1] == Kingdom:
                add = False
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
    old = bpdata.get(da[0],[0,0,0,0,0,0,0,0,0])
    rbcl = False
    matK = False
    #public,genbank,rt,rbcl-pu,matk-pu,rbcl-gb,matk-gb,rbcl-rt,matK-rt
    #test which marker was sequenced
    marker = da[3].split(";")
    if "rbcL" in marker or "rbcLa" in marker:
        rbcl = True
    if "matK" in marker:
        matK = True
    if da[1] == "y":
        old[1] += 1
        if rbcl == True:
            old[5] += 1
        if matK == True:
            old[6] += 1

    elif da[2] != "":
        rt = da[2]
        if rt.count("(") > 0:
            rt = rt[0:rt.find("(")] + rt[rt.find(")")+1:]
        rt = rt.strip(" ").lower()
        if rt in rtTerms:
            old[2] += 1
            if rbcl == True:
                old[7] += 1
            if matK == True:
                old[8] += 1
            c = rtcount.get(rt,0)
            c += 1
            rtcount[rt] = c
        else:
            old[0] += 1
            if rbcl == True:
                old[3] += 1
            if matK == True:
                old[4] += 1
            rtnew.append(rt)
            rtnew = list(set(rtnew))
    else:
        old[0] += 1
        if rbcl == True:
            old[3] += 1
        if matK == True:
            old[4] += 1
    bpdata[da[0]] = old
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
def calcPPGM(pro,bp,rt):
    #pro = all data
    #bp: public,genbank,rt,pu-rbcl,pu-matk,gb-rbcl,gb-matk,rt-rbcl,rt-matk
    #rt: True = calculate without RT; False: RT = public
    pu = bp[0]
    pur = bp[3]
    pum = bp[4]
    if rt == False:
        pu += bp[2]
        pur += bp[7]
        pum += bp[8]
    gb = bp[1]
    pr = pro - sum(bp[0:3])
    if pr < 0:
        pr = 0
    return([pu,pr,gb,pur,pum,bp[5],bp[6]])

#Calculate overlap w/wo RT => new RT tacks? => make overview RT tacks/counts
def makeOutputGap(info,proData,bpData,outputGap,outputRT):
    outGap = open(outputGap,"w")
    outRT = open(outputRT,"w")

    outGap.write("Species\tBOLD public\tBOLD private\tGenBank\tBOLD public rbcL\tBOLD public matK\tGenBank rbcL\tGenBank matK\tNumber of Countries\tCountries")
    outRT.write("Species\tBOLD public\tBOLD private\tGenBank\tBOLD public rbcL\tBOLD public matK\tGenBank rbcL\tGenBank matK\tNumber of Countries\tCountries")

    specs = sorted(list(info.keys()))
    for sp in specs:
        inf = info.get(sp)
        outGap.write("\n" + sp + "\t")
        outRT.write("\n" + sp + "\t")

        ppgm = calcPPGM(proData.get(sp,0),bpData.get(sp,[0,0,0,0,0,0,0,0,0,0]),False)
        ppgmRT = calcPPGM(proData.get(sp,0),bpData.get(sp,[0,0,0,0,0,0,0,0,0,0]),True)

        outGap.write("\t".join([str(v) for v in ppgm]))
        outRT.write("\t".join([str(v) for v in ppgmRT]))

        outGap.write("\t{}\t{}".format(str(inf[0]),inf[1]))
        outRT.write("\t{}\t{}".format(str(inf[0]),inf[1]))

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


OldGap = "OldData/FwVp_GapOld.txt"
ProgFolder = "progressReports"
Kingdom = "Plants"
BoldDaset = "rawdata/FwVp"

outputGap = "NewData/FwVp_Gap.txt"
outputRT = "NewData/FwVp_Gap_RT.txt"
outputRTT = "RT/FwVp_RT_Overview.txt"

if not os.path.exists("NewData"):
    os.mkdir("NewData")

if not os.path.exists("RT"):
    os.mkdir("RT")

#Take tacks for RT
rtTerms = ["bin rep tree identification","bold identification engine","molecular using","bold id engine","bold id engine, november 2012","bold:aaa9475","bold:aab1628","bold:acf5706","bold:aaa9710","tree based identification june 2016","barcoding/bold","barcode","dna barcode 100%","bold-id engine","bold engine","bold id-engine","bold id engine manual","molecular data","tree based identification","tree-based identification","genbank blast","bold id engine","molecular coi barcode","molecular co1 barcode","bin taxonomy match","dna barcoding","dna barcode","bin match","bold database","dna","its2 and coi barcoding region","bold barcode library","by its2","dna sequence analysis","tree base identification","bold id_engine","bold id engine / taxonomy match","molecular coi","bold","identifikation ber sequenz, auftrennung larval nicht mglich","identifikation ber sequenz","dna-barcoding","dna sequence","coi blast","revers","bin taxonomy match |tree based identification","identifikation ber sequenz, limnius volckmari bildet zwergformen aus, die mit l. opacus verwechselt werden knnen","bold id","nj tree","revers bestimmt","bin taxonomy match below phylum","bold id engine manual below phylum","identifikation ueber sequenz","dna barcode match","dna based identification"]


info,ppgmOld = loadOldGap(OldGap)
proData = loadProgress(ProgFolder,info,Kingdom)
print(ppgmOld)
print(proData)
bpData,rtnew,rtcount = loadBoldpub(BoldDaset,info,rtTerms)
print(bpData)
print(rtnew)
print(rtcount)
makeOutputGap(info,proData,bpData,outputGap,outputRT)
makeOutputRT(outputRTT,rtcount)
