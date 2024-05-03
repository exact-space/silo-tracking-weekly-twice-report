from datetime import datetime, timedelta
import time
import pandas as pd
import numpy as np 
import requests , json,time
import os
import pytz
import platform
import messaging as mg
version = platform.python_version().split(".")[0]
if version == "3":
  import app_config.app_config as cfg
elif version == "2":
    import app_config as cfg
config = cfg.getconfig()

body={
        "Silo 1": {
            "Vendors": [
                "GAP_Shaft_Coke_Sanvira",
                "GAP_Shaft_Coke_Sinoway",
                "GAP_Shaft_Coke_Shangdom",
                "GAP_Shaft_Coke_Jingashu",
                "GAP_Shaft_Coke_Shandong_Yujia"
            ],
            "Consignment":[
                "GAP_Consignment_Sanvira",
                "GAP_Consignment_Sinoway",
                "GAP_Consignment_Shangdom",
                "GAP_Consignment_Jingashu",
                "GAP_Consignment_Shandong_Yujia"
            ],
            "VBD":[
                "GAP_Consignment_Sanvira_VBD",
                "GAP_Consignment_Sinoway_VBD",
                "GAP_Consignment_Shangdom_VBD",
                "GAP_Consignment_Jingashu_VBD",
                "GAP_Consignment_Shandong_Yujia_VBD"
            ]
        },
        "Silo 2":{
            "Vendors": [
                "GAP_Rotary_Coke_Sanvira_Oman", 
                "GAP_Rotary_Coke_Krishna_Hydrocarbons", 
                "GAP_Rotary_Coke_Primer_Industries",       
                "GAP_Rotary_Coke_NRL",      
                "GAP_Rotary_Coke_Oxbow_kwait", 
                "GAP_Rotary_Coke_Neo_Carbon",
                "GAP_Rotary_Coke_Oxbow_USA_550",
                "GAP_Rotary_Coke_Oxbow_USA",
                "GAP_Rotary_Coke_Petro_Carbon", 
                "GAP_Rotary_Coke_Goa_Carbon",
                "GAP_Rotary_Coke_Raincil"
                ],
            "Consignment":[
                "GAP_Consignment_Sanvira_Oman",
                "GAP_Consignment_Krishna_Hydrocarbons",
                "GAP_Consignment_Primer_Industries",
                "GAP_Consignment_NRL",
                "GAP_Consignment_Oxbow_kwait",
                "GAP_Consignment_Neo_Carbon",
                "GAP_Consignment_Oxbow_USA_550",
                "GAP_Consignment_Oxbow_USA",
                "GAP_Consignment_Petro_Carbon",
                "GAP_Consignment_Goa_Carbon",
                "GAP_Consignment_Raincil"
                 ],
            "VBD":[
                 "GAP_Consignment_Sanvira_Oman_VBD",
                "GAP_Consignment_Krishna_Hydrocarbons_VBD",
                "GAP_Consignment_Primer_Industries_VBD",
                "GAP_Consignment_NRL_VBD",
                "GAP_Consignment_Oxbow_kwait_VBD",
                "GAP_Consignment_Neo_Carbon_VBD",
                "GAP_Consignment_Oxbow_USA_550_VBD",
                "GAP_Consignment_Oxbow_USA_VBD",
                "GAP_Consignment_Petro_Carbon_VBD",
                "GAP_Consignment_Goa_Carbon_VBD",
                "GAP_Consignment_Raincil_VBD"
            ]
            
        }
    }

import pandas as pd
import numpy as np 
import requests , json,copy
def getdata_api(dataTagId):
        # url='https://data.exactspace.co/exactdata/api/v1/datapoints/query'
        url=config["api"]["query"]
#         print(url)
        body = {
            "metrics": [],
            "cache_time": 0,
            "start_absolute": 1698777000000,
            
            }
            
        for tag in dataTagId:

            query = {
                    "tags": {},
                    "name": tag,
                }
            body['metrics'].append(query)

        res = requests.post(url=url,json = body)
        custJson = json.loads(res.content)
        # print(custJson)
        df_list = []
        for cust in custJson['queries']:

            listOfList = cust['results'][0]['values']
            time = [lists[0] for lists in listOfList ]
            value = [lists[1] for lists in listOfList ]
            tag = cust['results'][0]['name']
            df = pd.DataFrame({"time":time,tag:value})
            # df['time'] = pd.to_datetime(df['time'], unit='ms') + pd.Timedelta(hours=5.5)
            # df['time'] = df['time'].dt.floor('min')
            # df.sort_values(by='time', inplace=True)

            df_list.append(df)    
        return df_list

