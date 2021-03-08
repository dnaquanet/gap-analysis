def load_list_names(file1):
    list_names = {}
    list_names_sub = {}
    list_sub = {}
    l = 0
    for line in open(file1):
        line2 = line.rstrip("\n").split("\t")
        l += 1
        if l > 1 and len(line2) > 2:
            if line2[3] == "No":
                list_names[line2[0]] = line2[2] + "_" + line2[1]
            else:
                list_names_sub[line2[0]] = line2[2] + "_" + line2[3] + "_" + line2[1]
                old = list_sub.get(line2[3],[])
                old.append(line2[0] + "_" + line2[2])
                list_sub[line2[3]] = old
    return(list_names,list_names_sub,list_sub)

def load_ambi(file1):
    l = 0
    ambi = {}
    for line in open(file1):
        l += 1
        line2 = line.rstrip("\n").split("\t")
        if l > 1:
            lists = line2[5].split(";")
            if len(lists) > 1:
                lists.remove("CL-AMBIE")
            for lis in lists:
                old = ambi.get(lis,[])
                old.append(line2[0:5])
                ambi[lis] = old
    return(ambi)

def load_erms(file1):
    l = 0
    erms = {}
    for line in open(file1):
        l += 1
        line2 = line.rstrip("\n").split("\t")
        if l > 1:
            lists = line2[2].split(";")
            for lis in lists:
                old = erms.get(lis,[])
                old.append(line2[0:2])
                erms[lis] = old
    return(erms)

def test_su(data,su,list_names_sub,spe):
    sun = ""
    for s in su:
        specs = data.get(s.split("_")[0],[])
        if len(specs) > 0:
            if spe in [specsa[0] for specsa in specs]:
                sun = list_names_sub.get(s.split("_")[0]).split("_")[2]
    return(sun)

def ambi_make_lists(ambi,list_names,list_names_sub,list_sub):
    for lis,name in list_names.items():
        if name.startswith("AMBI"):
            out = open("summary_lists/" + name + ".tsv", "w")
            out.write("Taxonomic group\tTaxonomic subgroup\tSpecies\tBOLD public\tBOLD private\tGenBank\tEcological status")
            typ = name.split("_")[1]
            su = list_sub.get(typ,[])
            if len(su) > 1:
                su = [s for s in su if s.split("_")[1] == "AMBI"]
            specs = ambi.get(lis)
            for spe in specs:
                sun = test_su(ambi,su,list_names_sub,spe[0])
                out.write("\n" + name.split("_")[1] + "\t" + sun + "\t" + spe[0] + "\t" + "\t".join(spe[2:5]) + "\t" + spe[1])
            out.close()

def erms_make_lists(erms,list_names,list_names_sub,list_sub):
    for lis,name in list_names.items():
        if name.startswith("ERMS"):
            out = open("summary_lists/" + name + ".tsv", "w")
            out.write("Taxonomic group\tTaxonomic subgroup\tSpecies\tTotal barcodes")
            typ = name.split("_")[1]
            su = list_sub.get(typ,[])
            if len(su) > 1:
                su = [s for s in su if s.split("_")[1] == "ERMS"]
            specs = erms.get(lis)
            for spe in specs:
                sun = test_su(erms,su,list_names_sub,spe[0])
                out.write("\n" + name.split("_")[1] + "\t" + sun + "\t" + "\t".join(spe[0:2]))
            out.close()


list_names,list_names_sub,list_sub = load_list_names("list_progress2.txt")
print(list_names)
print(list_names_sub)
print(list_sub)
ambi = load_ambi("overview_AMBI.tsv")
print(ambi)
ambi_make_lists(ambi,list_names,list_names_sub,list_sub)

erms = load_erms("overview_ERMS.tsv")
print(erms)
erms_make_lists(erms,list_names,list_names_sub,list_sub)
