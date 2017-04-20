"""
Created on Sat Mar  4 20:42:14 2017

Extract a date and or time from a string in a variety of formats

@author: David
"""

"""
Possible formats for date:
    Dates:
    25/04/94,25/04/1994, 25/04, 25th Apr, Apr 25th, April 25th
    The 25th of this month, The 25th of next month, 1 month today, 2 months today, in two weeks
    a week on saturday, tomorrow, yesterday, in two days, on Friday ...
    
    How to approach this problem?
    1) Parse the text, splitting into sections seperated by wither spaces or symboles
    2) Run through the text systematically analysing each 'word' and it's significance
    3) Return the best possible understanding
"""
import os
from pathlib import Path

from datetime import datetime, timedelta
import calendar
from dateutil import rrule

import num_parse
from dates import date_finder, time_finder

from textblob import TextBlob, Word

#A dictionary of words that can be understood for mapping words of the same meaning and grouping
_date_words = {
        'second':['time','sec'],
        'seconds':['time','sec'],
        'sec':['time','sec'],
        'secs':['time','sec'],
        'minute':['time','min'],
        'minutes':['time','min'],
        'min':['time','min'],
        'mins':['time','min'],
        'hour':['time','hr'],
        'hours':['time','hr'],
        'hr':['time','hr'],
        'hrs':['time','hr'],
        'day':['time','day'],
        'days':['time','day'],
        'week':['time','wk'],
        'weeks':['time','wk'],
        'wk':['time','wk'],
        'month':['time','mth'],
        'months':['time','mth'],
        'mth':['time','mth'],
        'mths':['time','mth'],
        'year':['time','yr'],
        'yr':['time','yr'],
        'years':['time','yr'],
        'yrs':['time','yr'],
        'morning':['time','am'],
        'afternoon':['time','pm'],
        'evening':['time','pm'],
        'night':['time','pm'],
        'am':['time','am'],
        'pm':['time','pm'],
        'monday':['day',0],
        'mon':['day',0],
        'tuesday':['day',1],
        'tue':['day',1],
        'wednesday':['day',2],
        'wed':['day',2],
        'thursday':['day',3],
        'thur':['day',3],
        'thu':['day',3],
        'friday':['day',4],
        'fri':['day',4],
        'saturday':['day',5],
        'sat':['day',5],
        'sunday':['day',6],
        'sun':['day',6],
        'weekend':['day','wk_end'],
        'weekends':['day','wk_end'],
        'january':['mth',1],
        'jan':['mth',1],
        'february':['mth',2],
        'feb':['mth',2],
        'march':['mth',3],
        'mar':['mth',3],
        'april':['mth',4],
        'apr':['mth',4],
        'apl':['mth',4],
        'may':['mth',5],
        'june':['mth',6],
        'jun':['mth',6],
        'july':['mth',7],
        'jul':['mth',7],
        'august':['mth',8],
        'aug':['mth',8],
        'september':['mth',9],
        'sept':['mth',9],
        'sep':['mth',9],
        'october':['mth',10],
        'oct':['mth',10],
        'november':['mth',11],
        'nov':['mth',11],
        'december':['mth',12],
        'dec':['mth',12],
        'yesterday':['rel','yest'],
        'today':['rel','td'],
        'tomorrow':['rel','tmrw'],
        'in':['rel','in'],
        'last':['rel','last'],
        'first':['rel','first'],
        'this':['rel','this'],
        'next':['rel','nxt'],
        'every':['rel','evy'],
        'at':['at','at'],
        'on':['on','on'],
        'for':['len','for'],
        'untill':['len','till'],
        'till':['len','till'],
        'a':['one','a'],
        'an':['one','a'],
        'midnight':['num','12am'],
        'midday':['num','12pm'],
        'noon':['num','12pm'],
        'past':['num','past'],
        'to':['num','to'],
        'half':['num','30'],
        'quarter':['num','15'],
        }

