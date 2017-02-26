import re

def ensure_valid_response(input_msg, valid_responses_lst, input_is_lst = None):
    if input_is_lst == "list":
        fail = True
        while fail:
            response = input(input_msg)
            response = re.split(''' (?=(?:[^'"]|'[^']*'|"[^"]*")*$)''', response)
            for i in range(len(response)):
                if (response[i].startswith('"') and response[i].endswith('"')) or (response[i].startswith("'") and response[i].endswith("'")):
                    response[i] = response[i][1:-1]
                if response[i] not in valid_responses_lst:
                    print ("\n'" + ' '.join(response) + "' is not a valid response. ")
                    fail = True
                    break
                else:
                    fail = False
    else:
        response = None
        while response not in valid_responses_lst:
            response = input(input_msg)
    return response

def single_column_grouping(data, column):
    categories = []
    rows_grouped = 0
    index = data[0].index(column)
    for row in data[1:]:
        if row[index] not in categories:
            categories.append(row[index])
    #categories.insert(0, "0")
    categories_to_grp = ensure_valid_response("\nPlease specify categories to group. \n" + '\n'.join(categories) + "\n", categories, "list")
    new_category = input("\nPlease specify a name for the new category (any name besides 0). Or press 0 to exit grouping function ")
    if new_category == "0":
        return data
    for row in data[1:]:
        if row[index] in categories_to_grp:
            rows_grouped += 1
            row[index] = new_category
    print(str(rows_grouped) + " rows were renamed under new category name.")
    return data

def multiple_column_grouping(data, columns):
    def new_category_column(new_category, indexes, combi): #combi: Eg. [Bus, 0, 0]
        for row in data[1:]:
            match = True
            for i in indexes:
                if row[i] != combi[indexes.index(i)]:
                    match = False
                    break
            if match:
                row.append(new_category)


    categories = []     # list of all the combinations in specified columns. For eg: [[Bus, 0, 0],[0, MRT, 0],[0, 0, Taxi]]    
    indexes = []   # indexes of specified columns by user in dataset 
    for col in columns:
        indexes.append(data[0].index(col))
    for row in data[1:]:
        combi = []
        for i in indexes:
            combi.append(row[i])
        if combi not in categories:
            categories.append(combi)
    for combi in categories:
        print("\nPlease specify a new category name for records where Columns \"" + '", "'.join(columns) + "\" have values of \"" + '", "'.join(combi) + "\" respectively.")
        new_category = input()
        new_category_column(new_category, indexes, combi)
    p = re.compile('^[\S]*$')
    new_col_name = " "
    while p.fullmatch(new_col_name) == None:
        new_col_name = input("\nColumns have been combined. Please input a column name for the combined column. Ensure that you do not include whitespace within the column name. ")
    data[0].append(new_col_name)
    return data

def option2_group(data, field_lst):
    groups_to_filter = ensure_valid_response("\nPlease specify column(s) to apply grouping on: \n" + '\n'.join(field_lst[1:]) + "\n\n Or press 0 to exit grouping function. ", field_lst, "list")
    if groups_to_filter == ["0"]:
        return data
    elif len(groups_to_filter) == 1:
        data = single_column_grouping(data, groups_to_filter[0])
    else:
        data = multiple_column_grouping(data, groups_to_filter)
    return data