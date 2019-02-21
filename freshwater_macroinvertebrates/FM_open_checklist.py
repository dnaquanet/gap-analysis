from __future__ import division
import os
from xlrd import open_workbook

#Functions used to generate output

#In a dictionary add a list for an entry (with or without list)
def addListDic(dic,entry,list1):
    old = dic.get(entry,[])
    old = old + list1
    old = sorted(list(set(old)))
    dic[entry] = old
    return(dic)


#Load contry information
#This section has to be adapted based on the format of the input file
def loadCountrySyns(file1,sheetname,genspe,spename,couname,synonyms,synname="",genname=""):
    #Identfiy relevant excel sheet and columns in the sheet
    book = open_workbook(file1)
    sheet = book.sheet_by_name(sheetname)
    header = [s.value for s in sheet.row(0)]
    sspec = header.index(spename)
    scount = header.index(couname)
    if synonyms == "Y":
        ssyns = header.index(synname)
    if genspe == "Y":
        sgen = header.index(genname)

    tot = sheet.nrows
    count = {}
    syns = {}

    for r in range(1,tot):
        da = [s.value for s in sheet.row(r)]
        #Identify species name
        spe = da[sspec].strip(" ")
        #List Countries
        cou = da[scount].strip(" ").strip(",").split(",")

        #Test if genus and species name is valid
        #If yes, note countries in which the species is monitored and synonyms
        if genspe == "Y":
            gen = da[sgen].strip(" ")
            if gen != " " and gen != "":
                if spe != " " and spe != "" and spe.endswith(" sp.") == False and spe.endswith(" sp") == False:
                    spen = gen + " " + spe
                    cou = [c.strip(" ") for c in cou]
                    count = addListDic(count,spen,cou)
                    if synonyms == "Y":
                        syn = da[ssyns].split(",")
                        for s in syn:
                            s = s.strip(" ")
                            if s != "" and s != " " and s != spen:
                                syns[s] = spen

                #Double check of too long species names
                elif len(spe.split(" ")) > 1:
                    print(spe)

        #Test if species name is valid
        #If yes, note countries in which the species is monitored and synonyms
        else:
            if spe != " " and spe != "" and spe.endswith(" sp.") == False and spe.endswith(" sp") == False and len(spe.split(" ")) == 2:
                cou = [c.strip(" ") for c in cou]
                count = addListDic(count,spe,cou)
                if synonyms == "Y":
                    syn = da[ssyns].split(",")
                    for s in syn:
                        s = s.strip(" ")
                        if s != "" and s != " " and s != spe:
                            syns[s] = spe
            #Double check of too long species names
            elif len(spe.split(" ")) > 2:
                print(spe)

    return(count,syns)

#Load data from progress report
def loadProgress(file2,syns):
    data = {}
    for line in open(file2):
        line2 = line.replace("\r", "").rstrip("\n").split("\t")
        #The first lines of the progress report are not meaningful for this analysis
        #Only species information are considered
        if len(line2) > 6 and line2[2] == "Species":
            name = line2[0].strip(" ")
            #Test if species name is a synonym, if yes, take the correct species name
            if name in syns.keys():
                name = syns.get(name)
            #Note barcodes deposited for the species/synonym
            bc = int(line2[7])
            old = data.get(name,0)
            data[name] = old + bc
    return(data)

#Reformate length of barcodes
def getLenGen(pos,da):
    leng = da[pos]
    if leng.endswith("]"):
        leng = int(leng[0:leng.find("[")])
    elif leng == "":
        leng = 0
    else:
        leng = int(leng)
    return(leng)

def getPosLen(lenrbcl,nlenrbcla,lenmatk,lim):
    no = 0
    p = 3
    if lenrbcl >= lim or nlenrbcla >= lim:
        p = 0
        no += 1
    if lenmatk >= lim:
        p = 1
        no += 1
    if no > 1:
        p = 2
    return(p)


