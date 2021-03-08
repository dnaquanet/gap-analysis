from __future__ import division
import os
from xlrd import open_workbook
import matplotlib.pyplot as plt; plt.rcdefaults()
import numpy as np
import matplotlib.pyplot as plt


def dic_set_add(dic,entry,value):
    old = dic.get(entry,set())
    old.add(value)
    dic[entry] = old
    return(dic)

def fill_dic_entries(dic,list1,name):
    for ta in list1:
        dic = dic_set_add(dic,ta,name)
    return(dic)

def load_checklist_info(file1,syns):
    book = open_workbook(file1)
    if "mod" in book.sheet_names():
        sheet = book.sheet_by_name("mod")
        print(file1)
    else:
        sheet = book.sheet_by_name("animals")
    header = [s.value for s in sheet.row(4)]
    sspec = header.index("species")
    tot = sheet.nrows
    data = []
    for r in range(5,tot):
        da = [s.value for s in sheet.row(r)]
        spec = da[sspec]
        if spec != "" and spec != " ":
            if spec.find("(") > 0:
                spec = spec.split(" ")[0] + " " + spec.split(" ")[2]
            else:
                spec = " ".join(spec.split(" ")[0:2])
            if spec in syns.keys():
                spec = syns.get(spec)
            data.append(spec)
    return(data)

def load_all_checklists(syns):
    checklists = {}
    checklists_r = {}
    for file1 in os.listdir("Checklists"):
        if file1.endswith(".xlsx"):
            name = file1.split("_")[0]
            data = load_checklist_info("Checklists/" + file1,syns)
            checklists = fill_dic_entries(checklists,data,name)
            checklists_r[name] = data
    return(checklists,checklists_r)

def load_progress(file1,data,syns):
    l = "no"
    data_new = {}
    for line in open(file1):
        line2 = line.replace("\r", "").rstrip("\n").split("\t")
        if len(line2) > 6 and line2[2] == "Species":
            name = line2[0]
            if name.find("(") > 0:
                name = name.split(" ")[0] + " " + name.split(" ")[2]
            else:
                name = " ".join(name.split(" ")[0:2])
            if name in syns.keys():
                name = syns.get(name)
            bc = int(line2[7])
            old = data_new.get(name,0)
            data_new[name] = bc + old
    for spe,bc in data_new.items():
        if data.get(spe,0) < bc:
            data[spe] = bc
    return(data)

def load_all_prog(syns):
    all_prog = {}
    for file1 in os.listdir("Progress"):
        if file1.endswith(".xls"):
            all_prog = load_progress("Progress/" + file1, all_prog,syns)
    return(all_prog)

def load_dataset(file1,lim,prog,cont,syns):
    cont = 0
    data = {}
    book = open_workbook(file1)
    sheet = book.sheet_by_name("Lab Sheet")
    header = [s.value for s in sheet.row(2)]
    nspec = header.index("Identification")
    nlength = header.index("COI-5P Seq. Length")
    ngenb = header.index("Institution")
    ncont = header.index("Contamination")
    nflag = header.index("Flagged Record")
    tot = sheet.nrows
    for r in range(3,tot):
        da = [s.value for s in sheet.row(r)]
        spec = da[nspec]
        if spec.find("(") > 0:
            spec = spec.split(" ")[0] + " " + spec.split(" ")[2]
        else:
            spec = " ".join(spec.split(" ")[0:2])
        if spec in syns.keys():
            spec = syns.get(spec)
        leng = da[nlength]
        if leng.endswith("]"):
            leng = int(leng[0:leng.find("[")])
        elif leng == "":
            leng = 0
        else:
            leng = int(leng)
        genb = da[ngenb]
        if genb == "Mined from GenBank, NCBI":
            genb = "mined"
        else:
            genb = "no"
        if leng >= lim:
            if da[nflag] != "Yes" and da[ncont] != "COI-5P":
                old = data.get(spec,[0,0])
                if genb == "no":
                    old[0] = old[0] + 1
                else:
                    old[1] = old[1] + 1
                data[spec] = old
            else:
                old = prog.get(spec)
                old = old - 1
                prog[spec] = old
                cont += 1
    return(data,prog,cont)

