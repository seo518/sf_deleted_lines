# coding: utf-8
import pandas as pd
import glob
import os
from salesforce_reporting import Connection, ReportParser
import warnings
from ftplib import FTP, all_errors
from datetime import datetime
warnings.filterwarnings('ignore')
import config

#FTP
ftp_server = config.ftp_server
ftp_user = config.ftp_user
ftp_pw = config.ftp_pw
ftp_path = config.ftp_path
ftp_report_name = config.ftp_report_name

#Salesforce
your_token = config.your_token
your_username = config.your_username
your_password = config.your_password
your_instance = config.your_instance
report_ids = config.report_ids
report_agencies = config.report_agencies
report_id = report_ids[0]
sl_report_path = config.sl_report_path

out_report_path = config.out_report_path

if not(os.path.exists(out_report_path)):
    out_report_path = config.local_default_path
    if not(os.path.exists(out_report_path)):
        os.mkdir(out_report_path)
 
#Get FTP File
ftp_files = list()
try:
    ftp = FTP(host=ftp_server, user=ftp_user, passwd=ftp_pw)
    ftp.cwd(ftp_path)

    #Get list and pick most recent file
    ftp_files = ftp.nlst()
    print("FTP Files found: ", len(ftp_files))
    ftp_files = [x for x in ftp_files if ftp_report_name in x]
    ftp_files.sort(reverse=True)
    
except all_errors:
    print('Unable to access FTP file')

if(len(ftp_files) == 0):
    print("No files in ftp folder")
    ftp_file_flag = False
else:
    ftp_file_flag = True

if ftp_file_flag:
    ftp_file = ftp_files[0]
    sf_file = ftp_file

    #This will write to the cwd
    os.chdir(r'C:\temp')
    ftp.retrbinary('RETR ' + ftp_file, open(ftp_file, 'wb').write)

    #Check if file transfer and then delete
    if(os.path.isfile(ftp_file)):
        ftp.delete(ftp_file)

else:
    sf_file_raw = input("No ftp file found. Enter path to the file or enter to quit: ")
    if not os.path.isfile(sf_file_raw):
        exit()

    sf_file = sf_file_raw

# Read data frame
os.chdir(r'C:\temp')
sl_df = pd.read_csv(sf_file)
agencies = list()
if (len(sl_df)):
    sl_df['Agency'] = sl_df.SF_OPPORTUNITY_NAME.str.split(' ').str.get(0)
    sl_df['Agency'] = sl_df.Agency.str.title()
    agencies = list(sl_df.Agency.unique())
print(len(sl_df), 'records in Spotlight (', len(agencies),' agencies )')
print(sl_df.SF_START_DATE.min(), ' - ', sl_df.SF_END_DATE.max(), '\n')

# Get SF data
sf = Connection(username=your_username, password=your_password, security_token=your_token)
df = pd.DataFrame()
sf_columns = ['ID', 'Agency', 'Stage', 'Type', 'Opportunity' , 'Sell_Line', 'Start', 'End', 'Budget', 'Units']
for idx, report_id in enumerate(report_ids):
    report = sf.get_report(report_id, details=True)
    parser = ReportParser(report)
    records = parser.records()
    tmp_df = pd.DataFrame(records, columns = sf_columns)
    tmp_df['Label'] = report_agencies[idx]
    df = df.append(tmp_df)
    print(report_agencies[idx], ': ', len(tmp_df), ' - ', len(df))
print('Total:', len(df))

# Format data
df.Budget = df.Budget.str.replace('CAD ','')
df.Budget = df.Budget.str.replace('USD ','')
df.Budget = df.Budget.str.replace(',','')
df.Budget = df.Budget.astype(float)
print(len(df), 'records in Salesforce: \n', df.Start.min(), ' - ', df.End.max())
df.to_csv(os.path.join(out_report_path,'SF_Data.csv'),index=False)

sf_fees = df[df.Type == 'FeeOrder']
df = df[df.Type != 'FeeOrder']
print('Fees: ', len(sf_fees), '\nMedia: ', len(df))