#Load data from dataset
def loadDataset(file3,lim,syns,prog):
    data = {}
    cont = 0
    #Identfiy relevant excel sheet and columns in the sheet
    book = open_workbook(file3)
    sheet = book.sheet_by_name("Lab Sheet")
    header = [s.value for s in sheet.row(2)]
    nspec = header.index("Identification")
    nlenrbcl = header.index("rbcL Seq. Length")
    nlenmatk = header.index("matK Seq. Length")
    nlenrbcla = header.index("rbcLa Seq. Length")
    ngenb = header.index("Institution")
    ncont = header.index("Contamination")
    nflag = header.index("Flagged Record")
    tot = sheet.nrows
    for r in range(3,tot):
        da = [s.value for s in sheet.row(r)]
        spec = da[nspec].strip(" ")
        if len(spec.split(" ")) > 2:
            spec = spec.split(" ")[0] + " " + spec.split(" ")[1]
        #Test if species name is a synonym, if yes, take the correct species name
        if spec in syns.keys():
            spec = syns.get(spec)

        #Make a readable length variable
        lenrbcl = getLenGen(nlenrbcl,da)
        lenmatk = getLenGen(nlenmatk,da)
        lenrbcla = getLenGen(nlenrbcla,da)
        p = getPosLen(lenrbcl,lenrbcla,lenmatk,lim)

        #Make a readable GenBank variable
        genb = da[ngenb]
        if genb != "Mined from GenBank, NCBI":
            genb = "no"

        #Check if at least one barcode has a sufficient length, if it is obtained from GenBank and if it originates from an contamination
        if p < 3:
            if da[nflag] != "Yes" and da[ncont] != "rbcL" and da[ncont] != "rbcLa" and da[ncont] != "matK":
                #Note if the barcode is optained from GenBank
                old = data.get(spec,[[0,0,0],[0,0,0]])
                if genb == "no":
                    old[0][p] = old[0][p] + 1
                else:
                    old[1][p] = old[1][p] + 1
                data[spec] = old
            else:
                #If the Barcode originates from a contamination, remove it from the progress report count of the species
                old = prog.get(spec,0)
                old = old - 1
                prog[spec] = old
                cont += 1

    return(data,prog,cont)

#Calculate the number of barcodes which are BOLD public, BOLD private and mined from GenBank
#BOLD public = Barcodes in the dataset not mined from GenBank
#GenBank = Barcodes in the dataset mined from GenBank
#BOLD private = Barcodes in the progress report - BOLD public - GenBank (- contaminations)
def pubPriGb(progr,datas,count):
    ppg = {}
    for spec in count.keys():
        tot = progr.get(spec,0)
        da = datas.get(spec,[[0,0,0],[0,0,0]])
        pub = sum(da[0])
        gb = sum(da[1])
        priv = max(tot - pub - gb,0)
        ppg[spec] = [pub,priv,gb,da[0],da[1]]
    return(ppg)

#Generate output file (".tsv" format)
#Species are only listed if they have a valid species name and are monitored in at least one country
def makeSummary(count,ppg,syns,output):
    out = open(output,"w")
    out.write("Species\tPublic\tPrivate\tGenBank\tBpub rbcL\tBpub matK\tBpub both\tGenB rbcl\tGenB matK\t GenB both\tCountries\tList\tSynonyms")
    for tax in sorted(count.keys()):
        if tax != "" and tax != " ":
            vals = ppg.get(tax,[0,0,0,[0,0,0],[0,0,0]])
            cou = sorted(count.get(tax))
            sys = [sy for sy,sp in syns.items() if sp == tax]
            #Make sure that the species is listed in at least one country
            if len(cou) > 1:
                out.write("\n" + tax + "\t" + "\t".join([str(p) for p in vals[0:3]]) + "\t" + "\t".join([str(p) for p in vals[3]]) + "\t"  + "\t".join([str(p) for p in vals[4]]) + "\t" + str(len(cou)) + "\t" + ";".join(cou) + "\t" + ";".join(sorted(sys)))
            elif len(cou) == 1 and cou[0] != " " and cou[0] != "":
                out.write("\n" + tax + "\t" + "\t".join([str(p) for p in vals[0:3]]) + "\t" + "\t".join([str(p) for p in vals[3]]) + "\t"  + "\t".join([str(p) for p in vals[4]]) + "\t" + str(len(cou)) + "\t" + ";".join(cou) + "\t" + ";".join(sorted(sys)))
    out.close()


#User defined variables
#file1: Table with species and information in which countries the species are monitored
file1 = "Countries.xlsx"

#file2: Progress report of BOLD (is saved in ".xls" format although it is a text file)
file2 = "CL-DNAVP_progress.xls"

#file3: Dataset downloaded from BOLD including all possible tabs.
file3 = "CL-DNAVP_dataset.xlsx"

#output file name
output = "test_vp.tsv"

# Minimum length of a barcode to be valid (500 corresponds to the data from the progress report)
lim = 500

#Specify format of the checklist file
#Specify sheet name in the input table with species & country infomration
sheetname = "mod2"
#Species epiteton in extra column (Y or N)
genspe = "N"
#Genus column name (if species epiteton in extra column)
genname = "Genus"
#Species column name
spename = "Species"
#Country column name
couname = "Country"
#Table includes synonym information (Y or N)
synonyms = "Y"
#Synonym column name (if synonym information is included)
synname = "Synonym"


#Generating output file
count,syns = loadCountrySyns(file1,sheetname,genspe,spename,couname,synonyms,synname,genname)
progr = loadProgress(file2,syns)
datas,progr,cont = loadDataset(file3,lim,syns,progr)
ppg = pubPriGb(progr,datas,count)
makeSummary(count,ppg,syns,output)

print(syns)
print("Finished with " + str(output))
