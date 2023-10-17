import config
import sys, os
import utility
import arcpy

arcpy.env.overwriteOutput = True

log_obj = utility.Open_Logger(config.log_file)
log_obj.info("Water Isolation Creator - Starting".format())

try:

    log_obj.info("Water Isolation Creator - Buffering valves".format())
    valve_buffer = arcpy.Buffer_analysis(config.WB_valves_in_mem, r"in_memory\valve_buffer", "0.25 Feet")

    log_obj.info("Water Isolation Creator - Erasing buffered valve areas from mains".format())
    mains_valve_buff_erase = arcpy.Erase_analysis(config.WB_mains_in_mem, valve_buffer, r"in_memory\mains_valve_buff_erase")

    log_obj.info("Water Isolation Creator - Dissolving the erased mains to connect Unsplit Lines".format())
    mains_dissolve = arcpy.Dissolve_management(mains_valve_buff_erase,
                                               r"in_memory\mains_dissolve",
                                               '',
                                               '',
                                               'SINGLE_PART',
                                               'UNSPLIT_LINES')

    log_obj.info("Water Isolation Creator - Adding fitting_ID".format())
    utility.add_and_assign_field_from_another(config.WB_fittings_in_mem, "fitting_ID", "LONG", "OBJECTID")

    log_obj.info("Water Isolation Creator - Adding main_ID".format())
    utility.add_and_assign_field_from_another(mains_dissolve, "main_ID", "LONG", "OBJECTID")

    log_obj.info("Water Isolation Creator - Running spatial join of fittings vs mains (1-m)".format())
    fitting_mains_sj_1toM = arcpy.SpatialJoin_analysis(config.WB_fittings_in_mem,
                                                       mains_dissolve,
                                                       r"in_memory\fitting_mains_sj_1toM",
                                                       "JOIN_ONE_TO_MANY",
                                                       "KEEP_ALL",
                                                       '',
                                                       "WITHIN_A_DISTANCE",
                                                       "0.2 Feet")

    log_obj.info("Water Isolation Creator - Getting values to group on".format())
    values_to_group_on = utility.get_list_of_unique_field_values(fitting_mains_sj_1toM, 'fitting_ID')

    log_obj.info("Water Isolation Creator - Grouping and getting lists of pivoted values".format())
    lists_of_pivoted_values = utility.values_group_and_pivot(values_to_group_on, fitting_mains_sj_1toM, 'fitting_ID', 'main_ID')

    log_obj.info("Water Isolation Creator - Smooshing the lists where they share values".format())
    smooshed_lists = utility.list_smoosher(lists_of_pivoted_values)

    # print(len(smooshed_lists))
    # for list in smooshed_lists:
    #     print(list)

    log_obj.info("Water Isolation Creator - Adding Group IDs".format())
    utility.add_field_if_needed(mains_dissolve, "Group_ID", "SHORT")
    counter = 1
    # assumes main_ID values from smooshed list are unique - I think they should be
    for list in smooshed_lists:
        with arcpy.da.UpdateCursor(mains_dissolve, ["main_ID", "Group_ID"]) as cursor:
            for row in cursor:
                if row[0] in list:
                    row[1] = counter
                cursor.updateRow(row)
        counter = counter + 1

    # this cleans up the remaining, individual main pieces that did not touch a fitting so were not part of spatial join
    with arcpy.da.UpdateCursor(mains_dissolve, ["Group_ID"]) as cursor:
        for row in cursor:
            if row[0] is None:
                row[0] = counter
            cursor.updateRow(row)
            counter = counter + 1

    log_obj.info("Water Isolation Creator - Dissolving on Group ID".format())
    mains_groupID_dissolve = arcpy.Dissolve_management(mains_dissolve,
                                                       r"in_memory\mains_groupID_dissolve",
                                                       'Group_ID',
                                                       '#',
                                                       'MULTI_PART')

    log_obj.info("Water Isolation Creator - Adding Color field (loops through 20 colors)".format())
    utility.add_field_if_needed(mains_groupID_dissolve, "Color", "SHORT")
    with arcpy.da.UpdateCursor(mains_groupID_dissolve, ["Color"]) as cursor:
        counter = 1
        for row in cursor:
            if counter <= 20:
                row[0] = counter
                counter = counter + 1
            else:
                counter = 1
                row[0] = counter
                counter = counter + 1
            cursor.updateRow(row)

    # possible final step - small buffer the result and select the ORIGINAL mains, tag those with an
    # isolation area id

    output_fc = os.path.join(config.working_gdb, "mains_with_group_ID")
    log_obj.info("Water Isolation Creator - Saving output to {}".format(output_fc))
    arcpy.CopyFeatures_management(mains_groupID_dissolve, output_fc)

    log_obj.info("Water Isolation Creator - Process Complete".format())


except Exception as e:
    arcpy.ExecuteError()
    log_obj.exception(str(sys.exc_info()[0]))
    log_obj.info("Water Isolation Creator Failed".format())
    pass