def uploadDataToAttachment(fileName):
    path = "./"
    files = {'upload_file': open(str(path+fileName),'rb')}
    url =config["api"]["meta"]+ '/attachments/tasks/upload'
    # url= 'https://data.exactspace.co/exactapi' +'/attachments/tasks/upload'
    response = requests.post(url, files=files)
    status=""
    if(response.status_code==200):
        status="File uploaded to attachment"
        try:
            os.remove(fileName)
            status+=" and also Removed from local directory"
        except:
            return "Uploaded to attachment but Something went wrong in removing file from local directory"
    else:
        time.sleep(10)
        response = requests.post(url, files=files)
        if(response.status_code==200):
            status="File uploaded to attachment"
            try:
                os.remove(fileName)
                status+=" and also Removed from local directory"
            except:
                return "Uploaded to attachment but Something went wrong in removing file from local directory"
        else:
            return "Error! File upload Failed! File is in your local directory , error code: "+str(response.status_code)
    return status   
def timestamp_to_date(timestamp):
    return time.strftime('%Y-%m-%d', time.localtime(timestamp))

def send_mail(report_file_generated):
    formatted_date = timestamp_to_date(int(time.time()))
    logopath=config["api"]["meta"]+'/attachments/mail/download/logo.png'
    html=' <!doctype html><html><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\"><title>Pulse </title><style type=\"text/css\">body{margin:0;}body,table,td,p,a,li,blockquote{-webkit-text-size-adjust:none!important;font-family:sans-serif;font-style:normal;font-weight:400;}button{width:90%;}@media screen and (max-width:600px){body,table,td,p,a,li,blockquote{-webkit-text-size-adjust:none!important;font-family:sans-serif;}table{width:100%;}.footer{height:auto!important;max-width:48%!important;width:48%!important;}.table.responsiveImage{height:auto!important;max-width:30%!important;width:30%!important;}.table.responsiveContent{height:auto!important;max-width:66%!important;width:66%!important;}.top{height:auto!important;max-width:48%!important;width:48%!important;}.catalog{margin-left:0%!important;}}@media screen and (max-width:480px){body,table,td,p,a,li,blockquote{-webkit-text-size-adjust:none!important;font-family:sans-serif;}table{width:100%!important;border-style:none!important;}.footer{height:auto!important;max-width:96%!important;width:96%!important;}.table.responsiveImage{height:auto!important;max-width:96%!important;width:96%!important;}.table.responsiveContent{height:auto!important;max-width:96%!important;width:96%!important;}.top{height:auto!important;max-width:100%!important;width:100%!important;}.catalog{margin-left:0%!important;}button{width:90%!important;}}</style></head><body yahoo=\"yahoo\" background=\"#f7f7f7\" style=\"background:#f7f7f7;\"><table width=\"100%\" cellspacing=\"0\" cellpadding=\"0\"><tbody><tr><td><table width=\"650\" align=\"center\" cellpadding=\"0\" cellspacing=\"0\" background=\"#fff\" style=\"background:#fff\"><tbody><tr><td bgcolor=\"#f7f7f7\"><table class=\"top\" width=\"48%\" align=\"center\" cellpadding=\"0\" cellspacing=\"0\" style=\"padding:40px 10px 10px 10px;\"><tbody><tr><td style=\"font-size:12px;color:#929292;text-align:center;font-family:sans-serif;padding-bottom:15px;\"><img src="'
    html+=logopath
    html+='" width="150"/></td></tr></tbody></table></td></tr><tr> <td style="border-bottom: solid 1px #CACACA; padding: 15px 15px 30px 15px"><table width="100%" align="left"  cellpadding="0" cellspacing="0"><tr><td width="250" style="padding-top:15px;"><div style="font-size:20px; padding:5px 0px;"><div id="incInfo"><span style="font-size:30px; padding:5px 0px;">'
    html+=str("Daily Silo Tracking Report").replace("_"," ")
    html+='</span></div><div><small>Created on <b><i>'
    html+=formatted_date
    html+=' </i></b></small></div></td></tr></table></td></tr><tr> <td><table class="table" width="96%" align="center" style="text-align: center; padding-top: 15px;"><tbody><tr><td colspan="3" align="left" style="border-bottom: solid 1px #CACACA; padding-bottom: 8px; font-size: 15px;"><b> '
    html+="Customer Details"
    html+=' </b></td></tr><tr style="font-size: 13px; color: #9C9C9C"><td align="left" width="33.3%" style="padding-top: 10px;">Unit</td><td align="left" width="33.3%" style="padding-top: 10px;">Site</td><td align="left" width="33.3%" style="padding-top: 10px;">Customer</td></tr><tr><td align="left" width="33.3%"> '
    html+="GAP"
    html+='</td><td align="left" width="33.3%">'
    html+=str("GAP, Mahan")
    html+='</td><td align="left"  width="33.3%">'
    html+=str("GAP")
    html+='</td></tr></tbody></table><tr> <td style="padding:30px 0px 10px 0px; border-top:solid 1px #CACACA;"><table width="100%" align="left"  cellpadding="0" cellspacing="0"><tr><td align="center"><div> '
    mailrepname=str("Daily Silo Tracking Report")

    file = report_file_generated
    # time.sleep(2)
    
    f1='/src/uploads/tasks/'+report_file_generated
    Report_name="Daily Silo Tracking Report"

    emails=['anisha.jonnalagadda@adityabirla.com','dibyendu.g@adityabirla.com']

    regards='ExactSpace Technologies</b></html>'
    body = {
        "to":emails,
        "subject":  str(mailrepname)+" "+str("GAP"),
        "html": html+'</div></td></tr></table></td></tr><tr> <td ><table width="96%" align="left" cellpadding="0" cellspacing="0"><tr><td style="border-bottom: solid 1px #CACACA; padding-bottom: 35px; padding-left: 15px; font-size: 20px;"> <b>Dear Sir/Ma\'am,<br>Find the attached '+Report_name.replace("_"," ")+' file in the mail.</b></td></tr></table></td></tr></tbody> </table></td></tr></tbody></table></body><br>Regards,<br><b>'+regards,
        "f1":f1,  
        "f2":"", 
        "f3":"", 
        "cc":['nikhil.s@exactspace.co','ashlin.f@exactspace.co','arun@exactspace.co','sayan.dey@adityabirla.com'], 
        "bcc":[] 
    }
    time.sleep(1)
    email = mg.Email()
    mailstatus=email.sendSESMailWithAttach(body)
    # if mailstatus =='Success':
    # print("----------------------mailing the attachment with the report Attachment for report , status : " +str(mailstatus)+" for mailids "+str(emails)+"-------------")
    # else:
    #     time.sleep(5)
    #     mailstatus=email.sendSESMailWithAttach(body)