def load_al_dataset(lim,prog,syns):
    datasets = {}
    cont = 0
    for file1 in os.listdir("Dataset"):
        if file1.endswith(".xlsx"):
            data,prog,cont = load_dataset("Dataset/" + file1,lim,prog,cont,syns)
            for da,val in data.items():
                datasets[da] = val
    return(datasets)

def priv_pub_gb(progress,datasets,checklists):
    ppg = {}
    for spec,tot in progress.items():
        check = checklists.get(spec,[])
        am = [c for c in check if c.split("-")[1].startswith("MT")]
        if len(am) > 0:
            da = datasets.get(spec,[0,0])
            pub = da[0]
            gb = da[1]
            priv = max(tot - pub - gb,0)
            ppg[spec] = [pub,priv,gb]
    return(ppg)

def load_list_names():
    file1 = "list_progress.tsv"
    l = 0
    lists_order = []
    lists = {}
    head_lists = []
    for line in open(file1):
        l += 1
        if l > 1:
            line2 = line.replace("\r","").rstrip("\n").split("\t")
            if len(line2) > 2:
                lists[line2[0]] = line2[1]
                lists_order.append(line2[0])
                if line2[2] == "ERMS" and line2[3] == "No":
                    head_lists.append(line2[0])
    return(lists,lists_order,head_lists)

def make_plot_ambi(da1,checklists_r,ppg,thresh,output,lists):
    res = []
    tot = []
    names = []
    for da in da1:
        specs = list(set(checklists_r.get(da)))
        pro = [0,0,0]
        tot.append(len(specs))
        names.append(lists.get(da))
        for spec in specs:
            val = ppg.get(spec,[0,0,0])
            if val[0] >= thresh:
                pro[0] = pro[0] + 1
            elif val[0] + val[1] >= thresh:
                pro[1] = pro[1] + 1
            elif val[0] + val[1] + val[2] >= thresh:
                pro[2] = pro[2] + 1
        proc = [pro[0]/len(specs),(pro[1] + pro[0])/len(specs),(pro[2] + pro[1] + pro[0])/len(specs)]
        res.append(proc)

    y_pos =[r + 0.5 for r in range(0,len(da1))]
    fig = plt.figure(figsize=(11,9))
    ax = fig.add_subplot(111)
    ax.barh(y_pos, [r[2] for r in res],color='grey',align='center')
    ax.barh(y_pos, [r[1] for r in res],color='lightblue',align='center')
    ax.barh(y_pos, [r[0] for r in res],color='darkblue',align='center')
    for i,child in enumerate(ax.get_children()[:len(tot)]):
        ax.text(child.get_bbox().x1 + 0.02,i + 0.5,tot[i], verticalalignment ='center',fontsize=10)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=11)
    ax.set_xlabel('Percentage',fontsize=11)
    ax.tick_params(axis='x', which='major', labelsize=11)
    ax.set_xlim(0,1)
    ax.tick_params(
        axis='both',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        direction="out",
        left=False,
        right=False,      # ticks along the right edge are off
        top=False,
        width=1)

    plt.savefig("plots/" + output + "_" + str(thresh) + ".svg")
    plt.savefig("plots/" + output + "_" + str(thresh) + ".pdf")
    output2 = "gap/" + output + "_" + str(thresh) + ".tsv"
    out2 = open(output2, "w")
    out2.write("Taxon\tSpecies\tBold private\tBold total\ttotal")
    for t in range(0,len(names)):
        out2.write("\n" + "\t".join([names[t],str(tot[t]),str(res[t][0]),str(res[t][1]),str(res[t][2])]))
    out2.close()

