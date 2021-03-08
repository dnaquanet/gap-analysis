import requests
import time
from ratelimit import limits, sleep_and_retry
from string import ascii_lowercase
import os
import urllib3


urllib3.disable_warnings()


FIFTEEN_MINUTES = 900


start_time = time.time()
encoding = 'utf-8'

def loadSpeciesList(SpecFile):
    species = []
    genus = []
    data = open("lists/" + SpecFile).read().replace("\r\n","\n").split("\n")
    for da in data:
        species.append(da.strip(" ").strip("\n"))
        genus.append(da.split(" ")[0])
    genus = sorted(list(set(genus)))
    species = list(set(species))
    print(list1)
    print("Genera: " + str(len(genus)))
    print("Species: " + str(len(species)))
    return(species,genus)

def getLength(x):
    for info in [t.strip(" ") for t in x.split("\t")]:
        if info.startswith("<nucleotides>"):
            return(len(info[info.find("<nucleotides>")+len("<nucleotides>"):info.find("</n")].replace("-","")))

def getName(info):
    for info in [t.strip(" ") for t in info.split("\t")]:
        if info.startswith("<name>"):
            name = info[info.find("<name>")+len("<name>"):info.find("</n")]
            if " " in name:
                return(name)

def getPhylum(x,pyhlum):
    phyinfo = x[x.find("<phylum>"):x.find("</phylum>")]
    phyinfo = phyinfo.split("\t")
    phyinfo = [p.strip(" ") for p in phyinfo]
    for p in phyinfo:
        if p.startswith("<name>"):
            p2 = p[6:p.find("</")]
            if p2 in pyhlum:
                return(True)
    return(False)

def getMarker(x,marker,thresh):
    minf = x.split("\t")
    minf = [inf.strip(" ") for inf in minf]
    minfo = []
    for mi in range(len(minf)):
        if minf[mi] == "<sequence>":
            mc = [m for m in minf[mi:mi+10] if m.startswith("<markercode>")][0]
            seq = [m for m in minf[mi:mi+10] if m.startswith("<nucleotides>")][0]
            if marker in mc:
                leng = len(seq[seq.find("<nucleotides>")+len("<nucleotides>"):seq.find("</nucleotides")].replace("-",""))
                if leng >= thresh:
                    minfo.append(mc[mc.find("<markercode>")+len("<markercode>"):mc.find("</markercode>")])
    return(minfo)



def makeOutput(gen,geninfo,list1):
    out1 = open("rawdata/" + list1 + "/" + list1 + "_" + gen + ".txt", "w")
    out1.write("Species\tGenBank\tIDmet\tMarker")
    for da in geninfo:
        out1.write("\n" + "\t".join(da))
    out1.close()

def getBoldData(gen,thresh,species,list1,pyhlum,marker):
    geninfo = []
    response2 = requests.get("http://v4.boldsystems.org/index.php/API_Public/combined?taxon=" + gen + "&marker=COI-5P",verify=False)
    for x in response2.content.decode(encoding).replace("\r\n","\t").replace("  "," ").split("</record>")[:-1]:
        name = getName(x)
        if name in species:
            phy = getPhylum(x,pyhlum)
            if phy == False:
                print(x)
            else:
                minfo = getMarker(x,marker,thresh)
                if len(minfo) >= 1:
                    inst = x[x.find("<institution_storing>")+len("<institution_storing>"):x.find("</institution_storing>")]
                    if inst == "Mined from GenBank, NCBI":
                        genBank = "y"
                    else:
                        genBank = "n"
                    if x.find("<identification_method>") > 0:
                        idmet = x[x.find("<identification_method>")+len("<identification_method>"):x.find("</identification_method>")]
                    else:
                        idmet = ""
                    geninfo.append([name,genBank,idmet,";".join(minfo)])
    if len(geninfo) >= 1:
        makeOutput(gen,geninfo,list1)

@sleep_and_retry
@limits(calls=150, period=FIFTEEN_MINUTES)
def testDataPresent(gen):
    gen = gen.strip(" ")
    response = requests.get("http://v4.boldsystems.org/index.php/API_Public/stats?taxon=" + gen, verify=False)
    if response.status_code != 200:
        raise Exception('API response: {}'.format(response.status_code))
    return(int(response.content.decode(encoding).split(",")[0].split(":")[1]))

#Parameters

thresh = 500
list1 = "FwMi.txt"
pyhlum = ["Arthropoda","Annelida","Mollusca","Platyhelminthes"]
marker="COI-5P"

if not os.path.exists("rawdata"):
    os.mkdir("rawdata")

if not os.path.exists("rawdata/" + list1.split(".")[0]):
    os.mkdir("rawdata/" + list1.split(".")[0])

#Get Data
species,genus = loadSpeciesList(list1)

g=0
for gen in genus[genus.index("Orthetrum"):]:
    g += 1
    if testDataPresent(gen) > 0:
        getBoldData(gen,thresh,species,list1.split(".")[0],pyhlum,marker)
        if g%100 == 0:
            print(gen + " " + str(g))

print("--- %s seconds ---" % (time.time() - start_time))
