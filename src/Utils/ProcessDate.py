# Copyright (C) 2016 Deloitte Argentina.
# This file is part of CodexGigas - https://github.com/codexgigassys/
# See the file 'LICENSE' for copying permission.
import datetime


# Given a date in str (epoch or ISO)
# will return a datetime object.
def process_date(str_date):
    if str_date is None:
        return None
    str_date=str_date.strip()
    if str_date=="":
        return None
    if str_date.isdigit():
        return datetime.datetime.fromtimestamp(int(str_date))
    elif len(str_date)==20 and str_date[10]=="T":
        return datetime.datetime.strptime(str_date,"%Y-%m-%dT%H:%M:%SZ")
    elif len(str_date)==19 and str_date[10]==" ":
        return datetime.datetime.strptime(str_date,"%Y-%m-%d %H:%M:%S")
    elif len(str_date)==19 and str_date[10]=="T":
        return datetime.datetime.strptime(str_date,"%Y-%m-%dT%H:%M:%S")
    elif len(str_date)==16 and str_date[10]=="T":
        return datetime.datetime.strptime(str_date,"%Y-%m-%dT%H:%M")
    elif len(str_date)==16 and str_date[10]==" ":
        return datetime.datetime.strptime(str_date,"%Y-%m-%d %H:%M")
    else:
        return datetime.datetime.strptime(str_date,"%Y-%m-%d")

# Given a string like >=YYYY-MM-DD
# returns an object like
# {"$gte": datetime.datetime(YYYY,MM,DD,0,0,0,0)}
def parse_date_range(str_date):
    if str_date is None:
        return None
    str_date=str_date.strip()
    if str_date[1]=="=": # for dates like >=YYYY-MM-DD
        if str_date[0]==">":
            operator="$gte"
        elif str_date[0]=="<":
            operator="$lte"
        datetime_object=process_date(str_date[2:])
        return {operator: datetime_object}
    elif str_date[0]==">": # for >YYYY-MM-DD
        operator="$gt"
        datetime_object=process_date(str_date[1:])
        return {operator: datetime_object}
    elif str_date[0]=="<":
        operator="$lt"
        datetime_object=process_date(str_date[1:])
        return {operator: datetime_object}
    elif str_date[0]=="[" and str_date[len(str_date)-1]=="]":
         # for [YYYY-MM-DD;YYYY-MM-DD]
         operator1 = "$gte"
         operator2 = "$lte"
         dates = str_date[1:(len(str_date)-1)].split(";")
         date1 = process_date(dates[0])
         date2 = process_date(dates[1])
         return {operator1: date1, operator2: date2}
    elif len(str_date)==10:
         return {"$gte": process_date(str_date), "$lt": process_date(str_date)+datetime.timedelta(hours=24)}
    else:
         print "Invalid date for parse_date_range: "+str(str_date)
         raise ValueError
