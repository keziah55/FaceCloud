#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
usage: python facecloud.py infile outfile names **kwargs

Make a word cloud from Facebook messages and save image

positional arguments:
    infile      input message html file
    outfile     file to save the word cloud image to
    
Any additional keyword arguments are given to the WordCloud constructor.
The documentation for WordCloud can be found here:
http://amueller.github.io/word_cloud/generated/wordcloud.WordCloud.html#wordcloud.WordCloud
"""

import re
from bs4 import BeautifulSoup
from wordcloud import WordCloud
import ast
import sys


def makeWordCloud(file, outfile, **kwargs):
    """ Get text from Facebook messages
    
        Parameters
        ----------
        file : str
            Path to html file of messages
        outfile : str
            Path to save the wordcloud image
        kwargs  
            Wordcloud object arguments
    """
    
    text = getMessageText(file)
    wordcloud = WordCloud(**kwargs)
    wordcloud.generate(text)
    wordcloud.to_file(outfile)


def getMessageText(file):
    """ Get text from Facebook messages
    
        Parameters
        ----------
        file : str
            Path to html file of messages
            
        Returns
        -------
        String of text
    """
    
    with open(file) as fileobj:
        html = fileobj.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    msgClass = "_3-96 _2let"
    partClass = "_2lek"
    
    # <div class="_2lek">Participants: Annie Saxberg, Keziah Milligan and Susanna Hotham</div>
    part = soup.find('div', attrs={'class':partClass})
    m = re.match(r"(Participants:)(.*)", part.text)
    if m:
        names = m.group(2)
    else:
        part = soup.find('title')
        names = part.text
        
    names = [n.strip() for n in re.split(r",|and", names)]
    names = [name.split(' ')[0] for name in names]
    
    # message content in <div class="_3-96 _2let"> elements
    msgs = soup.find_all('div', attrs={'class':msgClass})
    
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
    minArgs = 2
    
    if numArgs < minArgs:
        raise TypeError("Please provide an infile and an outfile")
    
    infile = sys.argv[1]
    outfile = sys.argv[2]

    if numArgs > minArgs:
        remainArgs = sys.argv[minArgs+1:]
        kwargs = {}
        for r in remainArgs:
            k,v = r.split('=')
            # guess the type of the argument and cast
            kwargs[k] = _castType(v)
        
    makeWordCloud(infile, outfile, **kwargs)
    