For the gap-analyis the supplement table of the publication "Weigand et al. (2019) DNA barcode reference libraries for the monitoring of aquatic biota in
Europe: Gap-analysis and recommendations for future work. Science of the Total Environment 678: 499–524" are used.

For a smooth analysis, the different excel-tabs should be stored as separated text-files in a folder called "OldData" using the following nameing scheme:

The following abbreviations are used: 
- Freshwater macroinvertebrates: FwMi
- Freshwater vascular plants: FwVp
- Marine fish: MaFi
- Marine ERMS: MaEr
- Marine AMBI: MaAm

The files are named e.g. "MaAm_GapOld.txt"

Steps of the Gap Analysis:

1) Using the BOLD API to download metadata for the public available barcodes (e.g. apiBoldERMS.py). For AMBI first a list including only species currently missing in the ERMS data is generated (compErmsAmbi.py)
2) BOLD progress reports have to be downloaded manually from BOLD, making sure that all species of the different species lists are included. Those reports are saved in a folder "progressReports"
3) New gap results per species are generated (e.g. AnalyseBoldNew_ERMS)
4) Comparisions of old and new gap results are generated (e.g. CompareNewOldErms.py)
5) The proportion of barcodes identified by reverse taxonomy is calculated (e.g. CompareMaEr-RT.py)
