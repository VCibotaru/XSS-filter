from functools import wraps

from werkzeug.datastructures import ImmutableMultiDict
from flask import redirect, request, Response, make_response
import urllib
import HTMLParser
import re
import cgi

def check_cluw(request_args):
    return all('<' not in arg_value for arg_value in request_args.values())

def check_html(request_args):
    return all('&#' not in arg_value for arg_value in request_args.values())

def check_blash(request_args):
    return all('\\' not in arg_value for arg_value in request_args.values())
    
def normalize(s):
    parser = HTMLParser.HTMLParser() 
    s = parser.unescape(s) #unescape html 
    s = s.decode('unicode-escape') #decode unicode (/u006d) and ascii (/x6f)
    s = s.lower() 
    return "".join(s.split()) #remove whitespaces

def checkRE(inputString):
    contextCrusher = ['<script', '<javascript', '<img', 'body', 'video src', 'video']      
    event = ['','onmouseover','onload','onerror','background']
    valuableInfo = ['document.cookie','document[\'cookie\']', 'document["cookie"]', 'eval']
    for eachContext in contextCrusher:
        for eachEvent in event:
            for eachValuable in valuableInfo:
                regExp = eachContext + '(.)*' +  eachEvent + '(.)*' + eachValuable
                match = re.search(regExp,inputString)
                if match != None:
                    print 'found match: \t regExp \t\t\t input \n\t' + regExp + '\t' + match.group(0)
                    return False
    return True

def validateResponse(request_args, response):
    for val in request_args.values():
        if response.count(val) == 1:
            response.replace(val, escape(val, True).replace(':', '#&58;') )



REQUEST_VALIDATORS = [
]

RESPONSE_VALIDATORS = [
]

def protect(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        rendered_response = view_func(*args, **kwargs)
        if type(rendered_response) is not Response:
            rendered_response = make_response(rendered_response)

    return wrapper
'''
def protect(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        # validate request args2
        #if all(validator(request.args for validator in REQUEST_VALIDATORS):
        for val in request.args.values():
            #if not checkRE(val):
                #   return 'prohibited'
            rendered_response = view_func(*args, **kwargs)
            # view functions can return either raw html code
            # or object of Response class
            if type(rendered_response) is not Response:
                rendered_response = make_response(rendered_response)

            # validate response
            if all(validator(rendered_response) for validator in RESPONSE_VALIDATORS):
                print rendered_response.get_data()
                return rendered_response

    return wrapper
'''
'''
        if (all(checks)): 
            rendered_response = view_func(*args, **kwargs)
            # view functions can return either raw html code
            # or object of Response class
            if type(rendered_response) is not Response:
                rendered_response = make_response(rendered_response)

            # validate response
            if all(validator(rendered_response)
                for validator in RESPONSE_VALIDATORS
            ):
                # everything is fine
                return rendered_response
        # something went wrong
        return 'prohibited'

    return wrapper
'''