#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Usage: python facecloud.py infile... outfile [**kwargs]

Make a word cloud from Facebook and/or WhatsApp messages and save image

arguments:
    -f --facebook [FILE]  file of Facebook messages
    -w --whatsapp [FILE]  file of WhatsApp messages
    -o --outfile  [FILE]  file to save the word cloud image to
    -e --extra [...] additional args to pass to WordCloud
    
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
        file : str, list
            Path to html file of messages (or list of paths)
        outfile : str
            Path to save the wordcloud image
        kwargs  
            Wordcloud object arguments
    """
    if isinstance(file, str):
        file = [file]
    text = ''
    for f in file:
        text += getFacebookMessageText(f)
    wordcloud = WordCloud(**kwargs)
    wordcloud.generate(text)
    wordcloud.to_file(outfile)


def getFacebookMessageText(file):
    """ Get text from Facebook messages
    
        Parameters
        ----------
        file : str
            Path to html file of messages
            
        Returns
        -------
        String of text
    """
    
    # join all messages with new lines into one string
    words = ''
    
    with open(file) as fileobj:
        html = fileobj.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    
    msgClass = "_3-96 _2let"
    partClass = "_2lek"
    
    # If more than two people are in the cjat <div class="_2lek"> lists
    # the participants
    # Otherwise, the name can be found in <title>
    part = soup.find('div', attrs={'class':partClass})
    m = re.match(r"(Participants:)(.*)", part.text)
    if m:
        names = m.group(2)
    else:
        part = soup.find('title')
        names = part.text
        
    # make list of first names
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
    
    for msg in msgs:
        msgTxt = _getDivText(msg)
        # if the message is not a picture/file
        if ignMsg.search(msgTxt) is None:
            for word in ignWords:
                msgTxt = re.sub(word, '', msgTxt)
            words += '\n' + msgTxt
        
    return words


def getWhatsAppMessageText(file):
    """ Get text from WhatsApp messages
    
        Parameters
        ----------
        file : str
            Path to txt file of messages
            
        Returns
        -------
        String of text
    """
    
    words = ''
    
    with open(file) as fileobj:
        text = fileobj.read()
        
    # first message is probably this:
    # 'Messages to this group are now secured with end-to-end '
    # 'encryption. Tap for more info.')
    # So we should analyse the text after this
    ignMsg = re.search(r"\d\d/\d\d/\d\d\d\d, \d\d:\d\d - .*", text)
    if ignMsg:
        _, idx = ignMsg.span()
        text = text[idx+1:]
        
    ignMsgs = ['This message was deleted', '<Media omitted>']
        
    msgs = re.split(r"\d\d/\d\d/\d\d\d\d, \d\d:\d\d - .*?: ",  text)
    # remove empty messages and strip leading and trailing whitespace
    msgs = [msg.strip() for msg in msgs if msg]
    
    for msg in msgs:
        if msg not in ignMsgs:
            words += '\n' + msg
    
    return words
    
    
def _getDivText(tag):
    # read a div tag of fb messages and return the text of the first div with
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
    t = _guessType(s)
    return t(s)
    

if __name__ == '__main__':

    
    args = sys.argv[1:]
    
    if args[0] in ['-f', '--facebook', '-w', '--whatsapp']:
        files = []
        n = 1
        while True:
            arg = args[n]
            if not arg.startswith('-'):
                files.append(arg)
            else:
                break
            n += 1
    args = args[n:]
    
    if args[0] in ['-o', '--outfile']:
        outfile = args[1]
    args = args[2:]
    
    kwargs = {}
    
    if len(args) > 0 and args[0] in ['-e', '--extra']:
        args = args[1:]
        for r in args:
            k,v = r.split('=')
            # guess the type of the argument and cast
            kwargs[k] = _castType(v)
            
    
    makeWordCloud(files, outfile, **kwargs)
    
    
    # minArgs = 3 # minimum number of args
    
    # if numArgs < minArgs:
    #     print(__doc__)
    #     sys.exit(1)
    
    # infile = sys.argv[1]
    # outfile = sys.argv[2]
    # kwargs = {}

    # if numArgs > minArgs:
    #     remainArgs = sys.argv[minArgs:]
        # for r in remainArgs:
        #     k,v = r.split('=')
        #     # guess the type of the argument and cast
        #     kwargs[k] = _castType(v)
        
    # makeWordCloud(infile, outfile, **kwargs)
    