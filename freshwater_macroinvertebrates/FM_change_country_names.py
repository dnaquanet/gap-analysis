import os

def load_country_names(file1):
    cou_names = {}
    for line in open(file1):
        line2 = line.strip("\n").split("\t")
        line2 = [l.strip(" ") for l in line2]
        cou_names[line2[0]] = line2[1]
        cou_names[line2[1]] = line2[1]
    return(cou_names)

def load_files(folder):
    files = os.listdir(folder)
    return(files)

def make_new_file(cou_names,folder,foldern,file1):
    l = 0
    if not os.path.exists(foldern):
        os.makedirs(foldern)    
    out = open(foldern + "/" + file1, "w")
    for line in open(folder + "/" + file1):
        line2 = line.rstrip("\n").replace("?","").split("\t")
        l += 1
        if l == 1:
            out.write("\t".join(line2))
        else:
            cou = line2[5].split(";")
            coun = [cou_names.get(c,"NO") for c in cou]
            if "NO" in coun:
                print(line2)
                print(coun)
            else:
                coun = ";".join(sorted(coun))
                out.write("\n" + "\t".join(line2[0:5]) + "\t" + coun)
    out.close()


cou_names = load_country_names("country_names.txt")
files = load_files("summary")
for f in files:
    print(f)
    make_new_file(cou_names,"summary","summary_new_names",f)
