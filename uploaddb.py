# -*- coding: utf-8 -*-
import json
import pyodbc
import requests as req
import re
from pprint import pprint

def getGroupsAndTeachers(groups, teachers):
    _url = 'https://idm.dvfu.ru/component/calendar/calendar/'
    data = re.findall(r'<option value="(.+?)">(.+?)</option>', req.get(_url).text)
    for i, g in enumerate(data, start=1):
        if re.search(r'С8502', str(g)):
            teachers = data[i:]
            groups = data [:i]
            break

groups = teachers = []
getGroupsAndTeachers(groups, teachers)

def getDiscipline():
    disc = []
    for g in groups:
        data = json.loads(req.get(url.format(g[0])).text)
        for d in data:   
            disc.append(d['discipline'])  
    return sorted(list(set(disc)))

def uploadDiscipline():
    disc = getDiscipline()
    for d in disc:
        cursor.execute("INSERT INTO Discipline (name) VALUES ('" + d + "')")
        
def getPlace():
    place = []
    for g in groups:
        data = json.loads(req.get(url.format(g[0])).text)
        for d in data:   
            place.append(d['place'])  
    return sorted(list(set(place)))

def uploadPlace():
    place = getPlace()
    for p in place:
        cursor.execute("INSERT INTO Place (id) VALUES ('" + p + "')")

def uploadGroup():     
    for g in groups:
        cursor.execute("INSERT INTO GroupName (id, name) VALUES ('" + g[0] + "', '" + g[1] + "')")
        
def uploadTeacher():     
    for t in teachers:
        cursor.execute("INSERT INTO Teacher (id, name) VALUES ('" + t[0] + "', '" + t[1] + "')")

def getDate():
    date = []
    for g in groups:
        data = json.loads(req.get(url.format(g[0])).text)
        for d in data:   
            date.append(d['start'][:10])  
    return sorted(list(set(date)))

def getTime():
    start = end = []
    for g in groups:
        data = json.loads(req.get(url.format(g[0])).text)
        for d in data:   
            start.append(d['start'][12:19])  
            end.append(d['end'][12:19])
    return [sorted(list(set(start))), sorted(list(set(end)))]

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

#cursor.execute("SELECT * FROM sys.columns WHERE object_id = OBJECT_ID('dbo.Subgroup')") 
#row = cursor.fetchone()
#while row:
#    pprint(str(row))
#    row = cursor.fetchone()
    
cnxn.commit()
cursor.close()
cnxn.close()