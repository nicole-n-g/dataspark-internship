import re         

def filter_NAs(data, field_name):
    data_headings = data[0]
    for heading in data_headings:
        if heading == field_name:
            index = data_headings.index(heading)
            p = re.compile('[\s]*')
            for record in data[1:]:
                if p.fullmatch(record[index]) or record[index].lower() == "na" or record[index].lower() == "nil" or record[index]=="-":
                    data.remove(record)
    return data

def ensure_valid_response(input_msg, valid_responses_lst, input_is_lst = None):
    if input_is_lst == "list":
        fail = True
        while fail:
            response = input(input_msg).split()
            for r in response:
                if r not in valid_responses_lst:
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

def option3_filter(data, field_lst):
    
    def filter_category(data, field, category, include_exclude, part_data = None):   #field & category are lists of same length        
        def match(row, field_indexes, category):
            for i in range(len(field_indexes)):
                if (category[i].startswith('"') and category[i].endswith('"')) or (category[i].startswith("'") and category[i].endswith("'")):
                    category[i] = category[i][1:-1]
                if row[field_indexes[i]] != category[i]:
                    return False
            return True
        
        final_data = data[1:]
        field_indexes = []
        for i in range(len(field)):
            index = data[0].index(field[i])
            field_indexes.append(index)
        if include_exclude =="1":
            final_data = list(filter(lambda x: match(x, field_indexes, category), final_data))
            part_data.extend(final_data)
            final_data = part_data
        elif include_exclude =="2":
            final_data = list(filter(lambda x: not match(x, field_indexes, category), final_data))
            final_data = [data[0],] + final_data
        return final_data

    
    filter_option = ensure_valid_response("\nPlease select a filter option: \n 1. Exclude blanks, NAs and NILs \n 2. Filter based on categories \n Press 0 to exit filter function. ", ["0", "1", "2"])
        
    if filter_option == "1":
        field_to_filter = ensure_valid_response("\nPlease specify a column to filter out blanks, NAs and NILs from: \n" + '\n'.join(field_lst[1:]) + "\n\n Press 0 to exit filter function. ", field_lst)
        if field_to_filter == "0":
            return data
        data = filter_NAs(data, field_to_filter)

    elif filter_option == "2":
        fields_to_filter = ensure_valid_response("\nPlease specify column(s) to apply categorical filter on: \n" + '\n'.join(field_lst[1:]) + "\n\n Press 0 to exit filter function. ", field_lst, "list")
        if fields_to_filter == ["0"]:
            return data
        include_exclude = ensure_valid_response("\n1. Include specific categories or 2. Exclude specific categories? ", ["1", "2"])
        categories = []
        row = []
        while len(fields_to_filter) != len(row):
            categories = input("\nKey in the category(s) by row: (Press 0 to exit filter function) ").split(";")
            if categories == ["0"]:
                return data
            cat_lst = []
            for cat in categories:
                row = re.split(''' (?=(?:[^'"]|'[^']*'|"[^"]*")*$)''', cat)
                if len(row) != len(fields_to_filter):
                    break
                cat_lst.append(row)
        if include_exclude == "1":
            part_data = []
            for cat in cat_lst:
                part_data = filter_category(data, fields_to_filter, cat, include_exclude, part_data)
            data = [data[0],] + part_data
        elif include_exclude == "2":
            for cat in cat_lst:
                data = filter_category(data, fields_to_filter, cat, include_exclude)
    return data