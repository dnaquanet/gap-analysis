from __future__ import division
import os
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import cartopy.io.shapereader as shpreader

def read_code_dic(code_file):
    code_dic = {}
    for line in open(code_file):
        line2 = line.replace("\r","").rstrip("\n").split("\t")
        if len(line2) == 2:
            code_dic[line2[0]] = line2[1]
    return(code_dic)

def load_country_info(file1,code_dic):
    country_data = {}
    l = 0
    max_specs = 0
    for line in open(file1):
        l += 1
        line2 = line.replace("\r","").replace("?","").rstrip("\n").split("\t")
        if len(line2) > 2 and l > 1:
            count = code_dic.get(line2[0],"no data yet")
            country_data[count] = [int(line2[1]),float(line2[2]),float(line2[3]),float(line2[4])]
            if count == "no data yet":
                print(line2[0] + " no country code yet")
            if int(line2[1]) > max_specs:
                max_specs = int(line2[1])
    return(country_data,max_specs)

def get_color(value):
    cmap = plt.get_cmap("plasma_r")
    va = camp(value)
    print(va)

def make_map(country_data,output_name,maxi,levels):
    #Kartendetails
    shapename = 'admin_0_countries'
    countries_shp = shpreader.natural_earth(resolution='10m',category='cultural', name=shapename)
    #Farbverlauf
    cmap = plt.get_cmap("plasma_r")

    plt.figure(figsize=(20,14))
    for r in range(0,4):
        ax = plt.subplot(2,2,r+1,projection=ccrs.PlateCarree())
        for country in shpreader.Reader(countries_shp).records():
            code = country.attributes["ADM0_A3_US"]
            value = country_data.get(code,["NA","NA","NA","NA"])
            if value[1] == "NA":
                ax.add_geometries(country.geometry, ccrs.PlateCarree(),
                            lw=1,facecolor=(0.9,0.9,0.9),edgecolor=(0,0,0,1),alpha=1)
            else:
                if r == 0:
                    col = list(cmap(value[r]/maxi))
                else:
                    col = list(cmap(value[r]))
                ax.add_geometries(country.geometry, ccrs.PlateCarree(),
                    lw=1,facecolor=col,edgecolor=(0,0,0,1),alpha=1)

        #Legende
        if r == 0:
            sm = plt.cm.ScalarMappable(cmap=cmap,norm=plt.Normalize(0,maxi))
        else:
            sm = plt.cm.ScalarMappable(cmap=cmap,norm=plt.Normalize(0,1))
        sm._A = []
        cb = plt.colorbar(sm)
        cb.ax.set_yticklabels(cb.ax.get_yticklabels(), fontsize=8)
        # plt.colorbar(sm,ax=ax)

        #Map size
        ax.set_extent([-25,52,30,70])
        ax.set_aspect('auto', adjustable="box")
        ax.set_title(levels[r],fontsize=10)


    #Save
    plt.savefig(output_name)
    plt.savefig(output_name[:-3] + "pdf")
    plt.close()

def load_country_info_markers(file1,code_dic):
    country_data = {}
    l = 0
    max_specs = 0
    for line in open(file1):
        l += 1
        line2 = line.replace("\r","").replace("?","").rstrip("\n").split("\t")
        if len(line2) > 2 and l > 1:
            count = code_dic.get(line2[0],"no data yet")
            country_data[count] = [int(line2[1]),float(line2[2]),float(line2[3]),float(line2[4]),float(line2[5]),float(line2[6]),float(line2[7])]
            if count == "no data yet":
                print(line2[0] + " no country code yet")
            if int(line2[1]) > max_specs:
                max_specs = int(line2[1])
    return(country_data,max_specs)

def make_map_markers(country_data2,output_name,maxi,levels):
    #Kartendetails
    shapename = 'admin_0_countries'
    countries_shp = shpreader.natural_earth(resolution='10m',category='cultural', name=shapename)
    #Farbverlauf
    cmap = plt.get_cmap("plasma_r")

    plt.figure(figsize=(40,14))
    for r in range(0,7):
        r2 = r
        if r > 3:
            r2 = r + 1
        ax = plt.subplot(2,4,r2+1,projection=ccrs.PlateCarree())
        for country in shpreader.Reader(countries_shp).records():
            code = country.attributes["ADM0_A3_US"]
            value = country_data2.get(code,["NA","NA","NA","NA","NA","NA","NA"])
            if value[1] == "NA":
                ax.add_geometries(country.geometry, ccrs.PlateCarree(),
                            lw=1,facecolor=(0.9,0.9,0.9),edgecolor=(0,0,0,1),alpha=1)
            else:
                if r == 0:
                    col = list(cmap(value[r]/maxi))
                else:
                    col = list(cmap(value[r]))
                ax.add_geometries(country.geometry, ccrs.PlateCarree(),
                    lw=1,facecolor=col,edgecolor=(0,0,0,1),alpha=1)

        #Legende
        if r == 0:
            sm = plt.cm.ScalarMappable(cmap=cmap,norm=plt.Normalize(0,maxi))
        else:
            sm = plt.cm.ScalarMappable(cmap=cmap,norm=plt.Normalize(0,1))
        sm._A = []
        cb = plt.colorbar(sm)
        cb.ax.set_yticklabels(cb.ax.get_yticklabels(), fontsize=8)
        # plt.colorbar(sm,ax=ax)

        #Map size
        ax.set_extent([-25,52,30,70])
        ax.set_aspect('auto', adjustable=None)
        ax.set_title(levels[r],fontsize=10)


    #Save
    plt.savefig(output_name)
    plt.savefig(output_name[:-3] + "pdf")
    plt.close()

if not os.path.exists("map_plotting"):
    os.makedirs("map_plotting")

file1 = "Vascula-plants_v3.tsv"
name = file1.split("_")[0]
version = file1.split("_")[1].split(".")[0][1:]
code_dic = read_code_dic("country_codes.txt")
levels = ["Number of species","BOLD public", "BOLD total", "Total"]
levels2 = ["Number of species","rbcl BOLD public", "matk BOLD public", "both BOLD public","rbcl Public", "matk Public", "both Public"]

for lim in [1,5]:
    inp = "output/Progress_report_overview_" + name + "_v" + str(version) + "_lim" + str(lim) +"_country.tsv"
    inp2 =  "output/Progress_report_overview_" + name + "_v" + str(version) + "_lim" + str(lim) +"_country_markers.tsv"
    out = "map_plotting/" + name + "_v" + str(version) + "_lim" + str(lim) + ".svg"
    out2 = "map_plotting/" + name + "_v" + str(version) + "_lim" + str(lim) + "_markers.svg"
    country_data,max_specs = load_country_info(inp,code_dic)
    make_map(country_data,out,max_specs,levels)
    country_data2,max_specs2 = load_country_info_markers(inp2,code_dic)
    make_map_markers(country_data2,out2,max_specs2,levels2)
    print("map of lim " + str(lim) + " finished")