def create_task(report_file_generated):    
    url = config['api']['meta'] + '/activities'
    # url= 'https://data.exactspace.co/exactapi' + '/activities'
    local_timezone = pytz.timezone('Asia/Kolkata')
    current_time_milliseconds = int(time.time() * 1000)
    dt = datetime.fromtimestamp(current_time_milliseconds / 1000, tz=local_timezone)  # Convert milliseconds to seconds
    dt_alert_due_time = dt + timedelta(minutes=60)

    formatted_date_alert_time = dt.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    formatted_date_alert_due_time = dt_alert_due_time.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    formatted_date = dt.strftime("%Y-%m-%d %H:%M")

    data = {
    "type": "task",
    "voteAcceptCount": 0,
    "voteRejectCount": 0,
    "acceptedUserList": [],
    "rejectedUserList": [],
    "dueDate": formatted_date_alert_due_time,
    "assignee": "6149b9acf1902b2b7aecf9b1",
    "source": "Silo Tracking",
    "team": "GAP Silo Tracking",
    "createdBy": "5f491bb942ba5c3f7a474d15",
    "createdOn": formatted_date_alert_time,
    "siteId": "60ae7260e284d016d3559d09",
    "subTasks": [],
    "chats": [],
    "taskPriority": "--",
    "lastUpdatedOn":formatted_date_alert_time,
    "updateHistory": [{
        "action":"This task is created by Pulse.",
        "by": "",
        "on": formatted_date_alert_time
    }],
    "unitsId": "60ae9143e284d016d3559dfb",
    "collaborators": [
        '64a655f39465450006eebeec', #nikhil
        '61431baf1c46e3435ff50ac7', #sayan
        '5f491bb942ba5c3f7a474d15', #ashlin
        '5c591d697dc9e324ee08a456', #arun
        '6149b9acf1902b2b7aecf9b1' #anisha
        ],
    "status": "inprogress",
    "content": [
        {
            "type": "title",
            "value": "Daily Silo Tracking Report "+str(formatted_date)
        },
         {
            "sec": "No data",
            "type": "text",
            "value": ""
        }
    ],
    "taskGeneratedBy": "system",
    "incidentId": "",
    "category": "",
    "sourceURL": "",
    "notifyEmailIds": [
        "nikhil.s@exactspace.co",
        'ashlin.f@exactspace.co',
        'anisha.jonnalagadda@adityabirla.com',
        'sayan.dey@adityabirla.com',
        'dibyendu.g@adityabirla.com',
        'arun@exactspace.co'
        
    ],
    "chat": [],
    "taskDescription": "",
    "triggerTimePeriod": "days",
    "viewedUsers": [],
    "completedBy": "",
    "equipmentIds": [],
    "mentions": [],
    "systems": [],
    "attachments": [
        {
          "file_name": report_file_generated
        }
      ]
    }

    json_data = json.dumps(data,default=str)
    # print(json_data,"json_data")
    headers = {"Content-Type": "application/json"}
    response = requests.post(url, data=json_data, headers=headers)
    if response.status_code == 200:
        print("Task Create request was successful")
    else:
        print("Task Create request failed with status code:", response.status_code)

    return response.status_code
    

