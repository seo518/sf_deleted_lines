# Salesforce vs Spotlight Sync
## Used to find deleted lines

#### Requirements

[Salesforce_Reporting](https://pypi.org/project/salesforce-reporting)

	
`pip install salesforce-reporting`


#### Config file

Create a config.py file in the same folder as the code. Please update accordingly with your credentials

**config.py**

~~~

#Salesforce
#These need to be updated per user
your_token = r'paste_salesforce_token_here'
your_username = r'your_email_at_xaxis@xaxis.com'
your_password = r'your_secret_password'

# Salesforce Static
your_instance = 'na49.salesforce.com'
report_ids = ['00O5A000006xDVh', '00O5A000006P86q', '00O5A000006xCd6', '00O5A000006tmE5', '00O5A000006xCdH', '00O5A000006P86v', '00O5A000006xCdG', '00O5A000006xDhY', '00O5A000006tj6D', '00O5A000006tj6I']
report_agencies = ['WAV1', 'WAV2', 'MCM1', 'MCM2', 'MDS1', 'MDS2', 'DIR', 'mSIX', 'Ford FR', 'Ford EN']
sl_report_path = r'C:\Temp'

#Output folder for reports
out_report_path = r'\\Torfpsp01102\xax\Dept\Xaxis\Insights & Analytics\Saleforce\QA'
# If network path is unavailable, it will save files to local_default_path
local_default_path = r'C:\Temp'

#FTP
ftp_server = 'analytics.xaxis.com'
ftp_user = 'ftp_analyticscanada'
ftp_pw = 'Ca125XaX'
ftp_path = r'Spotlight/Salesforce_Sync'
ftp_report_name = 'Salesforce Placement IDs Check Sync'

~~~

#### Spotlight Report needed
Workspace: **Xaxis Overview Superbrand**
Report Name: Salesforce Placement IDs Check Sync - XAXCAN
https://platform.datorama.com/2381/analyze/report/edit?id=111525
