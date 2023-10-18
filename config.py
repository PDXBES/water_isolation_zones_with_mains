import os
import arcpy
import utility

utility.datetime_print("Running Config")

log_file = r"\\besfile1\ism_projects\Work_Orders\Joes_Sandbox\dev\WB_isolation_log"

working_gdb = r"\\besfile1\ISM_PROJECTS\Work_Orders\Joes_Sandbox\gdb\water_isolation_working.gdb"

sde_connections = r"\\besfile1\CCSP\03_WP2_Planning_Support_Tools\03_RRAD\CCSP_Data_Management_ToolBox\connection_files"

PWBWATER_sde = os.path.join(sde_connections, "GISDB1.PWBWATER.sde")

WB_fittings_raw = PWBWATER_sde + r"\PWBWATER.ARCMAP_ADMIN.Fitting"
WB_valves_raw = PWBWATER_sde + r"\PWBWATER.ARCMAP_ADMIN.SystemValve"
WB_mains_raw = PWBWATER_sde + r"\PWBWATER.ARCMAP_ADMIN.PressurizedMain"

#for testing
# WB_fittings_raw = r"\\besfile1\ISM_PROJECTS\Work_Orders\Joes_Sandbox\gdb\water_isolation_working.gdb\fittings_sub"
# WB_valves_raw = r"\\besfile1\ISM_PROJECTS\Work_Orders\Joes_Sandbox\gdb\water_isolation_working.gdb\valves_sub"
# WB_mains_raw = r"\\besfile1\ISM_PROJECTS\Work_Orders\Joes_Sandbox\gdb\water_isolation_working.gdb\mains_sub"

# subset inputs
#FITTINGCODE 1 = 'MAIN'
#SUBTYPE 16 = 'TapPlug'
WB_fittings_fl = arcpy.MakeFeatureLayer_management(WB_fittings_raw, r"in_memory\fittings_fl",
                                                   "STATUS  = 'ACT' and FITTINGCODE = 1 and SUBTYPE <> 16")
WB_valves_fl = arcpy.MakeFeatureLayer_management(WB_valves_raw, r"in_memory\valves_fl",
                                                 "STATUS = 'ACT' and FITTINGCODE = 1")
WB_mains_fl = arcpy.MakeFeatureLayer_management(WB_mains_raw, r"in_memory\mains_fl",
                                                "STATUS = 'ACT' and SUBTYPE in (1, 4, 6, 9)")
                                                #SUBTYPE 1 = Distribution, 4 = Bypass, 6 = Interconnect

# copy to memory
WB_fittings_in_mem = arcpy.CopyFeatures_management(WB_fittings_fl, r"in_memory\WB_fittings_in_mem")
WB_valves_in_mem = arcpy.CopyFeatures_management(WB_valves_fl, r"in_memory\WB_valves_in_mem")
WB_mains_in_mem = arcpy.CopyFeatures_management(WB_mains_fl, r"in_memory\WB_mains_in_mem")


#test_sj_source = r"c:\temp_work\working.gdb\fitting_mains_sj_1toM"