def datageneration(tags):
    #df=getdata_api(raw_tags)
    df = getdata_api(tags)
    # print(df)

    res = pd.DataFrame({"time":[]})
    for i in range(len(df)):
        df1 = df[i]
        if i == 0:
            res = df1
            continue
        res = pd.merge(res,df1, on="time", how="outer")
        # print(df1.shape, res.shape)

    # from functools import reduce
    # dfs = [df[i] for i in range(len(df))]
    # res = reduce(lambda left, right: pd.merge(left, right, on='time', how='outer'), dfs)


#     print(res)
#     print(res.columns)

    df1 = res.copy()

#     df['time'] = pd.to_datetime(df1['time'], format='ms')
    df1['time'] = df1['time'].astype(int)
    df1 = df1.sort_values(by='time', ascending=True)
    df1 = df1.reset_index(drop=True)

    # print(df['time'])
    # print(df.columns)
    return df1

def process_vendor(input_list):
    if input_list[0]!='time':
        words_to_remove = ['GAP', 'Consignment', 'VBD','Rotary','Coke','Shaft']
        filtered_words = [word for word in input_list if word not in words_to_remove]
        result_string = '_'.join(filtered_words)
        return result_string
    
consignment2 = []
con_vb2 = body["Silo 2"]["Consignment"] + body["Silo 2"]["VBD"]
con_vbd2 = datageneration(con_vb2)
# print(con_vbd2)
if con_vbd2.empty:
    print("No Silo 2 Consignment Data Found")
