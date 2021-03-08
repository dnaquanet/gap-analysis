def loadfile(file):
    specs = []
    info = {}
    data = open(file).read().replace("\r\n","\n").split("\n")
    for da in data[1:]:
        da = da.split("\t")
        if len(da) > 2:
            specs.append(da[2])
            info[da[2]] = da[0:2]
    return(specs,info)

def compareErAm(specsE,specsA):
    both = [sp for sp in specsA if sp in specsE]
    onA = [sp for sp in specsA if sp not in specsE]
    onE = [sp for sp in specsE if sp not in specsA]
    return(both,onA,onE)

def makeOutput(out,onA,infoA):
    ou1 = open(out,"w")
    ou2 = open(out.split(".")[0] + "_info.txt","w")

    ou1.write("Species")
    ou2.write("Taxonomic group\tTaxonomic subgoup\tSpecies")
    for spe in sorted(onA):
        ou1.write("\n" + spe)
        ou2.write("\n" + "\t".join(infoA.get(spe)) + "\t" + spe)
    ou1.close()
    ou2.close()

fileE = "OldData/MaEr_GapOld.txt"
fileA = "OldData/MaAm_GapOld.txt"
out = "lists/MaAmis.txt"

specsE,infoE = loadfile(fileE)
specsA,infoA = loadfile(fileA)
both,onA,onE = compareErAm(specsE,specsA)
makeOutput(out,onA,infoA)
