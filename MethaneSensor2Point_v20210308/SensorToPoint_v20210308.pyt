#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import csv
import pandas as pd
import arcpy

fields = "SysTime,Time,CH4_ppm,CO2_ppm,H2O_ppm,CH4d_ppm,CO2d_ppm,GasP_torr,GasT_C,AmbT_C,RD0_us,Gnd,LTC0_v,HZ,Batt_v,BATT_PERCENT,Pres_Stat,Temp_Stat,Analyzer_Stat,Fit_Flag,MIU_VALUE,MIU_DESC,Latitude_deg,Longitude_deg,Alt_mm,AltAbvGnd_mm,GndXSpd_m_sec_x100,GndYSpd_m_sec_x100,GndZSpd_m_sec_x100,Heading_deg_x100,AbsPress_hPa,DiffPress_hPa,Temp_C,WindDir_deg,WindSpd_m_sec,WindSpd_z_m_sec,Roll_Angle_rad,Pitch_Angle_rad,Yaw_angle_rad,WindSpd3D_m_sec,Wind_Dir_deg,Uvector_m_sec,Vvector_m_sec,Wvector_m_sec,Temperature_c"



class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "ACUASI Tools"
        self.alias = "ACUASI Tools"

        # List of tool classes associated with this toolbox
        self.tools = [SensorToPoint]


class SensorToPoint(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Sensor To Point"
        self.description = "Convert from sensor source file to points for use in ArcGIS Pro"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        # Zero parameter -- Browse for input file
        param0 = arcpy.Parameter(
            displayName="Input File(s)",
            name="inputFile",
            datatype="DETextFile",
            parameterType="Required",
            direction="Input",
            multiValue=True)
        
        params = [param0]

        # default parameter values
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        print("Processing: " + parameters[0].valueAsText)
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        # prep file(s)
        #inPath = "C:/gina/acuasi/MethaneOnlySensor/20190912_Methane/"
        #inPathContents = os.listdir(inPath)
        #for f in inPathContents:
        f = parameters[0].valueAsText
        messages.addMessage("Input(s): " + f)
        inputs = f.split(";")
        for i in inputs:
            if i.split(".")[-1] == "txt":
                ipath, iname = os.path.split(i) # got it if needed later
                lname = iname.split(".")[0].replace("-", "_")
                messages.addMessage("lname: " + lname)
                #fPath = os.path.join(inPath, f)
                #print(fPath)
                with open(i, "r") as incsv:
                    reader = csv.reader(incsv)
                    with open(os.path.join(ipath, lname) + "_format.csv", "w") as outcsv:
                        next(incsv)
                        next(incsv)
                        outcsv.write(fields + '\n')
                        for line in incsv:
                            if not line.startswith("-"):
                                outcsv.write(line.strip() + "\n")
                            else:
                                break
                        df = pd.read_csv(outcsv.name)
                        df['Alt_m'] = df['Alt_mm'].div(1000)
                        df.to_csv(outcsv.name)
                        
                        inTable = outcsv.name
                        messages.addMessage("Processing CSV file: " + inTable)
                        aprx = arcpy.mp.ArcGISProject("current")
                        amap = aprx.activeMap
                        #messages.addMessage("Map name: " + amap.name)
                        x = "Longitude_deg"
                        y = "Latitude_deg"
                        z = "Alt_m"
                        arcpy.MakeXYEventLayer_management(inTable, x, y, lname, arcpy.SpatialReference(4326), z)
                        lyrxName = lname + ".lyrx"
                        lyrxPath = os.path.join(ipath, lname + ".lyrx")
                        arcpy.SaveToLayerFile_management(lname, lyrxPath, 'RELATIVE')
                        lyrx = arcpy.mp.LayerFile(lyrxPath)
                        messages.addMessage("Layer file path: " + lyrxPath)
                        #eLayer = arcpy.MakeFeatureLayer_management(lname)
                        #messages.addMessage("eLayer Type: " + str(type(eLayer)))
                        amap.addLayer(lyrx)
            
        return
