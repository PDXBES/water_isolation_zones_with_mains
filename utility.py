import arcpy
import logging
from datetime import datetime
import sys



def datetime_print(message):
    print(datetime.now().strftime("%Y/%m/%d %H:%M:%S") + " " + message)


def Open_Logger(file_name):
    formatter = logging.Formatter(fmt='%(asctime)s %(module)s,line: %(lineno)d %(levelname)8s | %(message)s',
                                  datefmt='%Y/%m/%d %H:%M:%S')  # %I:%M:%S %p AM|PM format
    logging.basicConfig(filename='%s.log' % (file_name),
                        format='%(asctime)s %(module)s,line: %(lineno)d %(levelname)8s | %(message)s',
                        datefmt='%Y/%m/%d %H:%M:%S', filemode='a', level=logging.INFO)
    log_obj = logging.getLogger()
    log_obj.setLevel(logging.DEBUG)
    # log_obj = logging.getLogger().addHandler(logging.StreamHandler())

    # console printer
    screen_handler = logging.StreamHandler(stream=sys.stdout)  # stream=sys.stdout is similar to normal print
    screen_handler.setFormatter(formatter)
    logging.getLogger().addHandler(screen_handler)

    log_obj.info("Starting log session..")
    return log_obj


#input_fc = 'fittings_mains_sj_1toM'
#field = 'FACILITYID'
def get_list_of_unique_field_values(input_fc, field):
    fieldIDs = []
    with arcpy.da.SearchCursor(input_fc, [field]) as cursor:
        for row in cursor:
            fieldIDs.append(row[0])
    fieldID_set = set(fieldIDs)
    fieldID_list = list(fieldID_set)
    return fieldID_list


#input_fc = 'fittings_mains_sj_1toM'
#field1 = 'FACILITYID'
#field2 = 'AMID'
def values_group_and_pivot(fieldID_list, input_fc, field_to_group_on, field_to_pivot):
    main_IDs = []
    pivotted_ID_list = []

    for ID in fieldID_list:
        with arcpy.da.SearchCursor(input_fc, [field_to_group_on, field_to_pivot]) as cursor:
            for row in cursor:
                if row[0] == ID and row[1] is not None:
                    main_IDs.append(int(row[1]))
        pivotted_ID_list.append(main_IDs)
        main_IDs = []
    return pivotted_ID_list


# for list of lists - for any lists that have even a single matching value...
# it combines those lists and creates a distinct set of values within each new list
# https://www.reddit.com/r/learnpython/comments/n84jn4/list_of_lists_merge_sublists_with_common_elements/ - SuurSieni
def list_smoosher(list_of_lists):
    # List of all values
    values = sum(list_of_lists, [])
    # Each value into its own set
    values = list(map(lambda x: {x}, set(values)))
    # Loop sublists
    for item in map(set, list_of_lists):
        # All value sets that share at least one value with sublist
        values_in = [x for x in values if x & item]
        # All value sets with no shared values with sublist
        values_out = [x for x in values if not x & item]
        # Merge value sets with shared values into one set
        values_in = set([]).union(*values_in)
        # Re-define the value sets with the new sets, if any were merged
        if values_in:
            values = values_out + [values_in]
    list2 = [list(x) for x in values]
    return list2


def list_field_names(input_fc):
    field_names = []
    fields = arcpy.ListFields(input_fc)
    for field in fields:
        field_names.append(field.name)
    return field_names


def add_field_if_needed(input_fc, field_to_add, field_type, precision=None, scale=None, length=None):
    field_names = list_field_names(input_fc)
    if field_to_add not in field_names:
        arcpy.AddField_management(input_fc, field_to_add, field_type, precision, scale, length)


def assign_field_from_another(fc, source_field, target_field):
    with arcpy.da.UpdateCursor(fc, [source_field, target_field]) as cursor:
        for row in cursor:
            if row[0] is not None:
                row[1] = row[0]
            cursor.updateRow(row)


def add_and_assign_field_from_another(input_fc, field_to_add_and_assign, field_type, source_field):
    add_field_if_needed(input_fc, field_to_add_and_assign, field_type)
    assign_field_from_another(input_fc, source_field, field_to_add_and_assign)


def get_distinct_value_list(fc, field):
    value_list = []
    with arcpy.da.SearchCursor(fc, field) as cursor:
        for row in cursor:
            value_list.append(row[0])
    value_set = set(value_list)
    final_list = list(value_set)
    return final_list
