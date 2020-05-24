import re


_date_words = {
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
        }

def date_finder(st):
    '''
    Purpose of this function is to interpret numbers as they relate do dates
    returns ['date',[d,m,y]] where any of these items can be None
    Recognized formats: 
    25/04/1994, 25/04, 3rd, 25-04-1994, 25.04.1994
    
    Note: will asuume date is of the order day-month-year unless it is explicilty
    obvious e.g 04/25 is obviously mm/dd
    '''
    day = None
    month = None
    year = None
    
    #First check for the st, th, nd, rd endings
    matches = re.match(r'\d+(?=(st|th|nd|rd)$)',st)
    if matches:
        #Assumption is that a month day is referred to
        day = int(matches.group(0))
        return ['date',[day,month,year]]
        
    #Now check for the seperated values format (seperated by . or / or -)
    elif any(c in st for c in ['.','-','/','\\']):
        date_format = [None,None,None]
        nums = [None,None,None]
        
        matches = re.findall(r'\w+',st)
        #Now we need to understand each 'word' individually
        for i,match in enumerate(matches):
            #First check if it ends in st,th,nd or rd
            is_day = re.match(r'\d+(?=(st|th|nd|rd)$)',match)
            if is_day:
                 nums[i] = int(is_day.group(0))
                 date_format[i] = 'D' 
            #Now check if it is a word found in the dictionary
            tag = _date_words[match] if match in _date_words else [None,None]
            if tag[0] == 'mth':
                nums[i] = tag[1]
                date_format[i] = 'M'
            #TODO case where the user has specified a day (e.g. Mon-25th)
            #Now check for just plain numbers
            try:
                nums[i] = int(match)
                if nums[i] > 31:
                    date_format[i] = 'Y'
            except:
                pass
        return _fit(nums,date_format)
            
def _fit(nums,date_format):
    '''
    Pass date as an array of form [day,month,year]
    if position is set the number must go there
    '''
    #How many numbers are there?
    n = 0
    for num in nums:
        n += (1 if num != None else 0)
    date = [None,None,None]
    
    if n == 3:            
        #Determing if there is a specific format that must be followed        
        form = date_format
        if date_format[0] != None:
            if date_format[0] == 'D':
                form = ['D','M','Y']
            elif date_format[0] == 'M':
                form = ['M','D','Y']
            elif date_format[0] == 'Y':
                form = ['Y','M','D']
        elif date_format[1] != None:
            
            if date_format[1] == 'M':
                if date_format[2] == 'Y':
                    form = ['D','M','Y']
                elif date_format[2] == 'D':
                    form = ['Y','M','D']
            elif date_format[1] == 'D':
                form = ['M','D','Y']
        elif date_format[2] != None:
            if date_format[2] == 'D':
                form = ['Y','M','D'] 
        #Places those items that have specific designations
        for i, item in enumerate(form):
            if item == 'D':
                date[0] = nums[i]
            elif item == 'M':
                date[1] = nums[i]
            elif item == 'Y':
                date[2] = nums[i]
        #Now determine what they likely are if any other forms were given (N,M,N) or (N,N,Y)
        if form[1] == 'M':
            #must be D,M,Y or Y,M,D
            if nums[0] <= 31:
                date[0] = nums[0]
                date[2] = nums[2]
            elif nums[2] <= 31:
                date[0] = nums[2]
                date[2] = nums[0]
        elif form[2] == 'Y':
            #must be D,M,Y or M,D,Y
            if nums[1] > 12:
                date[0] = nums[1]
                date[1] = nums[0]
            elif nums[0] <= 31:
                date[0] = nums[0]
                date[1] = nums[1]
        #If no form at all is given then give the best guess
        if form[0] == form[1] == form[2] == None:
            if nums[1] > 12:
                #Must be M,D,Y
                date[0] = nums[1]
                date[1] = nums[0]
                date[2] = nums[2]
            elif nums[0] <= 31:
                date[0] = nums[0]
                date[1] = nums[1]
                date[2] = nums[2]
            else:
                date[0] = nums[2]
                date[1] = nums[1]
                date[2] = nums[0]                        
    elif n == 2:
        #Check for a specific fomat
        form = date_format
        if date_format[0] == 'D' or date_format[1] == 'M':
            form = ['D','M',None]
        elif date_format[0] == 'M' or date_format[1] == 'D':
            form = ['M','D',None]
        #Place the numbers if a format is given
        for i, item in enumerate(form):
            if item == 'D':
                date[0] = nums[i]
            elif item == 'M':
                date[1] = nums[i]
        #If there was no format specified make the best guess (assuming D,M is standard)
        if form[0] == form[1] == None:
            if nums[1] > 12:
                date[0] = nums[1]
                date[1] = nums[0]
            elif 31 >= nums[0]:
                date[0] = nums[0]
                date[1] = nums[1]
    #Check if the year is in 4-digit format
    if date[2] != None and date[2] < 1000:
        date[2] += 2000 #it is assumed we are in the current millenium
    
    return ['date',date] 

def time_finder(st):
    '''
    Recognized formats: 7am, 7:00:00 7:00am (given 'time' tag)
    7hr, 7s/sec, 7min (given 'rel_t' tag)        
    '''
    morning = None
    hour = 0
    minute = 0
    second = 0
       
    #Check for s, sec, min or hr at end of word
    matches = re.search(r'(\d+(?=(s|sec|secs)\b))',st)
    if matches:
        second = int(matches.group(1))
    matches = re.search(r'(\d+(?=(min|mins)\b))',st)
    if matches:
        minute = int(matches.group(1))
    matches = re.search(r'(\d+(?=(hr|hrs)\b))',st)
    if matches:
        hour = int(matches.group(1))
    matches = re.search(r'(\d+(?=(day)\b))',st)
    if matches:
        hour = int(matches.group(1))*24
    matches = re.search(r'(\d+(?=(wk)\b))',st)
    if matches:
        hour = int(matches.group(1))*7*24
    matches = re.search(r'(\d+(?=(mth)\b))',st)
    if matches:
        hour = int(matches.group(1))*24*30
    matches = re.search(r'(\d+(?=(yr)\b))',st)
    if matches:
        hour = int(matches.group(1))*7*24*365
      
    if hour+minute+second > 0:
        return ['rel_t',[hour,minute,second]]

    #Check for am or pm at the end of the word
    am_pm = re.search(r'(am|pm)$',st)
    try:
        if am_pm.group(1) == 'am':
            morning = True
        else:
            morning = False
    except AttributeError:
        pass    
    #Check for ##:## format
    if ':' in st or bool(re.search(r'(am|pm)$',st)):
        time = re.findall(r'(\d{1,2})',st)
        if time:
            try:
                hour = int(time[0])
                minute = int(time[1])
                second = int(time[2])
            except IndexError:
                pass
        else:
            return None
    else:
        return None
       
    if morning == False and hour < 12:
        hour += 12
    elif morning == True and hour >= 12:
        hour -= 12
        
    return ['tm',[hour,minute,second,morning]]