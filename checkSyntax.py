import datetime

def checkDate(date_string):
    date_format = '%Y-%m-%d'
    try:
       dateObject = datetime.datetime.strptime(date_string, date_format)
    except ValueError:
        return False
    else:
        return True