class natural_time_parser():
    
    def __init__(self):
        #Variables for storing the date
        self.now = datetime.now()
        self.year = 0
        self.month = 0
        self.day = 0
        self.hour = 0
        self.minute = 0
        self.second = 0
        self.length = 0
        self.morning = None
        #Perameters for thwill be passed to rrule
        self.freq = rrule.MINUTELY          #Frequency can be either rrule.YEARLY, MONTHLY, WEEKLY, DAILY, HOURLY, MINUTELY or SECONDLY
        self.dtstart = datetime.now()       #Start from today
        self.interval = 1
        self.wkstart = None
        self.count = 1                      #Returns only one instance as default
        self.until = None
        self.bysetpos = None
        self.byyear = None
        self.bymonth = None
        self.bymonthday = None
        self.byyearday = None
        self.byweekno = None
        self.byweekday = None #0 = Monday ... 6 = Sunday
        self.byhour = None
        self.byminute = None
        self.bysecond = 0 #Default to 0 seconds (who needs to be that accurate anyway??)
        
        #self.log = Path(os.path.dirname(__file__))/'date_log.txt'
        
        self._tags = {
                'time',
                'day',
                'mth',
                'rel',
                'at',
                'on',
                'len',
                'num',
                'rel_t',
                'tm',
                'date',
                'at',
                'on',
                'one',
                } 
        
           
        
    def parse_string(self,s):
        #First make the string all lower case, then split up all the words
        s = s.lower()
        #convert all numerical text to numbers (one => 1, second => 2nd etc
        s = num_parse.convert_num(s)
        tb = TextBlob(s)
        words = tb.words
        #map and group the words using _date_words 
        date_mapped = [(_date_words[w] if w in _date_words else w) for w in words]
        #remove all non-important words and tag numbers
        date_tagged = []
        for item in date_mapped:
            if self.contains_digit(item):
                date_tagged.append(['num',item])
            elif item[0] in self._tags:
                date_tagged.append(item)        
        #Cycle through everything and try to interpret the meaning of all the numbers
        self.interpret_num(date_tagged)
        #Now the numbers are turned to proper numbers and the words are tagged try to understand
        self.interpret_tags(date_tagged)
        #Are there any 'rel' tags in the words. e.g every, tomorrow, next
        
        date_list = list(rrule.rrule(freq=self.freq, dtstart=self.dtstart, interval=self.interval, wkst=self.wkstart, count=self.count, until=self.until,
        bysetpos=self.bysetpos, bymonth=self.bymonth, bymonthday=self.bymonthday, byyearday=self.byyearday, byweekno=self.byweekno,
        byweekday=self.byweekday, byhour=self.byhour, byminute=self.byminute, bysecond=self.bysecond))       
        
        date = date_list[0]
        
        return date
       
    def contains_digit(self,st):
        if isinstance(st,str):
            try:
                return any(c.isdigit() for c in st)
            except Exception:
                return False 
        else: return False
    
    def interpret_num(self,st_tagged):
        '''
        Seeks to understand the meening of each item tagged with the 'num' tag.
        Is it a day? Month? Time? Date? etc
        '''
        i = 0
        for item in st_tagged:            
            if item[0] != 'num':
                i += 1
                continue
            #Special case where 'past' and 'to' have been found
            if item[1] == 'past':
                #Check for number before and after
                if st_tagged[i-1][0] == 'num' and st_tagged[i+1][0] == 'num':
                    #This puts the time in a format that will be recognized
                    item = ['num',st_tagged[i+1][1]+':'+st_tagged[i-1][1]]
            elif item[1] == 'to':
                if st_tagged[i-1][0] == 'num' and st_tagged[i+1][0] == 'num':
                    #This puts the time in a format that will be recognized
                    minutes = str(60 - int(st_tagged[i-1][1]))
                    item = ['num',st_tagged[i+1][1]+':'+minutes] 
            #Special case where the number is a year (previous word a month and/or > 1000)
            try:
                num = int(item[1])
                if num > 1000 and (st_tagged[i-1][0] == 'mth' or st_tagged[i+1][0] == 'mth'):
                    date = ['date',[None,None,num]] 
                    st_tagged[i] = date
                    i += 1
                    continue
            except Exception:
                pass
            #Check if the number is some form of time or date.
            time = time_finder(item[1])
            date = date_finder(item[1])
            #Interpret the time or date
            if time != None:
                st_tagged[i] = time
                i += 1
                continue
            elif date != None:
                st_tagged[i] = date
                i += 1
                continue
            i += 1
    
    def interpret_tags(self,st_tagged):
        '''
        Tries to understand the meaning of a the phrase in relation to dates and time.
        Tags are interpreted in the following order:
            rel, len, time, day, mth, num
        '''
        #Work through each word, analysing the tag and meaning.
        i = 0
        for w in st_tagged:
            #Note that once anything has been interpreted (even if by another function) it is not looked at again
            if w[0] == 'rel':
                self.rel_tag(st_tagged,i)
            i += 1
        
        i = 0
        for w in st_tagged:
            if w[0] == 'len':
                self.len_tag(st_tagged,i)
            i += 1
                       
        i = 0
        for w in st_tagged:
            if w[0] == 'time':
                self.time_tag(st_tagged,i)
            i += 1
            
        i = 0
        for w in st_tagged:
            if w[0] == 'day':
                self.day_tag(st_tagged,i)
            i += 1
            
        i = 0
        for w in st_tagged:
            if w[0] == 'mth':
                self.mth_tag(st_tagged,i)
            i += 1        
        
        i = 0
        for w in st_tagged:
            if w[0] == 'at':
                self.at_tag(st_tagged,i)
            i += 1

        i = 0
        for w in st_tagged:
            if w[0] == 'num':
                self.num_tag(st_tagged,i)
            i += 1
            
        i = 0
        for w in st_tagged:
            if w[0] == 'tm':
                self.tm_tag(st_tagged,i)
            i += 1
        
        i = 0
        for w in st_tagged:
            if w[0] == 'date':
                self.date_tag(st_tagged,i)
            i += 1
   
    def date_tag(self,st_tagged,i):
        '''Pretty straight forward, it's a date'''
        self.bymonthday = st_tagged[i][1][0] if st_tagged[i][1][0] != None else self.bymonthday
        self.bymonth = st_tagged[i][1][1] if st_tagged[i][1][1] != None else self.bymonth
        #For the year need to change the start date
        if st_tagged[i][1][2] != None:
            new_year = st_tagged[i][1][2]
            if self.now.year < new_year:
                self.dtstart = self.dtstart.replace(year=new_year,month=1,day=1,hour=0,minute=0,second=0)
                #TODO feedback when event is in the past
        del st_tagged[i]
        return
    
    def at_tag(self,st_tagged,i):
        '''
        Could be followed by lots of things, generally denots a time or place.
        In this case time is assumed so we check the following 'word' for a number
        or time.
        '''
        if st_tagged[i+1][0] == 'num':
            #Assume that it refers to an hour
            self.byhour = int(st_tagged[i+1][1])
            #Check that it is correct am or pm
            if self.morning == False:
                if self.byhour < 12:
                    self.byhour += 12
            del st_tagged[i+1]
        elif st_tagged[i+1][0] == 'tm':
            #This can be ignored as it will be consumed at another point.
            pass
        del st_tagged[i]
        
        return
            
         
    def tm_tag(self,st_tagged,i):
        '''
        It is assumed currently that this is a start time
        TODO fix for situations where this is an end time e.g 10pm to 11pm
        '''
        self.byhour = st_tagged[i][1][0]
        self.byminute = st_tagged[i][1][1]
        self.bysecond = st_tagged[i][1][2]
        #Check that it matches correct AM/PM
        if self.morning == False and self.byhour < 12:
                self.byhour += 12
        elif self.morning == True and self.byhour >= 12:
            self.byhour -= 12
        del st_tagged[i]
        
        return
        
    def time_tag(self,st_tagged,i):
        '''
        Interprets items tagged with the 'time' tag.
        Words included in the tag are: second (sec), minute (min), hour (hr)
        day (day), week (wk), month (mth), year (yr), am and pm (am, pm).
        TODO get to work with the different time tags (sec, mth, wk etc)
        '''
        #First check for am or pm
        if st_tagged[i][1] == 'am':
            self.morning = True
        elif st_tagged[i][1] == 'pm':
            self.morning = False
        elif st_tagged[i-1][0] == 'num':
            if st_tagged[i][1] == 'sec':
                pass
            elif st_tagged[i][1] == 'min':
                pass
            elif st_tagged[i][1] == 'hr':
                pass
            elif st_tagged[i][1] == 'day':
                pass
            elif st_tagged[i][1] == 'wk':
                pass
            elif st_tagged[i][1] == 'mth':
                pass
            elif st_tagged[i][1] == 'yr':
                pass
            del st_tagged[i]
            del st_tagged[i-1]
        del st_tagged[i]
        return
    
    def day_tag(self,st_tagged,i):
        '''
        Includes all the days of the week. It is assumed this is equivalent to
        this DAY
        '''
        self.byweekday = st_tagged[i][1]
        del st_tagged[i]
        return
    
    def mth_tag(self,st_tagged,i):
        self.bymonth = st_tagged[i][1]
        del st_tagged[i]
        return
    
    def rel_tag(self,st_tagged,i):
        '''
        Interprets items with the relative (rel) tag
        Words included in this tag are: yesterday (yest), today (td), tomorrow (tmrw)
        last (last), this (this), next (nxt), every (evy)
        '''
        #TODO case where word is first, second, third etc (lost as a number)
        #First find out which instance of the tag we are looking at
        word = st_tagged[i][1]
        if word == 'yest':
            pass
        elif word == 'td':
            #Set start date to today
            date = self.now
            self.byyear = date.year
            self.bymonth = date.month
            self.bymonthday = self.day           
        elif word == 'tmrw':
            #Set start date to tomorrow at 00:00
            date = self.now + timedelta(days=1)
            date.replace(hour = 0, minute = 0, second = 0)
            self.byyear = date.year
            self.bymonth = date.month
            self.bymonthday = date.day
        elif word == 'last':
            try:
                last_what = st_tagged[i+1] #should be tagged as [time,day] or [day,(day)]
                if last_what[0] == 'day':
                    self.byweekday = last_what[1]
                    self.bymonthday = -1
                    del st_tagged[i+1]
                elif last_what[1] == 'day':
                    self.bymonthday = -1
                    del st_tagged[i+1]
                else:
                    print('Unexpected format: last')
            except IndexError:
                print('Unexpected format: last')                
            #Done analysis, now remove
            del st_tagged[i]
        elif word == 'nxt':
            #Next word should be one of: year, month, week, [month], [day]
            try:
                next_what = st_tagged[i+1]
                if next_what[0] == 'day':
                    self.dtstart = (self.now + timedelta(days=1)).replace(hour=0,minute=0,second=0)  
                    self.count = 1                    
                    self.byweekday = next_what[1]
                    del st_tagged[i+1]
                elif next_what[0] == 'mth':
                    self.bymonth = next_what[1]
                    del st_tagged[i+1]
                elif next_what[1] == 'yr':
                    #For some reason there is no byyear thing so need to change start date
                    self.byyear = self.now.year + 1
                    self.dtstart = self.dtstart.replace(day = 1, month = 1, year = self.now.year+1, hour = 0, minute = 0, second = 0)
                    del st_tagged[i+1]
                elif next_what[1] == 'mth':
                    date = self.now
                    if date.month < 12:
                        self.bymonth = date.month + 1
                    else:
                        self.bymonth = 1
                    del st_tagged[i+1]
                elif next_what[1] == 'wk':
                    date = self.now.isocalendar()
                    how_many_days = 7 - date[2] #Gets the day
                    self.dtstart = (self.now + timedelta(days=how_many_days)).replace(hour=0,minute=0,second=0)
                    self.until = self.dtstart + timedelta(days=7)    
                    self.count = None
                    del st_tagged[i+1]
                elif next_what[1] == 'day':
                    date = self.now + timedelta(day=1)
                    self.byyear = date.year
                    self.bymonth = self.month
                    self.byday = date.weekday()
                    del st_tagged[i+1]
                else:
                    print('Unexpected format: next/this')
            except IndexError:
                print('Unexpected format: next/this')
            
            del st_tagged[i] 
        elif word == 'this':
            #Next word should be one of: year, month, week, [month], [day]
            try:
                this_what = st_tagged[i+1]
                if this_what[0] == 'day':               
                    self.count = 1
                    self.byweekday = this_what[1]
                    del st_tagged[i+1]
                elif this_what[0] == 'mth':
                    self.bymonth = this_what[1]
                    del st_tagged[i+1]
                elif this_what[1] == 'yr':
                    #For some reason there is no byyear thing so need to change end date
                    self.until = self.now.replace(day = 31, month = 12, hour = 23, minute = 59, second = 59)
                    self.count = None
                    del st_tagged[i+1]
                elif this_what[1] == 'mth':
                    date = self.now
                    self.until = date.replace(day = calendar.monthrange(self.now.year,self.now.month)[1], hour = 23, minute = 59, second = 59)
                    self.count = None
                    del st_tagged[i+1]
                elif this_what[1] == 'wk':
                    self.until = self.now + timedelta(days=7)
                    self.count = None
                    del st_tagged[i+1]
                elif this_what[1] == 'day':
                    self.until = self.now.replace(hour=23,minute=59,second=59)
                    self.count = None
                    del st_tagged[i+1]
                else:
                    print('Unexpected format: next/this')
            except IndexError:
                print('Unexpected format: next/this')
        elif word == 'evy':            
            del st_tagged[i]
        return
    
    
    def num_tag(self,st_tagged,i):
        return
    
    def on_tag(self,st_tagged,i):
        return
    
    def len_tag(self,st_tagged,i):
        '''
        Interprets items with the 'len' tag which includes the words 'for'
        and 'till'
        '''
        word = st_tagged[i][1]
        if word == 'for':
            #TODO (sort out later)
            if st_tagged[i+1][0] == 'num': 
                n = int(st_tagged[i+1][1])
                if st_tagged[i+2][0] == 'time':
                    if st_tagged[i+2][1] == 'sec':
                        self.length = n
                        del st_tagged[i+2]
                    elif st_tagged[i+2][1] == 'min':
                        self.length = n * 60
                        del st_tagged[i+2]
                    elif st_tagged[i+2][1] == 'hr':
                        self.length = n * 3600
                        del st_tagged[i+2]
                else:
                    #Assume hours intended
                    self.length = n * 3600
            elif st_tagged[i+1][0] == 'rel_t':
                #Convert relative time to only seconds
                self.length = st_tagged[i+1][1][0]*3600 + st_tagged[i+1][1][1]*60 + st_tagged[i+1][1][2]
                pass
            elif st_tagged[i+1][0] == 'one':
                #Check the unit of time the user is intending (assume hours otherwise)
                if st_tagged[i+2][0] == 'time':
                    if st_tagged[i+2][1] == 'sec':
                        self.length = n
                        del st_tagged[i+2]
                    elif st_tagged[i+2][1] == 'min':
                        self.length = n * 60
                        del st_tagged[i+2]
                    elif st_tagged[i+2][1] == 'hr':
                        self.length = n * 3600
                        del st_tagged[i+2]
                else:
                    #Assume hours intended
                    self.length = n * 3600
                pass
            
            del st_tagged[i+1]                
                
        elif word == 'till':
            #TODO add functionality to consider number before and after
            del st_tagged[i]
            if st_tagged[i+1][0] == 'num':     
                pass
            elif st_tagged[i+1][0] == 'tm':
                pass
        
        del st_tagged[i]