else:
#     con_vbd2 = con_vbd2.drop("time", axis=1)
    consignment=[]
    con_vbd2['time'] = pd.to_datetime(con_vbd2['time'], unit='ms') + pd.Timedelta(hours=5.5)
    for index, row in con_vbd2.iterrows():
        row_time = row['time'] 
        common_value = None
        vbd_value = None

        for col in con_vbd2.columns:
            value = row[col]

            if pd.notna(value) and value != 0:
                col_name_parts = col.split('_')
            
                if col_name_parts[-1] == 'VBD':
                    vbd_value = value
                else:
                    common_value = value

        # Set vbd_value to 0 if it is None (no VBD value found)
        vbd_value = vbd_value if vbd_value is not None else 0
        vendor_name=process_vendor(col_name_parts)
        if type(common_value) != pd.Timestamp:
            if vendor_name !=None:
                if vbd_value ==0:
                    consignment.append((row_time,vendor_name, common_value, vbd_value))

                elif common_value is not None:
                    consignment.append((row_time,vendor_name, common_value, vbd_value))
            
    consignment2 = [(time.strftime('%Y-%m-%d %H:%M:%S'), category, value,vbd) for time, category, value,vbd in consignment]
    # print('Silo2 Consignment Record',consignment2)


feeding_data2 = datageneration(body["Silo 2"]["Vendors"])

Silo2_new = []
if feeding_data2.empty:
    print("No Feeding Found in Silo2")
else:
    raw=[]
    feeding_data2['time'] = pd.to_datetime(feeding_data2['time'], unit='ms') + pd.Timedelta(hours=5.5)
    for index, row in feeding_data2.iterrows():
        row_time = row['time'] 
        for col in feeding_data2.columns:
            value = row[col]
            if pd.notna(value) and value != 0:
                col_name_parts = col.split('_')
                vendor_name=process_vendor(col_name_parts)
#                 last_part = col_name_parts[-1]
                last_part=vendor_name
                
                if last_part != None  or value != row_time:
                    raw.append((row_time, last_part, value))

    Silo2_new = [(time.strftime('%Y-%m-%d %H:%M:%S'), category, value) for time, category, value in raw]
    # print("Feeding Record",Silo2_new)

from collections import defaultdict

def update_consignment_feeding2(consignment, silo):
    updated_consignment = []
    feeding_updated = []

    for feeding_tuple in silo:
        found = False
        for i, consignment_tuple in enumerate(consignment):
            if feeding_tuple[1].lower() == consignment_tuple[1].lower():
                found = True
                consignment[i] = (consignment_tuple[0],consignment_tuple[1], consignment_tuple[2] - feeding_tuple[2], consignment_tuple[3])

                if consignment[i][2] <= 0:
                    consignment.pop(i)
                    feeding_updated.append((feeding_tuple[0], feeding_tuple[1],feeding_tuple[2], consignment_tuple[3],consignment_tuple[0]))
                else:
                    feeding_updated.append((feeding_tuple[0],feeding_tuple[1],feeding_tuple[2], consignment[i][3],consignment[i][0]))

                break

        if not found:
            feeding_updated.append((feeding_tuple[0],feeding_tuple[1],feeding_tuple[2],0,0))
            # print(f"Consignment not found for {feeding_tuple[1]}{feeding_tuple[2]}")

    # print(feeding_updated)
    # print("#######")
    # print(consignment)
    consignment = [t for t in consignment if t[2] > 0]

    updated_consignment.extend(consignment)

#     print(feeding_updated)

    aggregated_data = defaultdict(lambda: {'date': None, 'categories': {}, 'con_date': None})

    # Assuming feeding_updated is a list of tuples with (date, category, value, weight, con_date)
    for date, category, value, weight, con_date in feeding_updated:
        if aggregated_data[date]['date'] is None:
            aggregated_data[date]['date'] = date
        if aggregated_data[date]['con_date'] is None:
            aggregated_data[date]['con_date'] = con_date

        if category not in aggregated_data[date]['categories']:
            aggregated_data[date]['categories'][category] = {'total_value': 0, 'weight_sum': 0}

        aggregated_data[date]['categories'][category]['total_value'] += value
        aggregated_data[date]['categories'][category]['weight_sum'] += weight

    Combined_feeding = [
        (
            key,  # Include the date in the tuple
            ' + '.join([f'{category}' for category in aggregated_data[key]['categories']]),
            sum([aggregated_data[key]['categories'][category]['total_value'] for category in aggregated_data[key]['categories']]),
            [aggregated_data[key]['categories'][category]['weight_sum'] for category in aggregated_data[key]['categories']],
            aggregated_data[key]['con_date']  # Include con_date in the tuple
        )
        for key in aggregated_data
    ]

    final_feeding = []

    for tup in Combined_feeding:
        date, category, total_value, weights, con_date = tup  # Added 'con_date' in the unpacking
        non_zero_weights = [w for w in weights if w != 0]
        if non_zero_weights:
            weighted_average = sum(non_zero_weights) / len(non_zero_weights)
            final_feeding.append((date, category, total_value, weighted_average, con_date))

    return updated_consignment, final_feeding

