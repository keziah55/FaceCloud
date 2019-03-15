# FaceCloud 

(C) Keziah Milligan, 2019
GPL v3. See https://www.gnu.org/licenses/gpl-3.0.en.html

FaceCloud is a program which makes a word cloud of a conversation,
given an html file of Facebook messages (as you get when you 
[download your data](https://www.facebook.com/help/212802592074644)).

## Requirements

- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [WordCloud](https://github.com/amueller/word_cloud)

## Usage

FaceCloud can be called from the command line, giving input and output files.
Any additional command line arguments are given to the WordCloud constructor.
Documentation for this can be found 
[here](http://amueller.github.io/word_cloud/generated/wordcloud.WordCloud.html#wordcloud.WordCloud).

For example,
```
python facecloud.py messages.html wordcloud.png width=1536 height=1024 colormap=plasma
```
makes a word cloud and saves it to an image 1536x1024 and uses the `plasma' colormap.

WordCloud uses Matplotlib colormaps. A full list of available colormaps can be found 
[here](https://matplotlib.org/gallery/color/colormap_reference.html).
