import numpy as np
import pandas as pd
import openpyxl
import csv
zipcodes= pd.read_excel("ZipCode_NYC.xlsx")

zipcodes= zipcodes.dropna()
zipcodes= zipcodes.drop_duplicates()
zipcodes.to_csv("zipcode_income.csv", index=False)
crimedata= pd.read_excel("NYPD_Complaint_Data_Current_(Year_To_Date)_20251202.xlsx", engine="openpyxl")
Description= crimedata.drop(['CMPLNT_NUM','ADDR_PCT_CD','HADEVELOPT','CRM_ATPT_CPTD_CD','STATION_NAME','PARKS_NM','TRANSIT_DISTRICT'],axis=1)
Description= Description.reset_index()
Description['CMPLNT_FR_DT']= pd.to_datetime(Description['CMPLNT_FR_DT'], errors='coerce')
Description['CMPLNT_TO_DT']= pd.to_datetime(Description['CMPLNT_TO_DT'],errors='coerce')
Description['RPT_DT']= pd.to_datetime(Description['RPT_DT'],errors='coerce')

Description= Description[Description['CMPLNT_FR_DT'].dt.year == 2025]
Description= Description[Description['CMPLNT_TO_DT'].dt.year == 2025]
Description= Description[Description['RPT_DT'].dt.year == 2025]
Description.to_csv("crime_data.csv", index=False)
