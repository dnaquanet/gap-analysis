from __future__ import division
import os
import matplotlib.pyplot as plt

#Load information from summary file
def loadInfos(file1):
    l = 0
    country = {}
    values1 = {}
    values2 = {}
    for line in open(file1):
        l += 1
        if l > 1:
            line2 = line.replace("\r\n","\n").rstrip("\n").split("\t")
            spec = line2[0]
            count = line2[11].split(";")
            vals = [int(va) for va in line2[1:4]]
            # vals2 = Total, BOLD public, BOLD private, GenBank
            vals2 = [sum(vals[0:3]),vals[0],vals[1],vals[2]]
            country[spec] = count
            values1[spec] = vals2
            values2[spec] = [int(va) for va in line2[4:10]]
    return(country,values1,values2)

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

def generateHitNumbersMarker(values3,lim):
    hits = [0,0,0,0,0,0,0]
    #hits = species,BPub rbcL, BPub matK, BPub both min, All rbcL, All matK, All both min
    for spec,vals3 in values3.items():
        hits = addOneList(hits,0)
        for x in range(0,len(vals3)):
            if vals3[x] >= lim:
                hits = addOneList(hits,x+1)
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

#make gap analysis output
def writeOutput(output,country,values,minimum,maximum):
    output2 = output + ".tsv"
    out2 = open(output2, "w")
    out2.write("Thresh\tNumber of Species\t%BOLD public\t%BOLD total\t%Total")
    for lim in range(minimum,maximum+1):
        hits = generateHitNumbers(values,lim)
        out2.write("\n" + str(lim) + "\t" + str(hits[0]))
        out2.write("\t" + str(round(hits[1]/hits[0],4)) + "\t" + str(round(hits[2]/hits[0],4)) + "\t" + str(round(hits[3]/hits[0],4)))
    out2.close()

#make gap analysis output per country
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

#get data for the different marker
def dataMarkerValues(values1,values2,country):
    # values1 = Total,BOLD pub,BOLD priv,GenBank
    # values2 = BPub rbcl,BPub matK,BPub both,GenB rbcl,GenB matK,GenB both

    # values3 = [BPub rbcl all, BPub matK all, BPub min both, All rbcl all, All matK all, All min both]
    values3 = {}

    for spec,val2 in values2.items():
        #formate barcode values per species
        val1 = values1.get(spec)
        bpr = val2[0]+val2[2]
        bpm = val2[1]+val2[2]
        bpb = min(bpr,bpm)
        ar = bpr + val2[3]+val2[5]
        am = bpm + val2[4]+val2[5]
        ab = min(ar,am)
        val3 = [bpr,bpm,bpb,ar,am,ab]
        values3[spec] = val3
    return(values3)

#summaries data for the different markers per country
def makeCountryDataMarker(values3,lim):
    # countrydata per country = #Species, #rbcl, #matK, #both (minimum)
    countryb = {}
    countryg = {}

    for spec,vals3 in values3.items():
        #For each country, sum up data
        counts = country.get(spec)
        for c in counts:
            oldb = countryb.get(c,[0,0,0,0])
            oldb[0] += 1
            if vals3[0] >= lim:
                oldb[1] += 1
            if vals3[1] >= lim:
                oldb[2] += 1
            if vals3[2] >= lim:
                oldb[3] += 1
            countryb[c] = oldb

            oldg = countryg.get(c,[0,0,0,0])
            oldg[0] += 1
            if vals3[3] >= lim:
                oldg[1] += 1
            if vals3[4] >= lim:
                oldg[2] += 1
            if vals3[5] >= lim:
                oldg[3] += 1
            countryg[c] = oldg

    return(countryb,countryg)

#make gap analysis output per marker
def writeOutputMarker(values3,lim,output,minimum,maximum):
    output5 = output + "_Marker.tsv"
    out5 = open(output5, "w")
    out5.write("Thresh\tNumber of Species\t%BOLD rbcL\t%BOLD matK\t%BOLD both min\t%All rbcL\t%All matK\t%All both min")
    for lim in range(minimum,maximum+1):
        hits = generateHitNumbersMarker(values3,lim)
        out5.write("\n" + str(lim) + "\t" + str(hits[0]))
        for x in range(1,len(hits)):
            out5.write("\t" + str(round(hits[x]/hits[0],4)))
    out5.close()

#make gap analysis for the different markers per country
def writeOutputCountryMarker(countrym,lim,output,type):
    output4 = output + "_lim" + str(lim) + "_country_" + type + ".tsv"
    out4 = open(output4,"w")
    out4.write("Country\tSpecies\t" + type + " rbcL\t" + type + " matK\t" + type + " min both")
    for cou in sorted(countrym.keys()):
        val = countrym.get(cou)
        val2 = [str(round(v/val[0],2)) for v in val]
        val2[0] = str(val[0])
        out4.write("\n" + cou + "\t" + "\t".join(val2))
    out4.close()

#generate pie charts
def makePiePlot(values1,values3,output,lim):
    #generate data
    #numbers = [no data, private data, only rbcL,only matK,both]
    numbersb = [0,0,0,0,0]
    numbersg = [0,0,0,0,0]
    for spec,vals3 in values3.items():
        if vals3[2] >= lim:
            numbersb[4] += 1
        elif vals3[1] >= lim:
            numbersb[3] += 1
        elif vals3[0] >= lim:
            numbersb[2] += 1
        elif values1.get(spec)[2] >= lim:
            numbersb[1] += 1
        else:
            numbersb[0] += 1

        print(spec,vals3,values1.get(spec))
        if vals3[5] >= lim:
            numbersg[4] += 1
            print("both")
        elif vals3[4] >= lim:
            numbersg[3] += 1
            print("matK")
        elif vals3[3] >= lim:
            numbersg[2] += 1
            print("rbcl")
        elif values1.get(spec)[2] >= lim:
            numbersg[1] += 1
            print("private")
        else:
            numbersg[0] += 1
            print("no")

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
    plt.savefig(output + "_lim" + str(lim) + "_marker.pdf")
    plt.savefig(output + "_lim" + str(lim) + "_marker.svg")




#User defined variables
#Input file summary files generated by FVP_open_checklist.py
inputFile = "Vascula-plants_v3.tsv"

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
#Test if output folder exists, otherwise create it
if not os.path.exists(outputFolder):
    os.makedirs(outputFolder)

#define variable for output file name
name = inputFile.split("_")[0]
version = inputFile.split("_")[1].split(".")[0][1:]
output = outputFolder + "/" + prefix + "_" + name + "_v" + str(version)
print(name,version,output)

#load information from summary file
country,values1,values2 = loadInfos(inputFile)

#Transform data for barplots
lists = makeCountryLists(country,values1,maxi)

#Make barplots
makeBarplot(country,lists,output,maxi)

#Make gap analysis output
writeOutput(output,country,values1,minimum,maximum)

#For values 1 and 5, make country data summaries
for lim in [1,5]:
    writeOutputCountry(country,values1,lim,output)

#Make gap analysis regarding the two different markers
values3 = dataMarkerValues(values1,values2,country)
print(values3)

writeOutputMarker(values3,lim,output,minimum,maximum)

#For values 1 and 5, make country data summaries, piecharts and country barplots
for lim in [1]:
    countryb,countryg = makeCountryDataMarker(values3,lim)
    writeOutputCountryMarker(countryb,lim,output,"BOLD")
    writeOutputCountryMarker(countryg,lim,output,"All")
    makePiePlot(values1,values3,output,lim)

print("finished")
