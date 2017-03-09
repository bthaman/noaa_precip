# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# MergeModel.py
# Created on: 2016-12-02 12:02:09.00000
#   (generated by ArcGIS/ModelBuilder)
# Description: 
# ---------------------------------------------------------------------------

# Import arcpy module
import arcpy
from arcpy import env

env.overwriteOutput = True
# Local variables:
out_fc = "C:\\Users\\wjt\\Documents\\ArcGIS\\Default.gdb\\m1dobs_allpt"

daily = r'C:\Users\wjt\Google Drive\Programming\Python\PycharmProjects\precip4\qpedaily\20161125\1dobs.shp'
all_pts = r'C:\Users\wjt\Google Drive\Programming\Python\PycharmProjects\precip4\Data\pts_cnty.shp'

fms = arcpy.FieldMappings()
fms.addTable(daily)
fms.addTable(all_pts)

idx = fms.findFieldMapIndex("GLOBVALUE")
fm = fms.getFieldMap(idx)
fm.mergeRule = 'Max'
fms.replaceFieldMap(idx, fm)

for f in fms.fields:
    if f.name not in ['HRAPX', 'HRAPY', 'LAT', 'LON', 'GLOBVALUE', 'UNITS']:
        fms.removeFieldMap(fms.findFieldMapIndex(f.name))

# Process: Merge
arcpy.Merge_management([daily, all_pts], out_fc, fms)