silo2_consignment=consignment2
con2,feed2=update_consignment_feeding2(silo2_consignment,Silo2_new)

# print(con2)
# print(feed2)

consignment1 = []
con_vb = body["Silo 1"]["Consignment"] + body["Silo 1"]["VBD"]
con_vbd1 = datageneration(con_vb)
# print(con_vbd1)
if con_vbd1.empty:
    print("No Silo 1 Consignment Data Found")
else:
#     con_vbd1 = con_vbd1.drop("time", axis=1)
    consignment=[]
    con_vbd1['time'] = pd.to_datetime(con_vbd1['time'], unit='ms') + pd.Timedelta(hours=5.5)
    for index, row in con_vbd1.iterrows():
        row_time = row['time'] 
        common_value = None
        vbd_value = None

        for col in con_vbd1.columns:
            value = row[col]

            if pd.notna(value) and value != 0:
                col_name_parts = col.split('_')

                if col_name_parts[-1] == 'VBD':
                    vbd_value = value
                else:
                    common_value = value

        # Set vbd_value to 0 if it is None (no VBD value found)
        vbd_value = vbd_value if vbd_value is not None else 0
        vendor_name=process_vendor(col_name_parts)
        if type(common_value) != pd.Timestamp:
            if vendor_name !=None:

                if vbd_value ==0:
                    consignment.append((row_time,vendor_name, common_value, vbd_value))


                elif common_value is not None:
                    consignment.append((row_time,vendor_name, common_value, vbd_value))
            
    consignment1 = [(time.strftime('%Y-%m-%d %H:%M:%S'), category, value,vbd) for time, category, value,vbd in consignment]
    # print('Silo2 Consignment Record',consignment1)

feeding_data1 = datageneration(body["Silo 1"]["Vendors"])
Silo1_new = []
if feeding_data1.empty:
    print("No Feeding Found in Silo1")
else:
    raw=[]
    feeding_data1['time'] = pd.to_datetime(feeding_data1['time'], unit='ms') + pd.Timedelta(hours=5.5)
    for index, row in feeding_data1.iterrows():
        row_time = row['time'] 
        for col in feeding_data1.columns:
            value = row[col]
            if pd.notna(value) and value != 0:
                col_name_parts = col.split('_')
                vendor_name=process_vendor(col_name_parts)
                
                last_part = vendor_name
                if last_part != None or value != row_time:
                    raw.append((row_time, vendor_name, value))

    Silo1_new = [(time.strftime('%Y-%m-%d %H:%M:%S'), category, value) for time, category, value in raw]
    # print("Feeding Record",Silo1_new)


def update_consignment_feeding(consignment_data, feeding1_data):
    updated_consignment = []
    feeding_updated = []

    for feeding_tuple in feeding1_data:
        found = False
        for i, consignment_tuple in enumerate(consignment_data):
            if feeding_tuple[1].lower() == consignment_tuple[1].lower():
                found = True
                consignment_data[i] = (consignment_tuple[0],consignment_tuple[1], consignment_tuple[2] - feeding_tuple[2], consignment_tuple[3])

                if consignment_data[i][2] <= 0:
                    consignment_data.pop(i)
                    feeding_updated.append((feeding_tuple[0], feeding_tuple[1],feeding_tuple[2], consignment_tuple[3],consignment_tuple[0]))
                else:
                    feeding_updated.append((feeding_tuple[0],feeding_tuple[1],feeding_tuple[2], consignment_data[i][3],consignment_data[i][0]))

                break

        if not found:
            if feeding_tuple[1] == 'Shangdom':
                feeding_updated.append((feeding_tuple[0],feeding_tuple[1],feeding_tuple[2],0.95,0))
            else:
                feeding_updated.append((feeding_tuple[0],feeding_tuple[1],feeding_tuple[2],0,0))
            print(f"Consignment not found for {feeding_tuple[1]}{feeding_tuple[2]}")

    consignment_data = [t for t in consignment_data if t[2] > 0]

    updated_consignment.extend(consignment_data)
    return updated_consignment, feeding_updated

