import smtplib
import ssl
import json
import sys
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
from pandas import json_normalize
import pandas as pd
from prettytable import PrettyTable


df = pd.DataFrame()

def Download_Data(link,i):
    global df

    print('>> Reading Data from the Source :', i+1 , ";", link)

    req = Request(link, headers={'User-Agent': 'Mozilla/5.0'})
    page = urlopen(req)
    html = page.read().decode("utf-8")
    soup = BeautifulSoup(html, "html.parser")

    Data = soup.find('div', {'class':"page-title symbol-header-info"}).attrs
    Data = Data['data-ng-init']

    Data = json.loads(Data[5:-1])
    df1 = json_normalize(Data)
    df = df.append(df1,ignore_index = True)


Source_list = ["url_of_your_source_1",
               "url_of_your_source_2"]

i = 0
for link in Source_list:
    try:
        Download_Data(link,i)
    except Exception as e:
        print(repr(e))
        print('\n<> Source not Found' + Source_list[i])
        pass
    i += 1

df.columns = [x_cols.title() for x_cols in df.columns.to_list()]
columns={'Symbol','Symbolname',	'Symboltype',	'Lastprice',	'Pricechange',	'Percentchange',	'Tradetime',
         'Contractname', 'Daystocontractexpiration', 'Symbolcode',	'Exchange',	'Symbolroot', 'Sessiondatedisplaylong'}

df.to_csv('data.csv', index=False, encoding='utf-8-sig',columns=columns)
print("<> Data file has been generated successfully")

tabular_table = PrettyTable()
tabular_fields = ["Brand Name","Latest Price", "Price Change", "Percentage Change"]
tabular_table.field_names = tabular_fields
tabular_table.add_row([df.loc[0, 'Contractname'],df.loc[0, 'Lastprice'],df.loc[0, 'Pricechange'], df.loc[0, 'Percentchange']])
tabular_table.add_row([df.loc[1, 'Contractname'],df.loc[1, 'Lastprice'],df.loc[1, 'Pricechange'], df.loc[1, 'Percentchange']])

print("<> Generating eMail with Data Collected...")
port = 465
smtp_server = "smtp.gmail.com"
sender_email = "sender_mail_id@gmail.com"
receiver_email = "receiver_mail_id@gmail.com"
password = 'password'

my_message = tabular_table.get_html_string()
html = """\
    <html>
        <head>
        <style>
            table, th, td {
                border: 1px solid black;
                border-collapse: collapse;
            }
            th, td {
                padding: 5px;
                text-align: left;    
            }    
        </style>
        </head>
    <body>
    <p>
        Today's Price Details<br>
        %s
    </p>
    </body>
    </html>
    """% (my_message)

with open('data.csv') as fp:
    record = MIMEBase('application', 'octet-stream')
    record.set_payload(fp.read())
    encoders.encode_base64(record)
    record.add_header('Content-Disposition', 'attachment',filename='full_details.csv')

data = MIMEText(html, 'html')
msg = MIMEMultipart('alternative')
msg['Subject'] = 'Daily Price of Coffee Brands'
msg['From'] = sender_email
msg['To'] = receiver_email
msg.attach(data)
msg.attach(record)

context = ssl.create_default_context()
with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email,  msg.as_string())

print("<> Successfully email has been sent...")
