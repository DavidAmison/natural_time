
"""
Created on Sat Mar  4 21:17:28 2017

Converts written numbers to integers: Currenlty designed only for positive whole numbers.

@author: David
"""
#from textblob import TextBlob


d_numbers = {        
        'eleven':11,
        'twelve':12,
        'thirteen':13,
        'fourteen':14,
        'fifteen':15,
        'sixteen':16,
        'seventeen':17,
        'eighteen':18,
        'nineteen':19,
        'twenty':20,
        'thirty':30,
        'fourty':40,
        'forty':40,
        'fifty':50,
        'sixty':60,
        'seventy':70,
        'eighty':80,
        'ninety':90,
        'one':1,
        'two':2,
        'three':3,
        'four':4,
        'five':5,
        'six':6,
        'seven':7,
        'eight':8,
        'nine':9,
        'ten':10,
        'hundred':100,
        'thousand':1000,
        'million':1000000,
        }

d_positions = {
        'first':1,
        'second':2,
        'third':3,
        'fourth':4,
        'fifth':5,
        'sixth':6,
        'seventh':7,
        'eighth':8,
        'ninth':9,
        'tenth':10,
        'eleventh':11,
        'twelth':12,
        'thirteenth':13,
        'fourteenth':14,
        'fifteenth':15,
        'sixteenth':16,
        'seventeenth':17,
        'eighteenth':18,
        'nineteenth':19,
        'twentieth':20,
        'thirtieth':30,
        'fourtieth':40,
        'fiftieth':50,
        'sixtieth':60,
        'seventieth':70,
        'eightieth':80,
        'ninetieth':90,
        'hundreth':100,
        'thousandth':1000,
        'millienth':1000000,
        }


def convert(s):
    '''Convert all numbers in the string to digits'''
    numbers = extract_num(s)
    #Is there any millions, thousands or hundreds?
    i = 0
    mi = -1
    th = -1
    hu = -1
    #Find indices of million, thousands and hundreds
    for num in numbers:
        if num == 1000000:
            mi = i
            th = i
            hu = i
            break
        i += 1
    i = mi if mi>-1 else 0
    for num in numbers[i:]:
        if num == 1000:
            th = i
            hu = i
            break
        i += 1
    i = th if th>-1 else 0
    for num in numbers[i:]:
        if num == 100:
            hu = i
            break
        i += 1
    
    total = 0
    total += convert_prefix(numbers[0:mi]) * 1000000 if mi>-1 else 0
    total += convert_prefix(numbers[mi+1:th]) * 1000 if th>-1 else 0
    total += convert_prefix(numbers[th+1:hu]) * 100 if hu>-1 else 0
    total += convert_prefix(numbers[hu+1:])
    
    return total

def convert_prefix(numbers):       
    total = 0
    last = 0
    for num in numbers:
        if num in [100,1000]:
            #Take away the number that would have been added
            if last == 0:
                last = num
                total += last
            else:
                total -= last
                last = num*last
                total += last            
        else:
            total += num
            last = num 
            
    return total  
    
#Read character by character from the right until something matches, store that number
#empty string and continue from that point. 

def extract_num(s):
    '''
    Returns all numbers in a string as a list in the order that they appear.
    Note that it does not interpret the meaning but simply writes the numbers: e.g
    one-hundred and ninety nine will return [1,100,90,9]       
    '''
    check_str = ''
    numbers = []
    for c in reversed(s):
        #Start building the string
        check_str = c + check_str
        #Check if it matches anything in the dictionary
        for num in d_numbers:
            if num in check_str:
                numbers.insert(0,d_numbers[num])
                check_str = ''
                break
        for num in d_positions:
            if num in check_str:
                numbers.insert(0,d_positions[num])
                check_str = ''
                break
            
    return numbers
    
def convert_num(s):
    '''
    Returns the input string with all numbers converted to digit format
    Currently only works for simple numbers
    '''
    s = s.split() #split up all the words
    #Check whether each word is a number in written form
    output_w = []
    previous_num = 0
    for w in s:
        check_str = ''
        numbers = []
        positional = False
        
        for c in reversed(w):
            check_str = c + check_str
            for num in d_numbers:
                if num in check_str:
                    numbers.insert(0,d_numbers[num])
                    check_str = ''
                    break
            for num in d_positions:
                if num in check_str:
                    numbers.insert(0,d_positions[num])
                    positional = True
                    check_str = ''
                    break
        #Try to understand the number (assumption that only two maximum will be found e.g twenty-three)
        n = 0
        if len(numbers) > 1:
            if numbers[0] > numbers[1]:
                n = numbers[0]+numbers[1]                
            else:
                n = numbers[0]*numbers[1]
        elif len(numbers) == 0:
            n = w
        elif numbers[0] < previous_num:            
            n += previous_num + numbers[0]
        elif previous_num == 0:
            n = numbers[0]
        else:
            n = previous_num * numbers[0]
        
        #Delete the previous number if this value includes it
        if previous_num > 0 and isinstance(n,int):
            del output_w[-1]
            
        #Add the word into the list (adjusting if it is a positional number)    
        output_w.append(str(n)+'st') if positional==True else output_w.append(str(n))
            
        try:
            previous_num = int(n)
        except ValueError:
            previous_num = 0
    
    output = ' '.join(str(w) for w in output_w)   
    return output      