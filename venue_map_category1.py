# Running Config: Chicago 1182815 CH_venues_experimental.json output_merged.json  review_dump_unique_sorted.json apikeys.txt

import json
import os
import sys
import re
import requests
from math import radians, cos, sin, asin, sqrt
from difflib import SequenceMatcher
from termcolor import colored


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


api_filename = ''
api_filename_ptr = 0
api_list = []
api_fetch_call = 0


def similar(a, b):
    return SequenceMatcher(None, a, b).ratio()


def authenticate_client(client_id, client_secret):
    payload = {}

    payload = {'grant_type': 'client_credentials', 'client_id': client_id, 'client_secret': client_secret}
    try:
        r = requests.post("https://api.yelp.com/oauth2/token", data=payload)
    except:
        print("Oops!", sys.exc_info()[0], "occured.")
        return 0
    else:
        print(r.text)
        json_output = r.json()

        return json_output["access_token"]


def populate_api_list():
    global api_filename
    global api_list
    fh = open(api_filename, 'r')
    for line in fh.readlines():
        line = line.strip()
        client_tuple = line.split(" ")
        api_list.append(client_tuple)


def authenticate_client_with_api_list():
    global api_list
    global api_filename_ptr
    client_id = api_list[api_filename_ptr][0]
    client_secret = api_list[api_filename_ptr][1]
    if api_filename_ptr == 2:
        api_filename_ptr = 0
    else:
        api_filename_ptr += 1
    yelp_client = 0
    while yelp_client == 0:
        yelp_client = authenticate_client(client_id, client_secret)
    return yelp_client


def find_by_phone_api(phone, yelp_client):
    global api_fetch_call
    if phone[0:1] != '+1':
        phone = '+1' + phone
    # print(phone)
    url = 'https://api.yelp.com/v3/businesses/search/phone?phone='
    url = url + phone
    # print(url)
    br = 'Bearer ' + yelp_client
    headers = {'Authorization': br}
    try:
        r = requests.get(url, headers=headers)
        api_fetch_call += 1
    except:
        print("Oops!", sys.exc_info()[0], "occured.")
    else:
        # print(r.text)
        json_output = r.json()
        if not 'error' in json_output:

            name = json_output['businesses'][0]['name']
            yelp_id = json_output['businesses'][0]['id']
            yelp_category=json_output['businesses'][0]['categories']

            return name, yelp_id,yelp_category
        else:
            return 0, 0,0





def extract_meetup_data(json_string):
    lat, lon, zip = 0, 0, 0
    phone, name, meetup_id = '', '', ''
    if 'lat' in json_string:
        lat = json_string["lat"]
    if 'lon' in json_string:
        lon = json_string["lon"]
    if 'phone' in json_string:
        phone = json_string["phone"]
        phone = re.sub('[^0-9+]+', '', phone)
        # print(str(phone))
    if 'zip' in json_string:
        zip = json_string["zip"]
    if 'id' in json_string:
        meetup_id = json_string["id"]
    if 'name' in json_string:
        name = json_string["name"]
    return name, meetup_id, phone, lat, lon


def check_file_exist(filename):
    retval = False
    if os.path.isfile(filename) == True:
        # print(str(filename) + 'File Already Exist')
        retval = True
    return retval


def extract_phone_number(yelp_file, phone):
    yelp_file_fh = open(yelp_file, 'r')
    print(str(phone))
    yelp_name = ""
    yelp_id = ""
    categories=""
    for yelp_lines in yelp_file_fh.readlines():
        phone_start_loc = yelp_lines.find('"phone": "')
        phone_strip = yelp_lines[phone_start_loc + 10:]
        phone_end_loc = phone_strip.find('"')
        yelp_phone = phone_strip[:phone_end_loc]

        if str(phone) in yelp_phone:
            print(colored('Found Phone Number', 'green'))
            yelp_lines = str(yelp_lines).strip()
            yelp_lines = str(yelp_lines).strip(',')
            json_data = json.loads(yelp_lines)
            if 'name' in json_data['businesses'][0]:
                yelp_name = json_data['businesses'][0]['name']
            if 'id' in json_data['businesses'][0]:
                yelp_id = json_data['businesses'][0]['id']
            if 'categories' in json_data['businesses'][0]:
                categories = json_data['businesses'][0]['categories']
            return yelp_id, yelp_name,categories

    return 0, 0,0


