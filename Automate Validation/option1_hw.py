import re
from bs4 import BeautifulSoup
from urllib.request import urlopen, build_opener
from time import sleep # be nice
import csv
import os
import geocoder
import sys

def split_string(string, delimiter):
	return list(map(lambda x: x.strip(), string.split(delimiter)))

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

#######################################################################
#######################################################################

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

#	returns True if postcode is correct format, False otherwise
def check_postcode_format(cell_value):
	p = re.compile("[0-9]?[0-9]{5}")
	if p.fullmatch(cell_value) == None:
		return False
	return True

#	checks validity of manually-matched data, prompts user again if data is not valid
def manually_matched_data(length_of_data_rows): 
	more_rows_yes_no = "y"
	while more_rows_yes_no == "y":
		more_rows_yes_no = ensure_valid_response("\nWould you like to input any manually matched rows back into dataset? (y/n)", ["y", "n"])
		if more_rows_yes_no == "n":
			return None
		more_rows = input("\nEnter the name of the file (.csv) which you would like to combine with the rest of the postal code data. File must be in the same directory as program. (Program assumes that postal codes are in the last column of dataset, and that column headings are included.)")
		if not os.path.isfile(more_rows):
			print("\nFile not found in directory.")
			continue
		#program does not check for format of all data rows again (format may be different original raw data input after application of grouping/filter functions). user responsible for not uploading rubbish files back into system.
		#check each row size & format of values in last column
		more_rows_yes_no = "n"
		data = read_csv(more_rows)
		for row in data[1:]: #data contains header
			if len(row) != length_of_data_rows:
				more_rows_yes_no = "y"
				print ("Row " + str(data.index(row)) + " does not match length of other rows in the rest of the postal code data.")
				break
			elif not check_postcode_format(row[-1]) and row[-1] != " " and row[-1] !="":
				more_rows_yes_no = "y"
				print("Row " + str(data.index(row)) + "'s postal code in the last column is not of the required format. \nRequired format: 6-digit sequence or a blank. \nRow " + str(data.index(row)) + "'s postal code: " + row[-1])
				break
	return data


def split_text_and_code_rows(data, address_column_index, text_format_rows, postcode_format_rows):
	for row in data[1:]:
		if check_postcode_format(row[address_column_index]):
			row.append(row[address_column_index]) #copying postal codes to new column, to combine with postal codes found from text entries later
			postcode_format_rows.append(row)
		else:
			text_format_rows.append(row)

def remove_null_addresses(text_format_rows, address_index):
	p = re.compile('[\s]*')
	for row in text_format_rows:
		if p.fullmatch(row[address_index]) or row[address_index].lower() == "na" or row[address_index].lower() == "nil" or row[address_index] == "-":
			text_format_rows.remove(row)
	return text_format_rows

# 	used in match_text_to_postcode() function
def get_search_terms(row, address_index, district_index): 
	search_terms = []
	location = row[address_index]
	location = location.replace(" ", "+")
	if district_index != None:
		district = row[district_index]
		district = district.replace(" ", "+")
		search_terms.append(location + "+" +district + "+singapore+building+address")
		search_terms.append(location + "+" +district + "+singapore+building")
		search_terms.append(location + "+" +district + "+singapore+address")
		search_terms.append(location + "+" +district + "+singapore")
	search_terms.append(location + "+singapore+building+address")
	search_terms.append(location + "+singapore+building")
	search_terms.append(location + "+singapore+address")
	search_terms.append(location + "+singapore")
	return search_terms

# 	used in match_text_to_postcode() function
def capture_address_box(soup, google_address_box): 
	for cite in soup.findAll("span", {'class': '_m3b'}):
		lst = split_string(cite.text.encode('utf-8').decode('utf-8'), " ")
		google_address_box.extend(lst)
	return google_address_box

# 	used in match_text_to_postcode() function
def capture_info_box(soup, google_info_box): 
	for cite in soup.findAll("span", {'class': '_tA'}):
		lst = split_string(cite.text.encode('utf-8').decode('utf-8'), " ")
		google_info_box.extend(lst)
	return google_info_box

# 	used in match_text_to_postcode() function
#	returns empty string if no valid postcode
def final_postcode(google_box):
	final_lst = []
	for element in google_box:
		if check_postcode_format(element):
			final_lst.append(element)
	final_lst = set(final_lst)
	final_lst = list(final_lst)
	if len(final_lst) == 0:
		return ""
	elif len(final_lst) == 1:
		return final_lst[0]
	else:
		return "Multiple Postal Codes Found:\n" + "\n".join(final_lst)

def match_text_to_postcode(text_format_rows, address_index, district_index=None):
	opener = build_opener()
	opener.addheaders = [('User-agent', 'Mozilla/5.0')]
	for row in text_format_rows:
		google_address_box = [] #stores any addresses captured in the google address box for each search
		google_info_box = [] #stores any addresses (& additional info) captured in the google info box for each search
		search_terms = get_search_terms(row, address_index, district_index)
		for search in search_terms:
			url = "http://www.google.com/search?q=" + search
			print(url)
			while True:
				try:
					page = opener.open(url)
					soup = BeautifulSoup(page, "lxml")
					break
				except:
					print("Encountered error: ", sys.exc_info()[0])
					sleep(0.5)
					continue
			google_address_box = capture_address_box(soup, google_address_box)
			if google_address_box == []:
				google_info_box = capture_info_box(soup, google_info_box)
		sleep(1)
		if google_address_box != []:
			row.append(final_postcode(google_address_box))
		else:
			row.append(final_postcode(google_info_box))
	return text_format_rows

