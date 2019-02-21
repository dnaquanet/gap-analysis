from __future__ import division
import os

def getFiles(folder):
    files = os.listdir(folder)
    return(files)

def openFile(folder,file1,out,first):
    taxgroup = file1[:-7]
    print(taxgroup)
    l = 0
    with open(folder + "/" + file1) as f:
        for line in f:
            line2 = line.replace("\r","").strip("\n").split("\t")
            l += 1
            if l == 1:
                header = line2
                header.append("Taxgroup")
                if first == "Y":
                    out.write("\t".join(header))
            if l > 1:
                line2.append(taxgroup)
                out.write("\n" + "\t".join(line2))
    first = "N"
    return(out,first)






folder = "summary_insects"
output = "summary_groups/AllInsects_v1.tsv"
first = "Y"

files = getFiles(folder)
print(files)
out = open(output,"w")
for file in files:
    out,first = openFile(folder,file,out,first)
out.close()
