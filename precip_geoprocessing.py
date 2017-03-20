"""
 geoprocessing
 last update: 3/20/2017
"""
import Tkinter as tk
import tkMessageBox

# Import arcpy and sys modules
import arcpy
import os
from os.path import isfile, join


class GPtools:
    def __init__(self):
        self.layer_name = None
        self.input_fc_name = None
        self.run_status = None
        self.clip_boundary = None
        self.out_features = None
        self.raster_field = None
        self.mxd_name = None
        self.out_path = None

    def get_status(self):
        return self.run_status

    def point_to_raster(self, in_features, out_raster, val_field, workspace=None):
        self.input_fc_name = in_features
        self.out_features = out_raster
        self.raster_field = val_field
        if workspace is None:
            workspace = join(os.getcwd(), 'Precip.gdb')
        arcpy.env.workspace = workspace
        arcpy.env.overwriteOutput = True
        assignment_type = 'MAXIMUM'
        priority_field = ''
        cell_size = 0.045
        arcpy.PointToRaster_conversion(self.input_fc_name, self.raster_field, self.out_features,
                                       assignment_type, priority_field, cell_size)

    def clip_to_boundary(self, in_features, clip_boundary, out_features):
        self.layer_name = in_features
        self.clip_boundary = clip_boundary
        self.out_features = out_features

        try:
            print "Clipping points..."
            arcpy.env.overwriteOutput = True
            arcpy.Clip_analysis(self.layer_name, self.clip_boundary, self.out_features, "")
            self.run_status = 'OK'
        except Exception as e:
            self.run_status = e
        return self.run_status

    def featureclass_to_featureclass(self, in_features, out_path, out_features):
        self.layer_name = in_features
        self.out_path = out_path
        self.out_features = out_features

        try:
            print "feature class to feature class..."
            arcpy.env.overwriteOutput = True
            arcpy.FeatureClassToFeatureClass_conversion(self.layer_name, self.out_path, self.out_features)
            self.run_status = 'OK'
        except Exception as e:
            self.run_status = e
        return self.run_status

    def tinraster_3d(self, layer_name, input_fc_name, raster_field_name):
        self.layer_name = layer_name
        self.input_fc_name = input_fc_name
        self.raster_field = raster_field_name

        # Check out any necessary licenses
        print "Checking out extension licenses..."
        arcpy.CheckOutExtension("3D")
        arcpy.CheckOutExtension("spatial")
        # overwrite output
        arcpy.env.overwriteOutput = True

        # tin
        outTIN = os.getcwd() + r'\Data\tin_' + self.layer_name

        # raster
        outRASTER = os.getcwd() + r'\Data\RST_' + self.layer_name

        input_fc = join(os.getcwd(), 'Precip.gdb', layer_name)
        print(input_fc)

        try:
            # Process: Create TIN
            print "Creating TIN..."
            arcpy.CreateTin_3d(outTIN, "PROJCS['NAD_1983_StatePlane_Texas_Central_FIPS_4203_Feet',"
                                       "GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',"
                                       "SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],"
                                       "UNIT['Degree',0.0174532925199433]],PROJECTION['Lambert_Conformal_Conic'],"
                                       "PARAMETER['False_Easting',2296583.333333333],"
                                       "PARAMETER['False_Northing',9842500.0],"
                                       "PARAMETER['Central_Meridian',-100.3333333333333],"
                                       "PARAMETER['Standard_Parallel_1',30.11666666666667],"
                                       "PARAMETER['Standard_Parallel_2',31.88333333333333],"
                                       "PARAMETER['Latitude_Of_Origin',29.66666666666667],"
                                       "UNIT['Foot_US',0.3048006096012192]]",
                               "'" + self.input_fc_name + "' " + self.raster_field +
                               " Mass_Points <None>", "DELAUNAY")

            # arcpy.CreateTin_3d(outTIN, "PROJCS['NAD_1983_StatePlane_Texas_Central_FIPS_4203_Feet',"
            #                            "GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',"
            #                            "SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],"
            #                            "UNIT['Degree',0.0174532925199433]],PROJECTION['Lambert_Conformal_Conic'],"
            #                            "PARAMETER['False_Easting',2296583.333333333],"
            #                            "PARAMETER['False_Northing',9842500.0],"
            #                            "PARAMETER['Central_Meridian',-100.3333333333333],"
            #                            "PARAMETER['Standard_Parallel_1',30.11666666666667],"
            #                            "PARAMETER['Standard_Parallel_2',31.88333333333333],"
            #                            "PARAMETER['Latitude_Of_Origin',29.66666666666667],"
            #                            "UNIT['Foot_US',0.3048006096012192]]",
            #                    "'Database Connections\\Connection to FWSDE.sde\\sde_wjt.\"FREESE\\wjt\".hrap\\"
            #                    "sde_wjt.\"FREESE\\wjt\"." + self.input_fc_name + "' " + self.raster_field +
            #                    " Mass_Points <None>", "DELAUNAY")

            # Process: TIN to Raster
            print "Creating raster..."
            # typical cellsize is 12500
            arcpy.TinRaster_3d(outTIN, outRASTER, "FLOAT", "LINEAR", "CELLSIZE 5000", "1")
            self.run_status = 'OK'
        except Exception as e:
            self.run_status = e
            root = tk.Tk()
            # allows tkMessageBox to be shown without displaying Tkinter root window
            root.withdraw()
            tkMessageBox.showinfo("Python error", e)
            return self.run_status
        return self.run_status