silo1_consignment=consignment1
con1,feed1=update_consignment_feeding(silo1_consignment,Silo1_new)

# print(con1)
# print(feed1)

import pandas as pd
import numpy as np 
import requests , json,copy

def getValues(tagList):
    url = "https://data.exactspace.co/exactdata/api/v1/datapoints/query"
    d = {
        "metrics": [
            {
                "tags": {},
                "name": "",
                "aggregators": [
                    {
                        "name": "avg",
                        "sampling": {
                            "value": "1",
                            "unit": "hours"
                        }
                    }
                ]
            }
        ],
        "plugins": [],
        "cache_time": 0,
        "start_absolute": 1701369000000
        # "start_relative":{
        #     "value":"14",
        #     "unit":"days",
        # }
    }
    finalDF = pd.DataFrame()
    dfs = []
    for tag in tagList:
        d['metrics'][0]['name'] = tag
        res = requests.post(url=url, json=d)
        values = json.loads(res.content)
        df = pd.DataFrame(values["queries"][0]["results"][0]['values'], columns=['time', values["queries"][0]["results"][0]['name']])
        df['time'] = pd.to_datetime(df['time'], unit='ms') + pd.Timedelta(hours=5.5)
        df['time'] = df['time'].dt.floor('min')
        df.sort_values(by='time', inplace=True)
        df = df.drop_duplicates()
        if df.shape[0] < 10:
            pass
        else:
            dfs.append(df)
    final_df = dfs[0]
    for df_ in dfs[1:]:
        final_df = pd.merge(final_df, df_, on='time')
    return final_df

# taglist = ['GAP_GAP01.PLC01.U362_C305_FIT_01_PV','GAP_GAP01.PLC01.U362_C315_FIT_01_PV']
# taglist = ['GAP_Silo_1_Beltscale_Consumption','GAP_Silo_2_Beltscale_Consumption'] 
taglist =['GAP_Shaft_Coke_Consumption','GAP_Rotary_Coke_Consumption']
data = getValues(taglist)
data.columns = ['Time','Silo1_consumption','Silo2_consumption']
# data['Silo2_consumption'] = data['Overall_flow'] - data['Silo1_consumption']
# data.drop_duplicates(subset='Time', inplace=True)
# data.reset_index(drop=True,inplace = True)
# data['Silo1_consumption'] = data['Silo1_consumption'].apply(lambda x: max(0, x))
# data['Silo2_consumption'] = data['Silo2_consumption'].apply(lambda x: max(0, x))
hourly_consumption = data[['Time','Silo1_consumption','Silo2_consumption']]
# data.reset_index(drop=True, inplace=True)
# data.set_index('Time', inplace=True)

# hourly_consumption = data.resample('H').apply(lambda x: x[x >= 1].mean())
# hourly_consumption = hourly_consumption.reset_index()
# hourly_consumption.columns = ['Time', 'Silo1_Consumption','Silo2_Consumption']

# print(hourly_consumption)

