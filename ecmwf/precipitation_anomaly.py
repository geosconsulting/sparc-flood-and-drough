import arcpy

# Local variables:
arcpy.env.workspace = r"J:\OMEP_GIS\01_Data\00_SDE_Connection_files\wfp__hq_esri__directdb__10_11_40_221.sde"

fdlist = arcpy.ListDatasets()
for fd in fdlist:
    print fd
