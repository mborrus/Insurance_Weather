# Insurance_Weather
Historical weather via addresses 

If we have a list of X addresses, can we automate or run a batch process that uses street addresses to find the closest weather stations, pull their historical data, and export it as CSVs. 
## Quick Start Guide:
1. Clone this repo `git clone ...`
2. Install necessary libaries and packages (see intro of .py file)
3. `python Address_to_Hist_Weather.py`
4. Answer the questions
- Address_File Path: The path to the address csv `./TestAddresses.csv`
- Address Header: The column where the addresses are stored (`Address (google maps)`) 
- Where to store csv files locally: The path to the save folder (`./Output_CSVs/Test/`)
- Where to save within AWS bucket: Name of the folder within the bucket (`Domestic`) 
5. You should see output:
```
0
Salesforce Tower
Latitude for the index = (37.78977435, -122.3969321220982)
Upload Successful
1
Empire State Building
Latitude for the index = (40.7486538125, -73.98530431249999)
Upload Successful
2
San Diego Zoo
Latitude for the index = (32.73788656954161, -117.14883175408295)
Upload Successful
```

## Approach:
Create a list of 10 random addresses in a spreadsheet
Load the addresses into python
Create a function which:
- Translates their position into a lat/lon position
- Put lat/lon position into a Benchmark api call
- Return historical weather station information
- Saves the file as a csv, upload it to AWS
- Write a for loop to go through each address and create a new list with address <> lat lon <> weather station data
- Test international addresses (for Spain)
## Code:
The code was written as a jupyter notebook before being converted to a python script. The notebook can be found on github and can be accessed so long as you’re a member of the Benchmark Labs group: 

## How to Run the Script:
The script is capable of taking a csv file with addresses, finding the latitude and longitude of each address, finding the closest N weather stations within a R sized radius and returning a variety of variables, but predominantly: Tempmax, Tempmin, Precipitation. A complete list of potential variables can be found here: https://docs.opendata.aws/noaa-ghcn-pds/readme.html. The data at some stations can go back numerous decades, but the default is to call 1 year of data from the day it’s called. 

The script will ask for input on the file name, the column header, where you want files saved locally, and where you’d like files saved on AWS. Input examples:
- Address_File Path: The path to the address csv (./TestAddresses.csv)
- Address Header: The column where the addresses are stored (Address): 
- Where to store csv files locally: The path to the save folder (./Output_CSVs/Test/):
- Where to save within AWS bucket: Name of the folder within the bucket (Domestic): 

## Output from Script:
The csv output from each address is stored in its own file, which is saved locally and then uploaded to Benchmark’s AWS S3 storage under the bucket address-weather-csvs. The final folder in which the csvs are saved can be written in the python command.

What is the Global Historical Climatology Network Daily? 
GHCN-Daily is a dataset that contains daily station-based measurements from land-based stations worldwide. The dataset is a composite of climate records (1763 to present) from numerous sources that were merged together and subjected to a common suite of quality assurance reviews. The five core measurements are:
PRCP = Precipitation (tenths of mm - accounts for 2/3rds of the dataset’s data points)
SNOW = Snowfall (mm)
SNWD = Snow depth (mm)
TMAX = Maximum temperature (tenths of degrees C)
TMIN = Minimum temperature (tenths of degrees C)

Benchmark Labs interns have written an API call to pull data based on latitude and longitude.

## Conclusions from this program:
The Address_to_Hist_Weather.py is a simple way to collect large amounts of location specific historical weather data. Decades worth of data can be collected in ~20 seconds for any number of locations globally, so long as an address is provided. The data is then stored on the AWS cloud and can be accessed by the end user at their discretion. 10 years worth of data for 100 addresses only takes up ~40Mb, meaning the weather data remains responsive to analysis with limited compute/storage resources.

## Drawbacks from this program:
### Limited variables and difficult data return:
The API call from Benchmark Labs does not guarantee that you will receive all variables you call for, and most stations only report precipitation data. With a wide enough radius, you can find temperature data, but it remains an open question how common other variables are in the dataset. However, changes to the API call could allow for the better prioritization of returned variables. 
### Long response time:
Most calls take ~20 seconds to return data, independent of date ranges. You can return data for around 120 locations in an hour, meaning it would not make sense to update the dataset daily.
### Difficulty with International Addresses:
Some international addresses (in testing) had abbreviations which the geocoder had difficulty parsing. I have code in the Jupyter Notebook for parsing Spanish addresses, but it will need to be tweaked if we have real examples. 