def make_plot_erms(da2,checklists_r,progress,thresh,output,lists,head_lists):
    res = []
    res2 = []
    tot = []
    names = []
    for da in da2:
        specs = list(set(checklists_r.get(da)))
        pro = 0
        tot.append(len(specs))
        names.append(lists.get(da))
        for spec in specs:
            val = progress.get(spec,0)
            if val >= thresh:
                pro += 1
        proc = pro/len(specs)
        res.append(proc)
        res2.append(pro)

    y_pos =[r + 0.5 for r in range(0,len(da2))]
    fig = plt.figure(figsize=(11,9))
    ax = fig.add_subplot(111)
    ax.barh(y_pos, res,color='blue',align='center')
    for i,child in enumerate(ax.get_children()[:len(tot)]):
        ax.text(child.get_bbox().x1 + 0.02,i + 0.5,tot[i], verticalalignment ='center',fontsize=10)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(names, fontsize=11)

    ax.set_xlabel('Percentage',fontsize=11)
    ax.tick_params(axis='x', which='major', labelsize=11)
    ax.set_xlim(0,1)
    ax.tick_params(
        axis='both',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        direction="out",
        left=False,
        right=False,      # ticks along the right edge are off
        top=False,
        width=1)

    plt.savefig("plots/" + output + "_" + str(thresh) + ".svg")
    plt.savefig("plots/" + output + "_" + str(thresh) + ".pdf")
    output2 = "gap/" + output + "_" + str(thresh) + ".tsv"
    out2 = open(output2, "w")
    out2.write("Taxon\tSpecies\tBarcodes\tPer Barcodes")
    tot2 = 0
    res3 = 0
    for t in range(0,len(names)):
        out2.write("\n" + "\t".join([names[t],str(tot[t]),str(res[t])]))
        if da2[t] in head_lists:
            tot2 += tot[t]
            res3 += res2[t]
    out2.write("\nall\t" + str(tot2) + "\t" + str(res3/tot2))
    out2.close()

def load_ecology(syns):
    ecol = {}
    for line in open("Species Ecological Group-2014-11-WORMS-2.tsv"):
        line2 = line.replace("\r", "").replace("sp.", "").rstrip("\n").split("\t")
        if len(line2) == 2:
            name = line2[0].strip(" ")
            if len(name.split(" ")) == 2:
                if name in syns.keys():
                    name = syns.get(name)
                ecol[name] = line2[1]
    return(ecol)

def ecol2ppg(ppg,ecol,checklists_r,thresh,listname):
    specs = list(set(checklists_r.get(listname)))
    cat = {}
    for tax in specs:
        ec = ecol.get(tax, "no")
        if ec == "not assigned":
            ec = "no"
        pro = ppg.get(tax, [0,0,0])
        old = cat.get(ec,[0,0,0,0])
        old[0] = old[0] + 1
        if pro[0] >= thresh:
            old[1] = old[1] + 1
        elif pro[0] + pro[1] >= thresh:
            old[2] = old[2] + 1
        elif pro[0] + pro[1] + pro[2] >= thresh:
            old[3] = old[3] + 1
        cat[ec] = old
    return(cat)

def make_plot_cat(cat,output):
    res = []
    res2 = []
    tot = []
    canames = sorted(cat.keys())[::-1]
    for ca in canames:
        val = cat.get(ca)
        res.append([val[1]/val[0],(val[1]+val[2])/val[0],(val[1]+val[2]+val[3])/val[0]])
        tot.append(val[0])

    y_pos =[r + 0.5 for r in range(0,len(canames))]
    fig = plt.figure(figsize=(11,9))
    ax = fig.add_subplot(111)
    ax.barh(y_pos, [r[2] for r in res],color='grey',align='center')
    ax.barh(y_pos, [r[1] for r in res],color='lightblue',align='center')
    ax.barh(y_pos, [r[0] for r in res],color='darkblue',align='center')
    for i,child in enumerate(ax.get_children()[:len(tot)]):
        ax.text(child.get_bbox().x1 + 0.02,i + 0.5,tot[i], verticalalignment ='center',fontsize=10)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(canames, fontsize=11)
    ax.set_xlabel('Percentage',fontsize=11)
    ax.tick_params(axis='x', which='major', labelsize=11)
    ax.set_xlim(0,1)
    ax.tick_params(
        axis='both',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        direction="out",
        left=False,
        right=False,      # ticks along the right edge are off
        top=False,
        width=1)

    plt.savefig("plots/" + output + "_" + str(thresh) + ".svg")
    plt.savefig("plots/" + output + "_" + str(thresh) + ".pdf")
    output2 = "gap/" + output + "_" + str(thresh) + ".tsv"
    out2 = open(output2, "w")
    out2.write("Taxon\tSpecies\tBold private\tBold total\ttotal")
    for t in range(0,len(canames)):
        out2.write("\n" + "\t".join([canames[t],str(tot[t]),str(res[t][0]),str(res[t][1]),str(res[t][2])]))
    out2.close()

