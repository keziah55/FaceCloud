#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Make a word cloud from Facebook messages


"""

import re
from bs4 import BeautifulSoup
from wordcloud import WordCloud
import ast
import sys


def makeWordCloud(file, outfile, names=None, **kwargs):
    """ Get text from Facebook messages
    
        Parameters
        ----------
        file : str
            Path to html file of messages
        outfile : str
            Path to save the wordcloud image
        names : list
            List of names of conversation participants
        kwargs  
            Wordcloud object arguments
    """
    
    text = getMessageText(file, names)
    wordcloud = WordCloud(**kwargs)
    wordcloud.generate(text)
    wordcloud.to_file(outfile)


def getMessageText(file, names=None):
    """ Get text from Facebook messages
    
        Parameters
        ----------
        file : str
            Path to html file of messages
        names : list
            List of names of conversation participants
            
        Returns
        -------
        String of text
    """
    
    with open(file) as fileobj:
        html = fileobj.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # only need body
    soup = soup.body
    
    # message content in <div class="_3-96 _2let"> elements
    msgs = soup.find_all('div', attrs={'class':"_3-96 _2let"})
    
    # ignore any text that states a picture/file was sent
    names = '|'.join(names)
    ignMsg = re.compile(
                r"(You|{}) (sent) (a|an) (photo|sticker|attachment|GIF|link)"
                .format(names))
    # list of words to strip out of text
    ignWords = ['https']
    
    text = ''
    
    for msg in msgs:
        msgTxt = _getDivText(msg)
        # if the message is not a picture/file
        if ignMsg.search(msgTxt) is None:
            for word in ignWords:
                msgTxt = re.sub(word, '', msgTxt)
            text += '\n' + msgTxt
        
    return text
    
    
def _getDivText(tag):
    # read a div tag of messages and return the text of the first div with
    # content
    
    # this is necessary because reactions are within the message div
    # (but after the main message content)
    
    # ignore first div, as that contains everything
    m = tag.find_next('div')
    # find next div    
    m = m.find_next('div')
    
    # find first div that contains text
    while not m.text:
        m = m.find_next('div')
        
    return m.text
    

def _guessType(s):
    # this neat wee function is from
    # https://www.reddit.com/r/learnpython/comments/4599hl/module_to_guess_type_from_a_string/czw3f5s
    try:
        value = ast.literal_eval(s)
    except ValueError:
        return str
    else:
        return type(value)
    
def _castType(s):
    t = _guessType(v)
    return t(v)
    

if __name__ == '__main__':

    numArgs = len(sys.argv)
    
    if numArgs < 3:
        raise TypeError("Please provide an infile, outfile and names")
    
    infile = sys.argv[1]
    outfile = sys.argv[2]
    names = sys.argv[3]
    # convert names to list, removing any leading or trailing whitespace
    names = [n.strip() for n in names.split(',')]
    
    if numArgs > 3:
        remainArgs = sys.argv[4:]
        kwargs = {}
        for r in remainArgs:
            k,v = r.split('=')
            # guess the type of the argument and cast
            kwargs[k] = _castType(v)
        
    makeWordCloud(infile, outfile, names, **kwargs)
    