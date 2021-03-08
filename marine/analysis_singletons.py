from __future__ import division
import os
import matplotlib.pyplot as plt

def reverse_lists(lists):
    lists_r = {}
    for spe,lis in lists.items():
        for l in lis:
            old = lists_r.get(l,set())
            old.add(spe)
            lists_r[l] = old
    return(lists_r)

def load_list_names():
    l = 0
    names = {}
    for line in open("list_progress.tsv"):
        l += 1
        if l > 1:
            line2 = line.rstrip("\n").split("\t")
            if len(line2) > 1:
                print(line2)
                names[line2[0]] = line2[1]
    return(names)


def make_pie_plot(list1,numbers,output):
    labels = ["without barcode","singleton BOLD public","singleton BOLD private","singleton GenBank","with multiple Barcodes"]
    colors = ["white","darkblue", "lightblue", "grey", "forestgreen"]

    ax = plt.figure()
    ax1 = plt.subplot(111)
    patches, texts = ax1.pie(numbers, colors=colors, shadow=False, startangle=90)
    for p in patches:
        p.set_linewidth(0.5)
        p.set_edgecolor("black")

    ax1.legend(patches[::-1], labels[::-1], loc="best")
    ax1.set_title(list1)
    ax1.axis('equal')
    plt.tight_layout()
    plt.savefig(output + "_" + list1 + "_singletons.pdf")

def make_pie_plot2(list1,numbers,output):
    labels = ["without barcode","singleton","with multiple Barcodes"]
    colors = ["white","grey", "forestgreen"]

    ax = plt.figure()
    ax1 = plt.subplot(111)
    patches, texts = ax1.pie(numbers, colors=colors, shadow=False, startangle=90)
    for p in patches:
        p.set_linewidth(0.5)
        p.set_edgecolor("black")

    ax1.legend(patches[::-1], labels[::-1], loc="best")
    ax1.set_title(list1)
    ax1.axis('equal')
    plt.tight_layout()
    plt.savefig(output + "_" + list1 + "_singletons.pdf")

def open_list(file1):
    l = 0
    data = {}
    eco = {}
    lists = {}
    for line in open(file1):
        l += 1
        if l == 1:
            header = line.rstrip("\n").split("\t")
        else:
            line2 = line.rstrip("\n").split("\t")
            eco[line2[0]] = line2[1]
            data[line2[0]] = [int(line2[2]),int(line2[3]),int(line2[4])]
            lists[line2[0]] = line2[5].split(";")
    return(data,eco,lists)

def open_list2(file2):
    l = 0
    data = {}
    lists = {}
    for line in open(file2):
        l += 1
        if l == 1:
            header = line.rstrip("\n").split("\t")
        else:
            line2 = line.rstrip("\n").split("\t")
            data[line2[0]] = int(line2[1])
            lists[line2[0]] = line2[2].split(";")
    return(data,lists)

def make_output(output,lists_r,names,data):
    out = open(output + ".tsv", "w")
    out.write("Name\ttotal\twithout barcodes\twith singletons BOLD public\twith singletons BOLD private\twith singletons GenBank\twith multiple barcodes")
    text = []
    for l,specs in lists_r.items():
        name = names.get(l)
        tot = len(specs)
        wo = 0
        wm = 0
        sin = [0,0,0]
        for sp in specs:
            d = data.get(sp)
            if sum(d) == 0:
                wo += 1
            elif sum(d) == 1:
                sin[d.index(1)] = sin[d.index(1)] + 1
            else:
                wm += 1
        text.append([name,str(tot),str(wo),str(sin[0]),str(sin[1]),str(sin[2]),str(wm)])
        make_pie_plot(name,[wo,sin[0],sin[1],sin[2],wm],output)
    text = sorted(text)
    for te in text:
        out.write("\n" + "\t".join(te))

def make_output2(output2,lists_r2,names,data2):
    out = open(output2 + ".tsv", "w")
    out.write("Name\ttotal\twithout barcodes\twith singletons\twith multiple barcodes")
    text = []
    for l,specs in lists_r2.items():
        name = names.get(l)
        tot = len(specs)
        wo = 0
        wm = 0
        sin = 0
        for sp in specs:
            d = data2.get(sp)
            if d == 0:
                wo += 1
            elif d == 1:
                sin += 1
            else:
                wm += 1
        text.append([name,str(tot),str(wo),str(sin),str(wm)])
        make_pie_plot2(name,[wo,sin,wm],output2)
    text = sorted(text)
    for te in text:
        out.write("\n" + "\t".join(te))

if not os.path.exists("singletons"):
    os.makedirs("singletons")

type = "AMBI"
file1 = "overview_" + type + ".tsv"
data,eco,lists = open_list(file1)
lists_r = reverse_lists(lists)
names = load_list_names()
output = "singletons/summary_singletons_" + type
make_output(output,lists_r,names,data)

type = "ERMS"
file2 = "overview_" + type + ".tsv"
data2,lists2 = open_list2(file2)
lists_r2 = reverse_lists(lists2)
output2 = "singletons/summary_singletons_" + type
make_output2(output2,lists_r2,names,data2)