class PdfCreator:
    def __init__(self):
        self.mxd_name = None
        self.run_status = None
        self.out_pdf = None
        self.lst_mxd = ['texas', 'austin', 'bexar', 'dfw', 'harris']

    def get_pdf_filename(self):
        return self.out_pdf

    def export_pdf(self, mxd_name, pdf_name, legend_title):
        self.mxd_name = mxd_name

        print " "
        # Set OverWrite if files already exist
        arcpy.OverWriteOutput = 1

        try:
            if self.mxd_name in self.lst_mxd:
                mapDoc = os.path.join(os.getcwd(), self.mxd_name + '.mxd')
            else:
                print "Incorrect argument passed in.  Aborting."
                raise ValueError('Incorrect argument passed in.')
        except ValueError:
            self.run_status = "Incorrect argument passed in."
            return self.run_status

        try:
            # set a variable to the full path and file name of the MXD
            fullnam = os.path.basename(mapDoc)

            # Strip off the MXD file extension and store as string variable for use in the 'out_pdf'
            nam = fullnam.strip(".mxd")
            # print nam

            map = arcpy.mapping
            mxd = map.MapDocument(mapDoc)

            map_document = mxd
            self.out_pdf = os.path.join(os.getcwd(), 'output', pdf_name + '.pdf')

            legend = arcpy.mapping.ListLayoutElements(mxd, "LEGEND_ELEMENT")[0]
            legend.title = legend_title

            # Set all the parameters as variables here:
            data_frame = 'PAGE_LAYOUT'
            resolution = "300"
            image_quality = "NORMAL"
            colorspace = "RGB"
            compress_vectors = "True"
            image_compression = "DEFLATE"
            picture_symbol = 'RASTERIZE_BITMAP'
            convert_markers = "False"
            embed_fonts = "True"
            layers_attributes = "NONE"
            georef_info = "False"
            print "Exporting PDF..."
            # Due to a known issue, the df_export_width and df_export_height must be set to integers in the code:
            map.ExportToPDF(map_document, self.out_pdf, data_frame, 640, 480, resolution, image_quality, colorspace,
                            compress_vectors, image_compression, picture_symbol, convert_markers, embed_fonts,
                            layers_attributes, georef_info)
            self.run_status = 'OK'
        except Exception as e:
            self.run_status = e
            print('Error exporting pdf')
        return self.run_status


class StatisticsCreator:
    def __init__(self):
        self.run_status = None
        self.fc_name = None
        self.summary_field_name = None

    def create_summary_stats(self, fc_name, summary_field_name):
        self.fc_name = fc_name
        self.summary_field_name = summary_field_name

        # overwrite output
        arcpy.env.overwriteOutput = True

        # Local variables:
        input_fc = "Database Servers\\FN27399_SQLEXPRESS2.gds\\HCFCD (VERSION:dbo.DEFAULT)" \
                   "\\HCFCD.DBO." + self.fc_name

        basins_GCDNA1983 = os.getcwd() + r'\Data\basins_GCDNA1983.shp'

        input_fc_GCSNA83 = "Database Servers\\FN27399_SQLEXPRESS2.gds\\HCFCD (VERSION:dbo.DEFAULT)" \
                           "\\HCFCD.DBO.Current_Clip_GCSNA83"

        Points_Basin_Join_shp = os.getcwd() + r'\Data\Points_Basin_Join.shp'

        Sum_Output_dbf = os.getcwd() + r'\Data\Sum_Output.dbf'

        try:
            # Process: Project
            print "Starting Summary_Statistics..."
            print "Projecting points..."
            arcpy.Project_management(input_fc, input_fc_GCSNA83,
                                     "GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',"
                                     "SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],"
                                     "UNIT['Degree',0.0174532925199433],METADATA['North America - NAD83',"
                                     "167.65,14.93,-47.74,86.45,0.0,0.0174532925199433,0.0,1350]]", "",
                                     "GEOGCS['HRAP_Sphere',DATUM['<custom>',SPHEROID['<custom>',"
                                     "6371200.0,0.0]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]")

            # Process: Spatial Join
            print "Spatial Join (This can take a while: please be patient)..."
            arcpy.SpatialJoin_analysis(input_fc_GCSNA83, basins_GCDNA1983, Points_Basin_Join_shp,
                               "JOIN_ONE_TO_ONE",
                               "KEEP_ALL")

            # Process: Summary Statistics
            arcpy.Statistics_analysis(Points_Basin_Join_shp, Sum_Output_dbf, self.summary_field_name +
                                      " MEAN", "BASIN_NAME")
            self.run_status = 'OK'
        except Exception as e:
            self.run_status = e
            root = tk.Tk()
            # allows tkMessageBox to be shown without displaying Tkinter root window
            root.withdraw()
            tkMessageBox.showinfo("Python error", e)
            print "Summary_Statistic_NET.py has errors and did not complete correctly"
        return self.run_status
