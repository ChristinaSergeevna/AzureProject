# -*- coding: utf-8 -*-

import json
import pyodbc
import requests as req
import re
from pprint import pprint
from datetime import datetime

groups = teachers = []
_url = 'https://idm.dvfu.ru/component/calendar/calendar/'
data = re.findall(r'<option value="(.+?)">(.+?)</option>', req.get(_url).text)
for i, g in enumerate(data, start=1):
    if re.search(r'С8502', str(g)):
        teachers = data[i:]
        groups = data[:i]
        break

def getValues(str):
    res = []
    for g in groups:
        data = json.loads(req.get(url.format(g[0])).text)
        for d in data:   
            res.append(d[str])  
    return sorted(list(set(res)))

def uploadDiscipline():
    disc = getValues('discipline')
    for d in disc:
        cursor.execute("INSERT INTO Discipline VALUES ('" + d + "')")

def uploadPlace():
    place = getValues('place')
    housing = 'CDEFGLMS'
    floor = '123456789'
    for p in place:
        if (place[0] == 'S' and place[2] == '-'):
            cursor.execute("INSERT INTO Place VALUES ('" + p + "', '" + place[0:2] +"')")
        elif (place[0] in housing and place[1] in floor):
            cursor.execute("INSERT INTO Place VALUES ('" + p + "', '" + place[0] +"')")
        
def uploadSubgroup():
    sgroup = getValues('subgroup')
    for sg in sgroup:
        cursor.execute("INSERT INTO Subgroup VALUES ('" + sg + "')")

def uploadNagruzka():
    nagruzka = getValues('nagruzka')
    for n in nagruzka:
        cursor.execute("INSERT INTO Nagruzka VALUES ('" + n + "')")

def uploadGroup():     
    for g in groups:
        cursor.execute("INSERT INTO GroupName VALUES ('" + g[0] + "', '" + g[1] + "')")
        
def uploadTeacher():     
    for t in teachers:
        cursor.execute("INSERT INTO Teacher VALUES ('" + t[0] + "', '" + t[1] + "')")

def getTime():
    start = end = []
    for g in groups:
        data = json.loads(req.get(url.format(g[0])).text)
        for d in data:   
            start.append(d['start'][11:19])  
            end.append(d['end'][11:19])
    return [sorted(list(set(start))), sorted(list(set(end)))]

def uploadTime():
    time = getTime()
    for t in time:
        cursor.execute("INSERT INTO LessonTime VALUES ('" + t[0] + "', " + t[1] + "')")

def nWeek(date):  
    ddate = datetime(int(date[:4]), int(date[5:7]), int(date[8:10]))
    return ((ddate - datetime(2018, 9, 17)).days // 7) + 1

def weekday(date):  
    ddate = datetime(int(date[:4]), int(date[5:7]), int(date[8:10]))
    return ddate.weekday()

def getDate():
    date = []
    for g in groups:
        data = json.loads(req.get(url.format(g[0])).text)
        for d in data:   
            date.append(d['start'][:10]) 
    return sorted(list(set(date)))

def uploadDate():
    date = getDate()
    for d in date:
        cursor.execute("INSERT INTO LessonDate VALUES ('" + d + "', " + str(nWeek(d)) + ", " str(weekday(d) + 1) + ")")
        
def uploadPeriod():
    for g in groups:
        data = json.loads(req.get(url.format(g[0])).text)
        for d in data:       
            cursor.execute("INSERT INTO Period VALUES (" + d['id'] + ", " +\
                                                       "(select id from LessonTime where start_time = '" +\
                                                       d['start'][11:19] + "'), " +\
                                                       "(select id from Discipline where name = '"  +\
                                                       d['discipline'] + "'), '" + g[0] + "', " +\
                                                       "(select id from Teacher where name = '" +\
                                                       (d['teacher']['title']) + "'), '" + d['place'] + "', " +\
                                                       "(select id from dbo.LessonDate where d = '"  +\
                                                       d['start'][:10] + "'), " +\
                                                       "(select id from Nagruzka where name = '"  +\
                                                       d['nagruzka'] + "'), " +\
                                                       "(select id from Subgroup where name = '" +\
                                                       d['subgroup'] + "'))")
            cnxn.commit()

url = 'https://idm.dvfu.ru/component/calendar/calendar/getEvents?format=json&filter%5Bgroups%5D={0}'
server = 'tcp:servername.database.windows.net'
database = 'database'
username = 'username@servername'
password = 'password'
driver= '{ODBC Driver 17 for SQL Server}'
cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)
cursor = cnxn.cursor()

#data = json.loads(req.get(url.format(str('00000000-0000-0000-14d5-bbc43e40f662'))).text)
#pprint(data)

#cursor.execute("SELECT * FROM sys.objects WHERE type in (N'U')");
#cursor.execute("SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.Subgroup')") 
#row = cursor.fetchone()
#while row:
#    pprint(str(row))
#    row = cursor.fetchone()
    
cnxn.commit()
cursor.close()
cnxn.close()

#пример запроса (свободные аудитории в чётные недели в среду второй парой):
#select id from Place 
#where id not in (select id_place from Period 
#where id_date in (select id from LessonDate where n_week % 2 = '0'
#and id_weekday = (select id from Weekday where name = 'Среда'))
#and id_time = (select id from LessonTime where start_time = '10:10:00'))