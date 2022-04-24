import pandas as pd
import geopandas as gpd
import geopy
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import requests
import json
import io
import csv
import os

##### SET DEFAULT DATES ####
from datetime import date, timedelta, datetime
today = date.today()
end_date_def = int(today.strftime("%Y%m%d")) #Set the end date for search to today
before = today - timedelta(days=365*1)
start_date_def = int(before.strftime("%Y%m%d")) #Set the search to begin 1 year ago

##### SET AWS PERMISSIONS ####
#Files can be uploaded to the AWS bucket I created: address-weather-csvs
import boto3
from botocore.exceptions import NoCredentialsError
#These can be downloaded from AWS under aws.amazon.com/iam/home#/security_credentials
#Import them from a csv so they're only stored locally and not in the file
#YOU WILL NEED TO ADD YOUR OWN ACCESS KEYS
credentials = pd.read_csv('/Users/mborrus/Benchmark/AWS/Marshall_accessKeys.csv');
ACCESS_KEY = str(credentials['Access key ID'][0])
SECRET_KEY = str(credentials['Secret access key'][0])

def CSV_to_latlon(file_path,header_name):
    '''
    This creates a latlon column for based on the address in your csv
    Must provide the file name and the header of the address column
    '''
    Address_Info = pd.read_csv(file_path)
    geolocator = Nominatim(user_agent="AdressToLat")
    geocode = RateLimiter(geolocator.geocode, min_delay_seconds = 1)
    Address_Info['geo_location'] = Address_Info[header_name].apply(geocode)
    return(Address_Info)

def Login(username,password):
    '''
    This logs you into the API and returns the auth key
    '''

    url = "https://api-dev.benchmarklabs.com:443/api/v1/2a6997a7-a9a2-4b2e-b87a-656d6e85cbaf/authentication/login"

    payload = json.dumps({
      "username": username,
      "password": password,
      "deviceId": "deviceId"
    })
    headers = {
      'Content-Type': 'application/json',
      'Cookie': 'JSESSIONID=7DD8740820BC48680E3175B686BD2589' #Does the cookie ever need to change?
    }

    #Convert response file into text and then into a json format
    response_login = requests.request("POST", url, headers=headers, data=payload)
    response_login = json.loads(response_login.text)
    Auth_Key = str(response_login['token']); #This pulls just the bearer token
    return(Auth_Key)

def Get_Data(Auth_Key, lat, lon, radius=10, stations=1, start_date=start_date_def, end_date=end_date_def, elem = ["TMIN","TMAX","PRCP"]):
    '''
    This returns the response from the API for any given radius, # of stations, date range, and lat/lon
    The defaults are a 10 mile radius with 1 station for 1 the previous year. I'll hope to add elements
    as an option as well.
    '''
    url = "https://api-dev.benchmarklabs.com:443/api/v1/2a6997a7-a9a2-4b2e-b87a-656d6e85cbaf/ghcnd/data"

    payload = json.dumps({
      "latitude": lat, #The latitude you're interested in
      "longitude": lon, #The longitude you're interested in
      "radius": radius, #How far of a radius to draw when searching for other stations
      "stations": stations, #Take the closest N stations
      "dateFrom": start_date, #Start date YYYY/MM/DD
      "dateTo": end_date, #End date YYYY/MM/DD
      "elements": elem, #https://docs.opendata.aws/noaa-ghcn-pds/readme.html
      "format": "csv"
    })
    headers = {
      'Authorization': 'Bearer ' + Auth_Key,
      'Content-Type': 'application/json',
      'Cookie': 'JSESSIONID=7DD8740820BC48680E3175B686BD2589'
    }

    response_ghcnd = requests.request("POST", url, headers=headers, data=payload, timeout=300)
    return(response_ghcnd)

def CSV_to_DF(Response_Data):
    '''
    translating the csv response to a pandas dataframe
    '''
    string = Response_Data.text #Take the text from the csv resonse
    Output = pd.read_csv(io.StringIO(string), sep=',', header=[0], quoting=csv.QUOTE_ALL) #Seperate the text file, using StringIO to make it a file
    pd.set_option('display.max_rows', 10) #This just makes it pretty
    #display(Output)
    return(Output)

def upload_to_aws(local_file, bucket, s3_file):
    '''
    Upload your file to a specific bucket with a specific name (s3_file)
    '''
    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY)

    try:
        s3.upload_file(local_file, bucket, s3_file)
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False

##### RETRIEVE WEATHER DATA FOR ADDRESSES ####
Address_File = input("Address_File Path (ex: 'TestAddresses.csv'): ")
Address_Header = input("Address Header (ex: 'Address'): ")
Local_Save_Path = input("Where to store csv files locally (ex: '/Output_CSVs/Dom/'): ")
#Local_Save_Path = '/Users/mborrus/Benchmark/Jupyter/Output_CSVs/Dom/'
AWS_Save_Path = input("Where to save within AWS bucket (ex: 'Domestic'): ")
#AWS_Save_Path = 'Domestic_Test'
Save_File_Name_Column = 'Landmark'

if not os.path.isdir(Local_Save_Path):
    os.mkdir(Local_Save_Path)

Address_Info = CSV_to_latlon(Address_File,Address_Header)
for addy in Address_Info.index:
    test_key = Login("superadmin","VrYAK#2Kfe") #Log in as super admin
    test_output = Get_Data(test_key,Address_Info['geo_location'].loc[addy].latitude,Address_Info['geo_location'].loc[addy].longitude, stations = 3) #Get data from first address
    output = CSV_to_DF(test_output); #Save the data as a dataframe and display the data
    Filename = str(Local_Save_Path + Address_Info[Save_File_Name_Column][addy] +'.csv')
    output.to_csv(Filename, index=None)
    print(addy)
    print(Address_Info['Landmark'][addy])
    print('Latitude for the index =', (Address_Info['geo_location'].loc[addy].latitude , Address_Info['geo_location'].loc[addy].longitude))
    uploaded = upload_to_aws(Filename, 'address-weather-csvs', str(AWS_Save_Path+'/'+Address_Info[Save_File_Name_Column][addy]+'.csv'))