def realtime_calc(hourly_consumption,silo1,silo2):
    coke_on_belt_scale_silo1 = []
    left_over_coke = []
    silo1_entries_list = []
    silo1_VBD = []
    con1_data=[]
    feed1_data=[]

    
    coke_on_belt_scale_silo2 = []
    left_over_silo2 = []
    silo2_entries_list = []
    silo2_VBD = []
    con2_data=[]
    feed2_data=[]

    
    c1_date,current_coke_code, current_value,current_VBD,con_date1= silo1[0]
    c2_date,current_coke, c_value, c_VBD,con_date2= silo2[0]
    
    current_index = 0 
    c_index = 0
    change_code = False
    change_code_rotary = False
    
    
    current_silo1_entries = copy.deepcopy(silo1)
    for consumption in hourly_consumption['Silo1_consumption']:
        current_value -= consumption
        negative = current_value
        left_over_coke.append(max(0, current_value))
        coke_on_belt_scale_silo1.append(current_coke_code)
        silo1_VBD.append(current_VBD)
        con1_data.append(con_date1)
        feed1_data.append(c1_date)

    
        if current_value <= 0:
            change_code = True
        if change_code:

            
            if len(current_silo1_entries)>current_index+1:
                c1_date,current_coke_code, current_value, current_VBD,con_date1 = current_silo1_entries[current_index+1]
                current_silo1_entries.pop(current_index+1)
                        
            current_value += negative
            if current_value>0:
                change_code = False
        else:
            change_code = False
        
        current_silo1_entries[0] = (c1_date,current_coke_code, current_value,current_VBD,con_date1)
        ap_current_silo1_entries=copy.deepcopy(current_silo1_entries)
        silo1_entries_list.append(ap_current_silo1_entries)
    


    current_silo2_entries = copy.deepcopy(silo2)
    for consumption in hourly_consumption['Silo2_consumption']:
        c_value -= consumption
        negative = c_value
        left_over_silo2.append(max(0, c_value))
        coke_on_belt_scale_silo2.append(current_coke)
        silo2_VBD.append(c_VBD)
        con2_data.append(con_date2)
        feed2_data.append(c2_date)


        if c_value <= 0:
            change_code_rotary = True
        if change_code_rotary:
            
            if len(current_silo2_entries)>c_index+1:
                c2_date,current_coke, c_value, c_VBD,con_date2 = current_silo2_entries[c_index+1]
                current_silo2_entries.pop(c_index+1)
                        
            c_value += negative
            if c_value>0:
                change_code_rotary = False
        else:
            change_code_rotary = False


       
        current_silo2_entries[0] = (c2_date,current_coke, c_value, c_VBD,con_date2)
        ap_current_silo2_entries=copy.deepcopy(current_silo2_entries)
        silo2_entries_list.append(ap_current_silo2_entries)
    
    hourly_consumption['Coke on silo1 belt scale'] = coke_on_belt_scale_silo1
    hourly_consumption['Left over coke silo1'] = left_over_coke
    hourly_consumption['Silo1_VBD'] = silo1_VBD
    hourly_consumption['Silo1_entries'] = silo1_entries_list
    hourly_consumption['Silo1_Consignment'] = con1_data
    hourly_consumption['Silo1_Feeding'] = feed1_data
    
    
    hourly_consumption['Coke on silo2 belt scale'] = coke_on_belt_scale_silo2
    hourly_consumption['Left over coke silo2'] = left_over_silo2
    hourly_consumption['Silo2_VBD'] = silo2_VBD
    hourly_consumption['Silo2_entries'] = silo2_entries_list
    hourly_consumption['Silo2_Consignment'] = con2_data
    hourly_consumption['Silo2_Feeding'] = feed2_data
    
    return hourly_consumption

hourly_consumption=realtime_calc(hourly_consumption,feed1,feed2)
# print(hourly_consumption)

df=hourly_consumption
# print(df)



# Convert 'Time' column to datetime type
df['Time'] = pd.to_datetime(df['Time'])

# Extract date from 'Time' column
df['Date'] = df['Time'].dt.date

# Group by date and aggregate the values
df_daily = df.groupby('Date').agg({
    'Silo1_consumption': 'sum',
    'Silo2_consumption': 'sum',
    'Coke on silo1 belt scale': lambda x: ', '.join(x.unique()),
    'Coke on silo2 belt scale': lambda x: ', '.join(x.unique()),
    'Silo1_VBD': 'mean',
    'Silo2_VBD': 'mean'
}).reset_index()

# print(df_daily)
new_df=df_daily.round(3)
# print(new_df)

new_df['agg_vbd'] = ((new_df['Silo1_VBD'] + new_df['Silo2_VBD']) / 2).round(3)

# new_df.to_csv("Daily Silo Tracking Record.csv")

formatted_date = timestamp_to_date(int(time.time()))
report_file_generated = f"Daily_Silo_Tracking_Record_{formatted_date}.csv"
new_df.to_csv(report_file_generated, index=False)

###############
uploadDataToAttachment(report_file_generated)
# send_mail(report_file_generated)
create_task(report_file_generated)