def find_by_name_pattern(name, lat, lon, yelp_file):
    yelp_file_fh = open(yelp_file, 'r')
    for yelp_lines in yelp_file_fh.readlines():
        name_start_loc = yelp_lines.find('"name":')
        name_strip = yelp_lines[name_start_loc + 9:]
        name_end_loc = name_strip.find('",')
        yelp_name = name_strip[:name_end_loc]

        id_start_loc = yelp_lines.find('"id":')
        id_strip = yelp_lines[id_start_loc + 7:]
        id_end_loc = id_strip.find('",')
        yelp_id = id_strip[:id_end_loc]
        print(yelp_id)

        latitude_start_loc = yelp_lines.find('"latitude": ')
        latitude_strip = yelp_lines[latitude_start_loc + 12:]
        latitude_end_loc = latitude_strip.find(', "longitude"')
        yelp_latitude = latitude_strip[:latitude_end_loc]

        longitude_start_loc = yelp_lines.find('"longitude": ')
        longitude_strip = yelp_lines[longitude_start_loc + 12:]
        longitude_end_loc = longitude_strip.find('},')
        yelp_longitude = longitude_strip[:longitude_end_loc]

        if similar(name, yelp_name) > .6 and calculate_distance_between_loc(float(lon), float(lat),
                                                                             float(yelp_longitude),
                                                                             float(yelp_latitude)) < 1:
            print(colored('Names are matching', 'green'))
            print(colored(name + ' ', 'blue'))#, end='')
            print(colored(yelp_name, 'blue'))
            return yelp_name, yelp_id
        elif similar(name, yelp_name) > .33 and calculate_distance_between_loc(float(lon), float(lat),
                                                                               float(yelp_longitude),
                                                                               float(yelp_latitude)) < .7:
            print(colored('Names are matching', 'green'))
            print(colored(name + ' ', 'blue'))#, end='')
            print(colored(yelp_name, 'blue'))
            return yelp_name, yelp_id
        else:
            return 0, 0


def calculate_distance_between_loc(lon1, lat1, lon2, lat2):
    # convert decimal degrees to radians

    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * asin(sqrt(a))
    r = 6371  # Radius of earth in kilometers. Use 3956 for miles
    return c * r


def find_by_name_api(name, yelp_client, lat, lon):
    url = 'https://api.yelp.com/v3/businesses/search?location=Chicago&limit=10&term='

    url = url + name
    # print(url)
    br = 'Bearer ' + yelp_client
    headers = {'Authorization': br}
    try:
        r = requests.get(url, headers=headers)
        # api_fetch_call += 1
    except:
        print("Oops!", sys.exc_info()[0], "occured.")
    else:
        print(name)
        print(r.text)
        json_output = r.json()
        if not 'error' in json_output:

            total = r.text.count('"id"')
            min_distance = 0
            nearest_loc_lat = ''
            nearest_loc_lon = ''
            nearest_loc_name = ''
            nearest_loc_id = ''
            distance = -1
            categories=""
            if int(total) > 0:
                for a in range(0, total):
                    yelp_name = json_output['businesses'][a]['name']
                    yelp_id = json_output['businesses'][a]['id']
                    yelp_lat = json_output['businesses'][a]['coordinates']['latitude']
                    yelp_lon = json_output['businesses'][a]['coordinates']['longitude']
                    if yelp_lat != None and yelp_lon != None:
                        # print('INdex-->'+str(a)+'Total-->'+str(total)+' Name-->'+str(name)+' Yelp Id-->'+str(yelp_id))
                        distance = calculate_distance_between_loc(float(lon), float(lat), float(yelp_lon),
                                                                  float(yelp_lat))
                    if (similar(name, yelp_name) > 0.6 or name in yelp_name) and distance < 2 and distance >= 0:
                        if min_distance == 0:
                            min_distance = distance
                            nearest_loc_lat = yelp_lat
                            nearest_loc_lon = yelp_lon
                            nearest_loc_name = yelp_name
                            nearest_loc_id = yelp_id
                            categories=json_output['businesses'][a]['categories']
                        elif distance < min_distance:
                            min_distance = distance
                            nearest_loc_lat = yelp_lat
                            nearest_loc_lon = yelp_lon
                            nearest_loc_name = yelp_name
                            nearest_loc_id = yelp_id
                            categories = json_output['businesses'][a]['categories']

                print('Best Match-->' + colored(nearest_loc_name, 'red'))

                if len(nearest_loc_id) > 0 and len(nearest_loc_name) > 0:
                    return nearest_loc_name, nearest_loc_id,categories
                else:
                    return 0, 0,0
            else:
                return 0, 0,0


def write_yelp_meet_tofile(meetup_id, yelp_id, yelp_name):
    fh = open('Meetup_yelp_mapping.txt', 'a+')
    out_string = str(meetup_id) + ' ' + str(yelp_id) + ' ' + str(yelp_name)
    # print(out_string)
    fh.write(out_string)
    fh.write('\n')
    fh.close()