# Comparing the 2 data sets
del_sl = sl_df[~sl_df.SF_CAMPAIGN_ID.isin(df.ID)]
not_in_sl = df[~df.ID.isin(sl_df.SF_CAMPAIGN_ID)]
print('Not in Salesforce: ', len(del_sl), '\nNot in SpotLight:', len(not_in_sl))

df['Start_Month'] = pd.to_datetime(df.Start, infer_datetime_format=True).dt.month
df['Sell_Line_Month'] = df.Start_Month.astype(str) + '_' +  df.Sell_Line

del_sl['Start_Month'] = pd.to_datetime(del_sl.SF_START_DATE, infer_datetime_format=True).dt.month
del_sl['Start_Month'] = del_sl.Start_Month.astype(int)
del_sl['Sell_Line_Month'] = del_sl.Start_Month.astype(str) + '_' +  del_sl.SF_NETWORK_PLACEMENT_NAME

use_cols = ['Agency', 'SF_CAMPAIGN_ID', 'ID', 'SF_OPPORTUNITY_NAME', 'SF_NETWORK_PLACEMENT_NAME', 'SF_START_DATE']
name_change_df = del_sl.merge(df[['ID', 'Sell_Line_Month']], on='Sell_Line_Month')
name_change_df = name_change_df[name_change_df.SF_CAMPAIGN_ID != name_change_df.ID][use_cols]


name_change_df.columns = ['Agency' , 'Deleted_ID', 'New_ID', 'SF Opportunity', 'SF_Network_Placement_Name',
       'SF_Start_Date']

del_sl = del_sl[['Agency','SF_CAMPAIGN_ID', 'SF_OPPORTUNITY_NAME', 'SF_NETWORK_PLACEMENT_NAME',
       'SF_START_DATE', 'SF_END_DATE', 'Budget', 'IO Booked Units',
       'Impressions']]

#Try to remove old files
print("--- Saving Output Files ---")
os.chdir(out_report_path)
tcnt = 0
for x in os.listdir(out_report_path):
    if 'SF Sync' in x:
        try:
            os.remove(x)
            tcnt += 1
        except OSError:
            pass
print("Cleaning: ", str(tcnt), ' files deleted')

# Testing SF_DELETEME
ford_sl_file = r'C:\temp\SF_DELETEME.csv'
ford_del_sf = del_sl[del_sl.SF_OPPORTUNITY_NAME.str.contains("Ford")][['SF_CAMPAIGN_ID']]
ford_del_sf.SF_CAMPAIGN_ID.to_csv(ford_sl_file,index=False, header=True)

with open(ford_sl_file,'rb') as f:
    ftp.cwd(r'/Spotlight/Ford/SF_DELETEME')
    ftp.storbinary('STOR SF_DELETEME.csv', f)
    ftp.cwd(r'/')
    ftp.cwd(ftp_path)
    print("SF_DELETEME sent to ftp: ", str(len(ford_del_sf)-1), " IDs to be deleted")


# Create a Pandas Excel writer using XlsxWriter as the engine.
for ag in agencies:
    tcnt = list() 
    tcnt.append(len(del_sl[del_sl.Agency == ag]))
    tcnt.append(len(not_in_sl[not_in_sl.Agency == ag]))
    tcnt.append(len(name_change_df[name_change_df.Agency == ag]))
    tstr = str(tcnt).replace(', ','-') + ' '
    output_filename = tstr + ag + ' - SF Sync' + '_' + datetime.now().isoformat().replace(':','') + '.xlsx'
    writer = pd.ExcelWriter(output_filename, engine='xlsxwriter')
    del_sl[del_sl.Agency == ag].to_excel(writer,'Spotlight', index=False)
    not_in_sl[not_in_sl.Agency == ag].to_excel(writer,'Salesforce', index=False)
    name_change_df[name_change_df.Agency == ag].to_excel(writer, 'Changed', index=False)
    writer.save()
    print(output_filename + ' saved')

if ftp_file_flag:
    #Check if file transfer and then delete
    try:
        ftp.delete(ftp_file)
    except:
        pass

print(out_report_path)