#	takes in a list of text format rows with google-search-derived postcodes in last column,
#	and returns rows where there is null or multiple postcodes
def empty_or_multiple_codes(text_format_rows, converted_text_format_rows):
	final = []
	for row in text_format_rows:
		if not check_postcode_format(row[-1]):
			final.append(row)
		else:
			converted_text_format_rows.append(row)
	return final

#	converts postcode to [latitude, longitude]
def convert_to_latlong(postcode):
	if len(postcode) == 5:
		postcode = "0" + postcode
	g = geocoder.google("Singapore " + postcode)
	max_lat = 1.48
	min_lat = 1.2
	min_long = 103.61
	max_long = 104.08
	if g.latlng == []:
		return convert_to_latlong(postcode)
	elif g.latlng[0] < max_lat and g.latlng[0] > min_lat and g.latlng[1] < max_long and g.latlng[1] > min_long:
		return g.latlng
	else:
		return ["",""]

def option1_addresses(data, field_lst):
	address_columns = ensure_valid_response("\nPlease specify columns for: \n1) building info/addresses \n2) districts (if any)  \n\n" + '\n'.join(field_lst[1:]) + "\n\nOr press 0 to exit transform-address-data function. ", field_lst, "list")
	if address_columns == ["0",]:
		return data
	elif len(address_columns)> 1:
		district_index = data[0].index(address_columns[1]) 
	address_index = data[0].index(address_columns[0])
	text_format_rows = [] #does not include header
	postcode_format_rows = [] #does not include header
	split_text_and_code_rows(data, address_index, text_format_rows, postcode_format_rows)
	# write_csv("text_format_rows.csv", text_format_rows, data[0])
	# write_csv("postcode_format_rows.csv", postcode_format_rows, data[0])
	if text_format_rows != []:
		remove_blanks = ensure_valid_response("\nRemove rows with blanks, NAs and NILs in " + address_columns[0] + " column? (y/n) \nOr press 0 to exit transform-address-data function. ", ["y","n","0"])
		if remove_blanks == "0":
			return data
		elif remove_blanks == "y":
			rows_removed = len(text_format_rows)
			text_format_rows = remove_null_addresses(text_format_rows, address_index)
			rows_removed -= len(text_format_rows)
			print(str(rows_removed) + " row(s) removed.")
			# write_csv("text_format_rows_nonull.csv", text_format_rows, data[0])
	
		print("\nConverting textual building info/addresses into postal codes, as derived from google.com...")
		if len(address_columns)> 1:
			text_format_rows = match_text_to_postcode(text_format_rows, address_index, district_index)
		else:
			text_format_rows = match_text_to_postcode(text_format_rows, address_index)
		#write_csv("text_format_rows_check.csv", text_format_rows, data[0])
		converted_text_format_rows = []
		empty_or_multiplecode_rows = empty_or_multiple_codes(text_format_rows, converted_text_format_rows)
		postcode_format_rows.extend(converted_text_format_rows)

		print("\nFor rows where no postcodes were found, or where multiple postcodes were found: refer to 'No_Single_Postcode_Found.csv'. User may manually match text addresses to postcodes and upload file back into program to continue data processing.")
		write_csv("No_Single_Postcode_Found.csv", empty_or_multiplecode_rows, data[0]+ [address_columns[0] + "_Postal_Codes"])
		#write_csv("All_Postcode_Rows_ForNow.csv", postcode_format_rows, data[0] + [address_columns[0] + ": Postal Codes"])

		mmd = manually_matched_data(len(data[0])+1)
		if mmd != None:
			postcode_format_rows.extend(mmd[1:])

		print("\nAll rows (original postcode rows, text-to-postcode converted rows, and manually converted rows if any) have been combined.")

	
	### convert postcodes to lat long & add latlngs into new columns
	print("\nDeriving latitudes and longitudes for all postcodes...")
	for row in postcode_format_rows:
		if check_postcode_format(row[-1]):
			latlng_lst = convert_to_latlong(row[-1])
			row.extend(latlng_lst)
		else:
			row.extend(["",""])

	print("\n(Rows with blanks, NAs, NILs and erroneous postcodes in the address column will return empty cells for lat-long)")
	header = data[0]+ [address_columns[0] + "_Postal_Codes", address_columns[0] + "_Latitudes", address_columns[0] + "_Longitudes"]
	field_lst.append(address_columns[0] + "_Postal_Codes")
	field_lst.append(address_columns[0] + "_Latitudes")
	field_lst.append(address_columns[0] + "_Longitudes")
	postcode_format_rows.insert(0, header)
	return postcode_format_rows

