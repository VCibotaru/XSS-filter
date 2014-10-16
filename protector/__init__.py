from functools import wraps

from werkzeug.datastructures import ImmutableMultiDict
from flask import redirect, request, Response, make_response
import urllib
import HTMLParser
import re
import cgi

    
dangerousTags = ['<script', '<img', '<video', '<a', '<body', '<iframe', '<bgsound'] #taken from owasp cheat sheet
dangerousAttributes = ['src', 'javascript', 'href', 'onmouseover', 'onload', 'onerror', 'background',
    'oncopy', 'oncut', 'oninput', 'onkeydown', 'onkeypress', 'onkeyup', 'onpaste',
    'onbeforeupload', 'onhashchange', 'onoffline', 'online', 'onreadystatechange ',
    'onunload', 'onreset', 'onsubmit', 'onlick',' oncontextmenu', 'ondbclick', 'onmousedown',
    'onmousemove', 'onmouseout', 'onmouseover', 'onmouseup', 'onmousewheel', 'onscroll', 'onblur', 'onfocus']
dangerousWords = ['eval', 'exec', 'alert', 'document.write', 'document["write"]', "document['write']"]
cookieStr = ['document.cookie', 'document["cookie"]', "document['cookie']"]
    
def normalize(s):
    parser = HTMLParser.HTMLParser() 
    s = parser.unescape(s) #unescape html 
    s = s.decode('unicode-escape') #decode unicode (/u006d) and ascii (/x6f)
    s = s.lower() 
    return "".join(s.split()) #remove whitespaces

def canEscapeResponse(request_args, response): #somewhat heuristic method
    canEscapeCount = 0 #it tries to find and escape all input args in resulting rendered page
    for val in request_args.values():
        if response.data.count(val) == 1: #to avoid situations with input like <br>
            newVal = cgi.escape(val, True).replace(':', '#&58;')
            response.set_data(response.data.replace(val, newVal))
            canEscapeCount += 1
    return canEscapeCount == len(request_args.values()) #if all args were escaped it means that page is secure

def findFirstInList(tList, tString, curIndex):
    minIndex = -1
    minSubStr = ""
    for subStr in tList:
        tmp = tString.find(subStr, curIndex)
        if (tmp != -1 and tmp < minIndex) or (minIndex == -1):
            minIndex = tmp
            minSubStr = subStr
    return [minIndex, minSubStr]

def argIsOk(arg):
    normArg = normalize(arg)
    curTagIndex = -1
    while True:
        [curTagIndex, curTag] = findFirstInList(dangerousTags, arg, curTagIndex + 1)
        if curTagIndex == -1:
            return True
        if curTag == '<script': #if current tag == <script>
            curAttrIndex = curTagIndex
            curAttribute = "No attribute"
        else :
            [curAttrIndex, curDangAttribute] = findFirstInList(dangerousAttributes, arg, curTagIndex)
        [curWordIndex, curWord] = findFirstInList(dangerousWords, arg, curAttrIndex)
        [curCookieIndex, curCookie] = findFirstInList(cookieStr, arg, curAttrIndex)
        if curWordIndex == -1 and curCookieIndex == -1:
            continue
        print ' '.join(['Found XSS: ', curTag, curAttribute, curWord, curCookie])
        return False
    return True



def protect(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        rendered_response = view_func(*args, **kwargs)
        if type(rendered_response) is not Response:
            rendered_response = make_response(rendered_response)
        #if canEscapeResponse(request.args, rendered_response):
            #return rendered_response
        for arg in request.args.values():
            if not argIsOk(arg):
                return 'prohibited'
        return rendered_response
    return wrapper