def search_reviews_from_dataset(yelp_id, yelp_name, yelp_complete_review_dataset):
    yelp_review_dataset_fh = open(yelp_complete_review_dataset, 'r')
    reviews = []
    for review_lines in yelp_review_dataset_fh.readlines():
        if str(yelp_id) in review_lines:
            json_data = json.loads(review_lines)
            print(str(json_data))
            total_reviews = int(json_data['3reviews'][0]['total'])
            for a in range(0, total_reviews):
                review = json_data['3reviews'][0]['reviews'][a]['text']
                review = str(review).strip()
                if len(review) > 5 and review not in reviews:
                    reviews.append(review)

    if len(reviews)<1:
        print('Review Search from API')
        yelp_client = authenticate_client_with_api_list()
        br = 'Bearer ' + yelp_client
        headers = {'Authorization': br}
        business_id = yelp_id
        url = 'https://api.yelp.com/v3/businesses/' + str(business_id) + '/reviews'
        try:
            r = requests.get(url, headers=headers)
            print(r.text)
        except requests.exceptions.ConnectionError:
            print("requests.exceptions.ConnectionError")

            print(r.text)
        except:
            print("Oops!", sys.exc_info()[0], "occured.")
            print(r.text)
        else:

            try:

                json_output = json.loads(r.text.strip())
                total_reviews = int(json_output['total'])
            except:
                print("Oops!", sys.exc_info()[0], "occured.")
                print(r.text)
            else:

                for a in range(0, total_reviews):
                    review = json_output['reviews'][a]['text']
                    review = str(review).strip()
                    if len(review) > 5 and review not in reviews:
                        reviews.append(review)
    return reviews


def map_meetup_yelp_data(city, meetup_id_for_search, meetup_file_name, yelp_completed_business_dataset,
                         yelp_complete_review_dataset):
    yelp_client = authenticate_client_with_api_list()
    meetup_id_for_search = int(meetup_id_for_search.strip())
    with open(meetup_file_name) as data_file:
        data = json.load(data_file)
        meetup_dataset_rows = len(data)
        reviews = []
        for a in range(0, meetup_dataset_rows):
            yelp_name, yelp_id = 0, 0
            yelp_categories=""
            if data[a]["city"] == city:
                name, meetup_id, phone, lat, lon = extract_meetup_data(data[a])
                if meetup_id == meetup_id_for_search:
                    print('Meetup Data Found')
                    print(name)
                    Match = False
                    if len(phone) > 4 and yelp_name == 0 and yelp_id == 0 and Match == False:
                        print('Phone Match from API')
                        yelp_name, yelp_id,yelp_categories = find_by_phone_api(phone, yelp_client)

                        if yelp_name != 0 and yelp_id != 0:
                            print(yelp_name)
                            write_yelp_meet_tofile(meetup_id, yelp_id, yelp_name)
                            reviews = search_reviews_from_dataset(yelp_id, yelp_name, yelp_complete_review_dataset)
                            Match = True
                            return yelp_id, yelp_name,yelp_categories, reviews
                    if len(name) > 0 and yelp_name == 0 and yelp_id == 0 and Match == False:
                        print('Name Match from API')
                        yelp_name, yelp_id,yelp_categories = find_by_name_api(name, yelp_client, lat, lon)

                        if yelp_name != 0 and yelp_id != 0:
                            print(yelp_name)
                            write_yelp_meet_tofile(meetup_id, yelp_id, yelp_name)
                            reviews = search_reviews_from_dataset(yelp_id, yelp_name, yelp_complete_review_dataset)
                            Match = True
                            return yelp_id, yelp_name,yelp_categories, reviews
                    if len(name) > 0 and yelp_name == 0 and yelp_id == 0 and Match == False:
                        print('Name Match from Dataset')
                        yelp_file = './output/output_lat_' + str(lat) + 'long_' + str(lon) + '.json'
                        if check_file_exist(yelp_file) == True:
                            yelp_name, yelp_id,yelp_categories = find_by_name_pattern(name, lat, lon, yelp_file)

                        if yelp_name != 0 and yelp_id != 0:
                            print(yelp_name)
                            write_yelp_meet_tofile(meetup_id, yelp_id, yelp_name)
                            reviews = search_reviews_from_dataset(yelp_id, yelp_name, yelp_complete_review_dataset)
                            Match = True
                            return yelp_id, yelp_name, yelp_categories,reviews

                    if yelp_name == 0 and yelp_id == 0 and len(phone) > 4 and Match == False:
                        print('You are in Phone Search from Database')
                        yelp_id, yelp_name,yelp_categories = extract_phone_number(yelp_completed_business_dataset, phone)
                        if yelp_name != 0 and yelp_id != 0:
                            print(yelp_name)
                            write_yelp_meet_tofile(meetup_id, yelp_id, yelp_name)
                            reviews = search_reviews_from_dataset(yelp_id, yelp_name, yelp_complete_review_dataset)
                            Match = True
                            return yelp_id, yelp_name,yelp_categories, reviews

        return '0', '0','0', []


def main1(arg_list):
    city = str(arg_list[0])
    meetup_id_for_search = str(arg_list[1])
    meetup_file_name = str(arg_list[2])
    yelp_completed_business_dataset = str(arg_list[3])
    yelp_complete_review_dataset = str(arg_list[4])
    global api_filename
    api_filename = str(arg_list[5])
    populate_api_list()
    yelp_id, yelp_name,yelp_categories, reviews = map_meetup_yelp_data(city, meetup_id_for_search, meetup_file_name,
                                                       yelp_completed_business_dataset,
                                                       yelp_complete_review_dataset)

    #print(yelp_id + ' ' + yelp_name + ' ' + str(yelp_categories) + ' '+ str(reviews))
    return yelp_id, yelp_categories,reviews

#if __name__ == '__main__': main()
