import csv
import argparse
import sys
import re
from option1_hw import *
from option2_grouping import *
from option3_filtering import *
import os
import itertools

def split_string(string, delimiter):
    return tuple(map(lambda x: x.strip(), string.split(delimiter)))

# >>> split_string("I, like, pie", ",")
# ('I', 'like', 'pie')

def make_field(line):
    """
    splits a line by tab
    """
    field = split_string(line, "\t")
    return field

def read_data(maker, file_name):
    """
    Reads a file and returns a tuple of tuples
    containing rows in the file and its entries.
    
    maker determines delimiter to split entries by.
    """
    tuples = ()
    with open(file_name, 'r') as file:
        for line in file:
            record = maker(line.strip())
            tuples = tuples + (record, )
    return tuples

def read_csv(csvfilename):
    """
    Reads a csv file and returns a list of list
    containing rows in the csv file and its entries.
    """
    rows = []

    with open(csvfilename, "rU") as csvfile:
        file_reader = csv.reader(csvfile)
        for row in file_reader:
            rows.append(row)
    return rows

def write_csv(newcsvfilename, lst, heading):
    with open(newcsvfilename, "w") as output:
        writer = csv.writer(output, lineterminator='\n')
        data = [heading,]
        data.extend(lst)
        writer.writerows(data)

def check_validity(data, specifications): #exits if not valid
    data_headings = data[0]
    for heading in data_headings:
        for field in specifications:
            if heading == field[1]:
                index = data_headings.index(heading)
                p = re.compile(field[3])
                for record in data[1:]:
                    if p.fullmatch(record[index]) == None or (";" in record[index]) or len(record[index])>0 and record[index][0] == record[index][-1] == '"':
                        print("Error in '" + heading + "' column" "\n  Cell value: " + record[index]) 
                        print ("  Expected value: " + field[2])
                        sys.exit()
                q = re.compile('^[\S]*$')
                if q.fullmatch(heading) == None:
                    print("Error in column name " + heading + ". Do not include whitespace within column name.")
                    sys.exit()
    print("\nValidity Check: Input data is valid.")

def check_validity_mapping_table(file_name, specifications): #returns false if not valid
    data = read_csv(file_name)
    data_headings = data[0]
    for heading in data_headings:
        for field in specifications:
            if heading == field[1]:
                index = data_headings.index(heading)
                p = re.compile(field[3])
                for record in data[1:]:
                    if p.fullmatch(record[index]) == None or (";" in record[index]) or len(record[index])>0 and record[index][0] == record[index][-1] == '"':
                        print("Error in '" + heading + "' column" "\n  Cell value: " + record[index]) 
                        print ("  Expected value: " + field[2])
                        return False
    return True



if __name__ == "__main__":
    #### Input params ##############################
    input_specifications = read_data(make_field, "input_format_specifications.txt")
    fields_to_analyze = [] # keeps a record of the names of fields that user can manipulate
    for line in input_specifications:
        fields_to_analyze.append(line[1])
    ################################################
    parser = argparse.ArgumentParser(description = "SDA Data Pre-validation phase: data cleaning and manipulation")
    parser.add_argument('full_data', type = str, help = "Input SDA dataset (.csv)")
    args = parser.parse_args()
    full_data = read_csv(args.full_data)
    full_data_headings = full_data[0]

    pri_key = None
    for field in input_specifications:
        ###remove field that is specified in input_format_specifications but not found in data
        if field[1] not in full_data_headings:
            fields_to_analyze.remove(field[1])
            print(field[1] + " as specified in input_format_specifications.txt was not found in SDA dataset")
            continue
        ###identifies primary key column
        if field[0] == "primary_key":
            pri_key = field[1]
    fields_to_analyze.insert(0, "0") #pressing "0" allows the user to exit task

    ###remove rows with null primary keys here
    if pri_key == None:
        sys.exit("\nError: Please indicate a valid primary key in the input_format_specifications.txt file.")
    else:
        print("\nRemoving any rows with NULL primary key (in column '" + pri_key + "')...")
        rows_removed = len(full_data)
        filtered_data = filter_NAs(full_data, pri_key)
        rows_removed -= len(filtered_data)
        print(str(rows_removed) + " row(s) removed.")

    check_validity(filtered_data, input_specifications)

    optional_task = None
    while optional_task != "0":
        optional_task = input("\nPlease select an optional task (1, 2 or 3): \n 1. Transform Address Data into Lat-Longs \n 2. Grouping of categories \n 3. Filter \n Press 0 to skip. ")
        if optional_task == "1":
            filtered_data = option1_addresses(filtered_data, fields_to_analyze)
            write_csv("applied_option1.csv", filtered_data[1:], filtered_data[0])
        elif optional_task == "2":
            filtered_data = option2_group(filtered_data, fields_to_analyze)
            write_csv("applied_option2.csv", filtered_data[1:], filtered_data[0])

        elif optional_task == "3":
            rows_removed = len(filtered_data)
            filtered_data = option3_filter(filtered_data, fields_to_analyze)
            rows_removed -= len(filtered_data)
            print(str(rows_removed) + " row(s) removed.")
            write_csv("applied_option3.csv", filtered_data[1:], filtered_data[0])

    
    print("\nAll the remaining rows in this dataset will be used to validate the algorithm output. ")

    #saving formats of final SDA data - so algorithm data will be in same comparable format
    final_format = []
    for index in range(1, len(filtered_data[0])):
        row_format = set()
        for row in filtered_data[1:]:
            row_format.add(row[index])
        final_format.append(list(row_format))

    #matching encrypted MSISDNs or IMSIs to phone numbers
    mapping_table = ""
    ID_input_specs = read_data(make_field, "MSISDN_or_IMSI_input_specifications.txt")
    while not os.path.isfile(mapping_table) or not check_validity_mapping_table(mapping_table, ID_input_specs):
        mapping_table = input("\nEnter the name of the encrypted MSISDN/IMSI file (.csv). File must be in the same directory as program. (Primary key in 1st column, Encrypted MSISDN/IMSI in 2nd column. Column headings are to be included) ")

    print("Program is now matching encrypted MSISDNs or IMSIs to primary key of each row...")
    mapping_table_data = read_csv(mapping_table)
    
    #cuts phone no. 6591234567 to 91234567
    def phone_num(num):
        return num[2:]
    
    #maps data row to MSISDN
    filtered_data_pri_key_index = filtered_data[0].index(pri_key)
    for person in filtered_data[1:]:
        for record in mapping_table_data[1:]:
            if phone_num(record[0]) == person[filtered_data_pri_key_index]:
                person.append(record[1])
                break

    write_csv("final_SDA_data.csv", filtered_data[1:], filtered_data[0] + [mapping_table_data[0][1]])

    print("\nMatching completed. Final SDA validation data stored in 'final_SDA_data.csv', format of final data stored in SDA_data_format.csv.")

    #saving formats of final SDA data - so algorithm data will be in same comparable format
    write_csv("SDA_data_format.csv", list(itertools.zip_longest(*final_format)), filtered_data[0][1:])

    print("\nPre-validation data processing is completed.\n")




































    
