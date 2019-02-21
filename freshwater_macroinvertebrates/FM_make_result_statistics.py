from __future__ import division
import os
import matplotlib.pyplot as plt

#Load information from summary file
def loadInfos(file1):
    l = 0
    country = {}
    values = {}
    for line in open(file1):
        l += 1
        if l > 1:
            line2 = line.replace("\r\n","\n").rstrip("\n").split("\t")
            spec = line2[0]
            count = line2[5].split(";")

            vals = [int(va) for va in line2[1:5]]
            # vals2 = Total, BOLD public, BOLD private, GenBank
            vals2 = [sum(vals[0:3]),vals[0],vals[1],vals[2]]
            country[spec] = count
            values[spec] = vals2
    return(country,values)

def addOneList(list1,pos):
    old = list1[pos]
    old += 1
    list1[pos] = old
    return(list1)

def generateHitNumbers(values,lim):
    hits = [0,0,0,0]
    #hits = species,BOLD Pub,BOLD total,total
    for spec in list(values.keys()):
        vals = values.get(spec)
        hits = addOneList(hits,0)
        if vals[1] >= lim:
            hits = addOneList(hits,1)
        if vals[1] + vals[2] >= lim:
            hits = addOneList(hits,2)
        if vals[0] >= lim:
            hits = addOneList(hits,3)
    return(hits)

#make a sortable list for the barplots
def makeCountryLists(country,values,maxi):
    lists = []
    for spe,coun in country.items():
        cou = len(coun)
        val = values.get(spe)

        #reset values by maximum
        val2 = [0,0,0,0]
        val2[0] = min(val[0],maxi)
        val2[1] = min(val[1],maxi)
        val2[2] = min(maxi-val2[1],val[2])
        val2[3] = min(maxi-val2[1]-val2[2],val[3])

        #species,numb. of country,reset total,reset BOLD public,reset BOLD private,reset GenBank
        lists.append([spe,cou,val2[0],val2[1],val2[2],val2[3]])

    #List sorts by number of BOLD barcodes, number of BOLD public barcodes, total number of barcodes, number of countries
    lists.sort(key=lambda x: x[3] + x[4],reverse=True)
    lists.sort(key=lambda x: x[3],reverse=True)
    lists.sort(key=lambda x: x[2],reverse=True)
    lists.sort(key=lambda x: x[1],reverse=True)
    return(lists)

#make a barplot graphic with barcodes ~ countries in which a species is monitored
def makeBarplot(country,lists,output,maxi):
    #Generate data for plot
    maxCount = max([x[1] for x in lists])
    listCount = [x[1] for x in lists]
    listBPub = [x[3] for x in lists]
    listBPri = [x[4] for x in lists]
    listGen = [x[5] for x in lists]

    #Make barplot
    fig, ax = plt.subplots()

    ax.get_xaxis().set_tick_params(direction='out', width=1)
    ax.get_yaxis().set_tick_params(direction='out', width=1)

    #y-axis: upper half = Number of barcodes, lower half = Number of countries in which a species is monitored
    y_lable = sorted(range(0,maxCount+1),reverse=True) + list(range(1,maxi+1))
    plt.yticks([p for p in range(-1 * maxCount,maxi+1)], y_lable,fontsize=10,fontname="Arial")
    plt.ylim(-1 * maxCount,maxi)

    #x-axis: data for each species
    plt.xlim([0,len(lists)])
    if len(lists) < 500:
        plt.xticks(range(0,len(lists),50),fontsize=10,fontname="Arial")
    elif len(lists) < 1000:
        plt.xticks(range(0,len(lists),100),fontsize=10,fontname="Arial")
    else:
        plt.xticks(range(0,len(lists),500),fontsize=10,fontname="Arial")

    #Plot bars
    pos = [r + 0.5 for r in range(0,len(lists))]
    width = 1
    plt.bar(list(pos),listBPub,width,color="darkblue",linewidth=0)
    plt.bar(pos,listBPri,bottom=listBPub,width=width,color="lightblue",linewidth=0)
    plt.bar(pos,listGen,bottom=[(listBPub[x]+listBPri[x]) for x in range(0,len(listBPub))],width=width,color="grey",linewidth=0)
    plt.bar(pos,[-1*c for c in listCount],width,color="darkgrey",linewidth=0)

    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')
    plt.axhline(y=0, color='black')
    plt.savefig(output + ".svg")
    plt.savefig(output + ".png")
    plt.close()

def writeOutput(output,country,values,minimum,maximum):
    output2 = output + ".tsv"
    out2 = open(output2, "w")
    out2.write("Thresh\tNumber of Species\t%BOLD public\t%BOLD total\t%Total")
    for lim in range(minimum,maximum+1):
        hits = generateHitNumbers(values,lim)
        out2.write("\n" + str(lim) + "\t" + str(hits[0]))
        out2.write("\t" + str(round(hits[1]/hits[0],4)) + "\t" + str(round(hits[2]/hits[0],4)) + "\t" + str(round(hits[3]/hits[0],4)))
    out2.close()

def writeOutputCountry(country,values,lim,output):
    cou_rev = {}
    output3 = output + "_lim" + str(lim) + "_country.tsv"
    out3 = open(output3,"w")
    for tax,cou in country.items():
        val = values.get(tax)
        for c in cou:
            old = cou_rev.get(c,[0,0,0,0])
            old = addOneList(old,0)
            if val[1] >= lim:
                old = addOneList(old,1)
            if val[1]+val[2] >= lim:
                old = addOneList(old,2)
            if val[0] >= lim:
                old = addOneList(old,3)
            cou_rev[c] = old

    out3.write("Country\tSpecies\tBOLD public\tBOLD private\tGenBank")
    for cou in sorted(list(cou_rev.keys())):
        val = cou_rev.get(cou)
        val2 = [str(round(v/val[0],2)) for v in val ]
        val2[0] = str(val[0])
        out3.write("\n" + cou + "\t" + "\t".join(val2))
    out3.close()


#User defined variables
#Folder including summary files generated by FM_open_checklist.py
inputFolder = "summary_groups"

#Name of output folder
outputFolder = "output"

#Name prefix of output files
prefix = "GapAnalysis"

#Define max. number of barcodes for barplots barcodes ~ countries in which a species is monitored
maxi = 10

#Define threshold for gap summary
minimum = 1
maximum = 10

#do analysis
allFiles = os.listdir(inputFolder)

#Test if output folder exists, otherwise create it
if not os.path.exists(outputFolder):
    os.makedirs(outputFolder)


for file1 in allFiles:
    #check file names for naming schema Taxongroup_vn.tsv in which vn stands for the file version
    if len(file1.split("_")) == 2 and file1.endswith("tsv") and file1.find("_v") > 1:
        print("starting analysis of " + file1)
        name = file1.split("_")[0]
        version = file1.split("_")[1].split(".")[0][1:]
        output = outputFolder + "/" + prefix + "_" + name + "_v" + str(version)

        #load information from summary file
        country,values = loadInfos(inputFolder + "/" + file1)
        #Transform data for barplots
        lists = makeCountryLists(country,values,maxi)
        #Make barplots
        makeBarplot(country,lists,output,maxi)
        #Make gap analysis output
        writeOutput(output,country,values,minimum,maximum)
        #For values 1 and 5, make country data summaries
        for lim in [1,5]:
            writeOutputCountry(country,values,lim,output)

print("finished")
