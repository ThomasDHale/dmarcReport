# import required modules
from datetime import datetime
from bs4 import BeautifulSoup
from zipfile import ZipFile
import gzip as gzip
import shutil as shutil
import pandas as pd
import glob as glob
import os as os

# No limit on number of rows to display
pd.set_option('display.max_rows', None)

def decompressXml(inputDirectory):
  
  # Use glob to find .gz files in the input directory
  gzFiles = glob.glob(inputDirectory+"*.gz")
  print(datetime.now(),"Found", len(gzFiles), "gzipped xml files in directory:", inputDirectory)

  # Decompress each file
  for gzFile in gzFiles:
    print(datetime.now(),gzFile)
    with gzip.open(gzFile, 'rb') as f_in:
      gz_content = f_in.read()
      f_out = open(gzFile+".xml", "w")
      f_out.write(bytes.decode(gz_content))
      print(datetime.now(),"Extracted",gzFile,"to",gzFile+".xml")
      f_out.close()
  print(datetime.now(),"Finished extracting gzip files\n")

  # Use glob to find .zip files in the input directory
  zipFiles = glob.glob(inputDirectory+"*.zip")
  print(datetime.now(),"Found", len(zipFiles), "zipped xml files in directory:", inputDirectory)

  # Decompress each file
  for zipFile in zipFiles:
    print(datetime.now(),zipFile)
    with ZipFile(zipFile) as f_in:
      f_in.extractall(path=inputDirectory)
      print(datetime.now(),"Extracted",zipFile,"to",inputDirectory)

def xml2table(inputDirectory, outputDirectory):

  # create a list of all the xml files in the directory
  xmlFiles = glob.glob(inputDirectory+"*.xml")
  print(datetime.now(),"We are using",inputDirectory)

  for xmlFile in xmlFiles:

    # reading content
    input_file = open(xmlFile, "r")
    contents = input_file.read()
    print(datetime.now(),"Opened:",xmlFile)

    # create a new variable called soup containing the contents of the xml file
    soup_allcontents = BeautifulSoup(contents, 'xml')

    # find report metadata
    soup_metadata = soup_allcontents.find_all('report_metadata')
    for metadata in soup_metadata:
      soup_orgname = metadata.find('org_name')
      soup_email = metadata.find('email')
      soup_contact = metadata.find('extra_contact_info')
      soup_reportid = metadata.find('report_id')
      soup_startdate = metadata.find('begin')
      soup_enddate = metadata.find('end')
      var_start = datetime.fromtimestamp(int(soup_startdate.text))
      var_end = datetime.fromtimestamp(int(soup_enddate.text))
      print(datetime.now(),"Extracted metadata")

    # find published policy data
    soup_policy = soup_allcontents.find_all('policy_published')
    for policy in soup_policy:
      soup_domain = policy.find('domain')
      print(datetime.now(),"Extracted policy")

    # find each instance of a row and create a new variable called to store them
    soup_rows = soup_allcontents.find_all('row')
    print(datetime.now(),"Extracted rows")

    # set up a dictionary called data and a list called columns
    dict_data = {'source_ip':[], 'dkim':[], 'spf':[]}
    print(datetime.now(),"Created dictionary to hold data")

    dict_cols = ['source_ip', 'dkim', 'spf']

    # set up a dictionary for the metadata
    dict_metadata = {'Domain':[soup_domain.text], 'Organisation Name':[soup_orgname.text], 'Email Address':[soup_email.text], 'Report ID':[soup_reportid.text], 'From':[var_start], 'To':[var_end]}

    # set n to 0. used to loop through each column in the cols list
    n = 0

    # add content into data dictionary
    for item in soup_rows:
      for column in dict_cols:
        i = item.find(dict_cols[n])
        dict_data[dict_cols[n]].append(i.text)
        n = n+1
      # set n to 0
      n = 0
    print(datetime.now(),"Added data to dictionary")

    # count the number of SPF failures and DKIM failures
    soup_spfFailures = str((dict_data['spf'].count('fail')))
    print(datetime.now(),"Counted number of SPF failures")
    soup_dkimFailures = str((dict_data['dkim'].count('fail')))
    print(datetime.now(),"Counted number of DKIM failures")

    # set up a dictionary for total failures
    dict_failures = {'SPF Failures':[soup_spfFailures],'DKIM Failures':[soup_dkimFailures]}
    
    # build the dataframe from the data dictionary
    df_metadata = pd.DataFrame(dict_metadata).T
    df_failures = pd.DataFrame(dict_failures).T
    df_data = pd.DataFrame(dict_data)
    print(datetime.now(),"Create dataframes")
    
    # create a file with the reportid
    output_name = (soup_orgname.text+"!"+soup_domain.text+"!"+soup_reportid.text)
    output_file = (outputDirectory+output_name+".txt")
    output_file_csv_data = (outputDirectory+output_name+".csv")
    
    # print out the report metadata to an external file with name defined above
    f = open(output_file, "w")
    print(datetime.now(),"Opened output file",output_file)
    f.write(df_metadata.to_string(header=False))
    print(datetime.now(),"Added metadata to output text file")
    f.write("\n\n")
    f.write(df_failures.to_string(header=False))
    print(datetime.now(),"Added failures to output text file")
    f.write("\n\n")
    f.write(df_data.to_string())
    print(datetime.now(),"Added data to output text file")
    f.close()
    print(datetime.now(),"Closed output file",output_file)
    
    # output the data to a csv file
    f = open(output_file_csv_data, "w")
    print(datetime.now(),"Opened csv file",output_file_csv_data)
    f.write(df_data.to_csv(index=False))
    print(datetime.now(),"Wrote data to csv file")
    f.close()
    print(datetime.now(),"Closed csv file",output_file_csv_data)
    
    print(datetime.now(),"Finished processing",xmlFile,"\n")
