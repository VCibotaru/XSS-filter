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
    'onunload', 'onreset', 'onsubmit', 'onclick',' oncontextmenu', 'ondbclick', 'onmousedown',
    'onmousemove', 'onmouseout', 'onmouseover', 'onmouseup', 'onmousewheel', 'onscroll', 'onblur', 'onfocus']
dangerousWords = ['eval', 'exec', 'alert', 'document.write', 'document["write"]', "document['write']",
    'document.writeln', 'document["writeln"]', "document['writeln']", "innerhtml", "outerhtml", "javascript"]
cookieStr = ['document.cookie', 'document["cookie"]', "document['cookie']"]


#white list would be huge, so warm welcome to 
def checkBlackList(tag, attribute, word, cookie):
    if word == 'eval': #if word == 'eval' then we don`t even need document.cookie, e.g. it can be obtained with brainfuck js
        isCookie = True
    else:
        isCookie = cookie in cookieStr

    scriptList = ['src'] + dangerousWords
    if tag == '<script' and word in scriptList and isCookie:
        return True

    mediaList = ['<img', '<video', '<iframe', '<bgsound']
    if tag in mediaList and attribute in dangerousAttributes and isCookie:
        if attribute == 'src':
            isDangWord = True
        else:
            isDangWord = word in dangerousWords
        return isDangWord

    if tag == '<a' and attribute == 'href' and isCookie:
        return True

    if tag == '<body' and word in dangerousWords and isCookie:
        return True

    return False

    




def normalize(s):
    parser = HTMLParser.HTMLParser() 
    s = parser.unescape(s) #unescape html 
    s = s.decode('unicode-escape') #decode unicode (/u006d) and ascii (/x6f)
    s = s.lower() 
    return "".join(s.split()) #remove whitespaces

def canEscapeResponse(request_args, response): #somewhat heuristic method. 
    #We will probably get many falses if html tags are valid
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

#this fuck (sorry, func) isn` quite accurate. TODO: rewrite in)
def argIsOk(arg):
    normArg = normalize(arg)
    curTagIndex = -1
    while True: #for every tag in arg string
        curTagIndex, curTag = findFirstInList(dangerousTags, normArg, curTagIndex + 1)
        if curTagIndex == -1:
            return True
        curAttrIndex = curTagIndex
        while True: #for every attribute of given tag
        #it will iterate till the end of arg string, not till the closing tag ?! Needs thinking
            if (curAttrIndex > len(normArg)):
                break
            if curTag == '<script': 
                curAttribute = ""
            else :
                curAttrIndex, curAttribute = findFirstInList(dangerousAttributes, normArg, curAttrIndex + 1)
            if curAttrIndex == -1:
                break
            curWordIndex = curCookieIndex = curAttrIndex
            while True: #for every word and cookie
                curWordIndex, curWord = findFirstInList(dangerousWords, normArg, curWordIndex + 1)
                curCookieIndex, curCookie = findFirstInList(cookieStr, normArg, curCookieIndex + 1)
                curWord, curCookie, curTagIndex, curAttribute
                if curWordIndex == -1 and curCookieIndex == -1:
                    curAttrIndex += 1
                    break
                print ' '.join(['Found XSS: ', curTag, curAttribute, curWord, curCookie])
                return False
    return True



def protect(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        rendered_response = view_func(*args, **kwargs)
        if type(rendered_response) is not Response:
            rendered_response = make_response(rendered_response)
        if canEscapeResponse(request.args, rendered_response):
            return rendered_response
        for arg in request.args.values():
            if not argIsOk(arg):
                return 'prohibited'
        return rendered_response
    return wrapper