def write_detailed_output(da1,da2,checklists,ppg,prog,ecol,lists,output):
    outam = open(output + "_AMBI.tsv","w")
    outer = open(output + "_ERMS.tsv","w")
    outam.write("Species\tEcology\tPublic BOLD\tPrivate BOLD\tGenBank\tLists")
    outer.write("Species\tTotal Barcodes\tLists")
    for spec in sorted(checklists.keys()):
        amli = [l for l in checklists.get(spec) if l in da1]
        erms = [l for l in checklists.get(spec) if l not in da1]
        if len(amli) >= 1:
            outam.write("\n" + spec + "\t" + ecol.get(spec,"not in list") + "\t" + "\t".join([str(i) for i in ppg.get(spec,[0,0,0])]) + "\t" + ";".join(sorted(list(set(amli)))))
        if len(erms) >= 1:
            outer.write("\n" + spec + "\t" + str(prog.get(spec,0)) + "\t" + ";".join(sorted(list(set(erms)))))
    outam.close()
    outer.close()

def load_syns_rem(file1):
    syns = {}
    book = open_workbook(file1)
    sheetsyn = book.sheet_by_name("Synonyms")
    tot = sheetsyn.nrows
    for r in range(1,tot):
        da = [s.value for s in sheetsyn.row(r)]
        spec = da[0].strip(" ")
        syn = da[1].strip(" ")
        if spec != "" and spec != " ":
            syns[syn] = spec
    remove = set()
    sheetrem = book.sheet_by_name("Remove")
    tot = sheetrem.nrows
    for r in range(1,tot):
        da = [s.value for s in sheetrem.row(r)]
        spec = da[0].strip(" ")
        if spec != "" and spec != " ":
            remove.add(spec)
    return(syns,remove)

def remove_from_ambi(da1,rem):
    for lis in da1:
        specs = checklists_r.get(lis)
        for s in rem:
            if s in specs:
                specs.remove(s)
        checklists_r[lis] = specs

    for spec in rem:
        lis = checklists.get(spec)
        for d in da1:
            if d in lis:
                lis.remove(d)
        checklists[spec] = lis
    return(checklists,checklists_r)

lim = 500

syns,remove = load_syns_rem("update_AMBI.xlsx")

checklists,checklists_r  = load_all_checklists(syns)
lists,lists_order,head_lists = load_list_names()
da1 = [l for l in lists_order[::-1] if (l.split("-")[1].startswith("MT") == True) or (l.split("-")[1].startswith("AMBIE") == True)]
da2 = [l for l in lists_order[::-1] if (l.split("-")[1].startswith("MT") == False) and (l.split("-")[1].startswith("AMBIE") == False)]
checklists,checklists_r = remove_from_ambi(da1,remove)
print("checklists loaded")

progress = load_all_prog(syns)
print("progress reports loaded")
#first value BOLD, second value GeneBank
datasets = load_al_dataset(lim,progress,syns)
print("datasets loaded")
#pub, priv, genb
ppg = priv_pub_gb(progress,datasets,checklists)







if not os.path.exists("plots"):
    os.makedirs("plots")
if not os.path.exists("gap"):
    os.makedirs("gap")

for thresh in [1,5]:
    print("calculating threshold " + str(thresh))
    make_plot_ambi(da1,checklists_r,ppg,thresh,"AMBI",lists)
    make_plot_erms(da2,checklists_r,progress,thresh,"ERMS",lists,head_lists)
    ecol = load_ecology(syns)
    for list1 in da1:
        cat = ecol2ppg(ppg,ecol,checklists_r,thresh,list1)
        make_plot_cat(cat, list1 + "_" + lists.get(list1) + "_cat")

write_detailed_output(da1,da2,checklists,ppg,progress,ecol,lists,"overview")
