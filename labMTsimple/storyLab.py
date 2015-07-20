#!/usr/bin/python
#
# storyLab.py
#
# a python module for using the labMT1.0 dataset
# no dependencies, unless using the plot function
#  (then we use matplotlib)
#
# USAGE
#
# In python:
#   tmpstr = 'a happy sentence'
#   from storyLab import emotionFileReader
#   lens = emotionFileReader(0.0)
#   from storyLab import emotion
#   happs = emotion(tmpstr,lens)
# 
# My test:
# >>> test = emotionFileReader(max=3.0)
# >>> len(test)
# 410
# >>> emotion('hate hate hate the',test)
# 2.34
# >>> test2 = emotionFileReader(min=7.0)
# >>> emotion('hate hate hate the',test2)
# 0
# >>> emotion('hate hate hate the happy',test2)
# 8.22
# >>> test3 = emotionFileReader()
# >>> emotion('hate hate hate the happy',test3)
# 4.044
# >>> allEmotions('hate hate hate the happy',test3)
# [4.044]
# >>> allEmotions('hate hate hate the happy',test,test2,test3)
# [2.34, 8.22, 4.044]
#
# In a shell:
#   alias happiness="$(pwd)/storyLab.py"
#   cat storyLab.py | happiness
#   storyLab.py happiness
#
# written by Andy Reagan
# 2014-03-01

import os
import re
import codecs
import copy

def emotionFileReader(stopval=1.0,lang="english",min=1.0,max=9.0,returnVector=False):
  # emotionFileReader(stopval=1.0,lang="english",min=1.0,max=9.0,returnVector=False)
  # 
  # stopval is our lens, \Delta h
  # read the labMT dataset into a dict with this lens
  # must be tab-deliminated
  #
  # with returnVector = True, returns tmpDict,tmpList,wordList
  # otherwise, just the dictionary

  labMT1flag = False
  scoreIndex = 1 # second value

  fileName = 'labMT/labMT2{0}.txt'.format(lang)

  try:
    f = codecs.open(fileName,'r','utf8')
  except IOError:
    relpath = os.path.abspath(__file__).split(u'/')[1:-1]
    relpath.append('data')
    relpath.append(fileName)
    fileName = '/'+'/'.join(relpath)
    f = codecs.open(fileName,'r','utf8')
  except:
    raise('could not open the needed file')

  # skip the first line
  f.readline()

  tmpDict = dict([(line.split(u'\t')[0].rstrip(u'"').lstrip(u'"'),
        [x.rstrip(u'"') for x in line.split(u'\t')[1:]]) for line in f])

  f.close()
  
  # remove words
  stopWords = []

  for word in tmpDict:
    # start the index at 0
    if labMT1flag:
      tmpDict[word][0] = int(tmpDict[word][0])-1
    if abs(float(tmpDict[word][scoreIndex])-5.0) < stopval:
      stopWords.append(word)
    else:
      if float(tmpDict[word][scoreIndex]) < min:
        stopWords.append(word)
      else:
        if float(tmpDict[word][scoreIndex]) > max:
          stopWords.append(word)
  
  for word in stopWords:
    del tmpDict[word]

  # build vector of all scores
  f = codecs.open(fileName,'r','utf8')
  f.readline()
  tmpList = [float(line.split(u'\t')[2]) for line in f]
  f.close()
  # build vector of all words
  f = codecs.open(fileName,'r','utf8')
  f.readline()
  wordList = [line.split(u'\t')[0] for line in f]
  f.close()

  if returnVector:
    return tmpDict,tmpList,wordList
  else:
    return tmpDict

def emotionFileReaderRaw(stopval=1.0,fileName=u'labMT1raw.txt',min=1.0,max=9.0,returnVector=False):
  # emotionFileReaderRaw(stopval=1.0,fileName=u'labMT1raw.txt',min=1.0,max=9.0,returnVector=False)
  #
  # idea here was originally to use the individual word scores to
  # sample from for each word, and generate a more statistically sound
  # standard deviation
  
  try:
    f = codecs.open(fileName,'r','utf8')
  except IOError:
    relpath = os.path.abspath(__file__).split('/')[1:-1]
    relpath.append('data')
    relpath.append('labMT1raw.txt')
    fileName = ''
    for pathp in relpath:
      fileName += '/' + pathp
    f = codecs.open(fileName,'r','utf8')

  tmpDict = dict()

  while f:
    word = f.readline()
    tmpDict[word] = []
    for i in range(10):
      tmpDict[word].append(map(int,f.readline().split(u'\t'))[1])
  f.close()
  
  # remove words
  stopWords = []

  for word in tmpDict:
    # start the index at 0
    if labMT1flag:
      tmpDict[word][0] = int(tmpDict[word][0])-1
    if abs(float(tmpDict[word][scoreIndex])-5.0) < stopval:
      stopWords.append(word)
    else:
      if float(tmpDict[word][scoreIndex]) < min:
        stopWords.append(word)
      else:
        if float(tmpDict[word][scoreIndex]) > max:
          stopWords.append(word)
  
  for word in stopWords:
    del tmpDict[word]

  return tmpDict

def emotion(tmpStr,someDict,scoreIndex=1,shift=False,happsList=[]):
  # emotion(tmpStr,someDict,scoreIndex=1,shift=False,happsList=[])
  #
  # take a string and the happiness dictionary, and rate the string
  # if shift=True, will return a vector (also then needs the happsList)
  
  scoreList = []
  # make a frequency vector
  if shift:
    freqList = [0 for i in range(len(happsList))]

  # doing this without the NLTK
  # words = [x.lower().lstrip(u"?';:.$%&()\\!*[]{}|\"<>,^-_=+").rstrip(u"@#?';:.$%&()\\!*[]{}|\"<>,^-_=+") for x in re.split(u'\s',tmpStr,flags=re.UNICODE)]
  
  # better re search
  # keeping all of the non-alphanumeric chars that show up inside words in the labMT set
  # which were found by:
  # lang = "english";
  # labMT,labMTvector,labMTwordList = emotionFileReader(stopval=0.0,fileName='labMT2'+lang+'.txt',returnVector=True)
  # charset = set([])
  # for word in labMTwordList:
  #     if len(re.findall('[^\w]+',word)) > 0:
  #         for i in range(len(re.findall('[^\w]+',word))):
  #             charset.add(re.findall('[^\w]+',word)[i])

  # this new replace isn't the exact same as the original parse
  # but it's closer to the one that MITRE developed, and I think
  # that it is an improvement
  replaceStrings = ['---','--','\'\'']
  for replaceString in replaceStrings:
        tmpStr = tmpStr.replace(replaceString,' ')
  words = [x.lower() for x in re.findall(r"[\w\@\#\'\&\]\*\-\/\[\=\;]+",tmpStr,flags=re.UNICODE)]

  # only use the if shifting
  if shift:
    for word in words:
      if word in someDict:
        scoreList.append(float(someDict[word][scoreIndex]))
        freqList[int(someDict[word][0])-1] += 1
  else:
    for word in words:
      if word in someDict:
        scoreList.append(float(someDict[word][scoreIndex]))

  # with numpy (and mean in the namespace)
  # happs = mean(scoreList)
  
  # without numpy
  if len(scoreList) > 0:
    happs = sum(scoreList)/float(len(scoreList))
  else:
    happs = 0

  if shift:
    return happs,freqList
  else:
    return happs

def stopper(tmpVec,labMTvector,labMTwords,stopVal=1.0,ignore=[]):
  # stopper(tmpVec,labMTvector,labMTwords,stopVal=1.0,ignore=[])
  #
  # take a frequency vector, and 0 out the stop words
  # will always remove the nig* words
  #
  # return the 0'ed vector
  
  ignoreWords = ["nigga","nigger","niggaz","niggas"];
  for word in ignore:
    ignoreWords.append(word)
  newVec = copy.copy(tmpVec)
  for i in range(len(labMTvector)):
    if abs(labMTvector[i]-5.0) < stopVal:
      newVec[i] = 0
    if labMTwords[i] in ignoreWords:
      newVec[i] = 0

  return newVec

def emotionV(frequencyVec,scoreVec):
  # emotionV(frequencyVec,scoreVec)
  #
  # given the frequency vector and the score vector, compute the happs
  # doesn't use numpy
  #
  # but equivalent to np.dot(freq,happs)/np.sum(freq)
  
  tmpSum = sum(frequencyVec)
  if tmpSum > 0:
    happs = 0.0
    for i in range(len(scoreVec)):
      happs += frequencyVec[i]*float(scoreVec[i])
    happs = float(happs)/float(tmpSum)
    return happs
  else:
    return -1

def allEmotions(tmpStr,*allDicts):
  # allEmotions(tmpStr,*allDicts)
  #
  # compute scores from a list of dicts
  # and return a list of scores
  
  emotionList = []
  for tmpDict in allDicts:
    emotionList.append(emotion(tmpStr,tmpDict))
  return emotionList

def shift(refFreq,compFreq,lens,words,sort=True):
  # shift(refFreq,compFreq,lens,words,sort=True)
  #
  # compute a shift, and return the results
  # if sort=True
  # will return the three sorted lists, and sumTypes
  # else
  # just the two shift lists, and sumTypes
  # (words don't need to be sorted)
  
  # normalize frequencies
  Nref = float(sum(refFreq))
  Ncomp = float(sum(compFreq))
  for i in range(len(refFreq)):
    refFreq[i] = float(refFreq[i])/Nref
    compFreq[i] = float(compFreq[i])/Ncomp
  # compute the reference happiness
  refH = sum([refFreq[i]*lens[i] for i in range(len(lens))])
  # determine shift magnitude, type
  shiftMag = [0 for i in range(len(lens))]
  shiftType = [0 for i in range(len(lens))]
  for i in range(len(lens)):
    freqDiff = compFreq[i]-refFreq[i]
    shiftMag[i] = (lens[i]-refH)*freqDiff
    if freqDiff > 0:
      shiftType[i] += 2
    if lens[i] > refH:
      shiftType[i] += 1

  indices = sorted(range(len(shiftMag)), key=lambda k: abs(shiftMag[k]), reverse=True)
  sumTypes = [0.0 for i in range(4)]
  for i in range(len(lens)):
    sumTypes[shiftType[i]] += shiftMag[i]

  sortedMag = [shiftMag[i] for i in indices]
  sortedType = [shiftType[i] for i in indices]
  sortedWords = [words[i] for i in indices]

  if sort:
    return sortedMag,sortedWords,sortedType,sumTypes
  else:
    return shiftMag,shiftType,sumTypes

def shiftHtml(scoreList,wordList,refFreq,compFreq,outFile):
  # shiftHtml(scoreList,wordList,refFreq,compFreq,outFile)
  # 
  # the most insane-o piece of code here (lots of file copying,
  # writing vectors into html files, etc)
  #
  # accepts a score list, a word list, two frequency files
  # and the name of an HTML file to generate
  #
  # ** will make the HTML file, and a directory called static
  # that hosts a bunch of .js, .css that is useful
  
  if not os.path.exists('static'):
    os.mkdir('static')

  outFileShort = outFile.split('.')[0]
    
  # write out the template
  f = codecs.open('static/'+outFileShort+'-data.js','w','utf8')
  f.write('lens = ['+','.join(map(lambda x: '{0:.0f}'.format(x),scoreList))+'];\n\n')
  f.write('words = ['+','.join(map(lambda x: '"{0}"'.format(x),wordList))+'];\n\n')
  f.write('refFraw = ['+','.join(map(lambda x: '{0:.0f}'.format(x),refFreq))+'];\n\n')
  f.write('compFraw = ['+','.join(map(lambda x: '{0:.0f}'.format(x),compFreq))+'];\n\n')
  f.close()
  
  # dump out a static shift view page
  template = '''<html>
<head>
<title>Simple Shift Plot</title>
<link href="static/hedotools.shift.css" rel="stylesheet">
</head>
<body>

<div id="header"></div>
<center>

<div id="lens01" class="figure"></div>
<br>
<p>Click on the graph and drag up to reveal additional words.</p>

<br>

<div id="figure01" class="figure"></div>

</center>

<div id="footer"></div>

<script src="static/d3.andy.js" charset="utf-8"></script>
<script src="static/jquery-1.11.0.min.js" charset="utf-8"></script>
<script src="static/urllib.js" charset="utf-8"></script>
<script src="static/hedotools.init.js" charset="utf-8"></script>
<script src="static/hedotools.shifter.js" charset="utf-8"></script>
<script src="static/{0}-data.js" charset="utf-8"></script>
<script src="static/example-on-load.js" charset="utf-8"></script>

</body>
</html>'''
  f = codecs.open(outFile,'w','utf8')
  f.write(template.format(outFileShort))
  f.close()

  print('copying over static files')
  # for staticfile in ['d3.v3.min.js','plotShift.js','shift.js','example-on-load.js']:
  for staticfile in ['d3.andy.js','jquery-1.11.0.min.js','urllib.js','hedotools.init.js','hedotools.shifter.js','example-on-load.js','hedotools.shift.css','shift-crowbar.js']:
    if not os.path.isfile('static/'+staticfile):
      import shutil
      relpath = os.path.abspath(__file__).split('/')[1:-1]
      relpath.append('static')
      relpath.append(staticfile)
      fileName = ''
      for pathp in relpath:
        fileName += '/' + pathp
      shutil.copy(fileName,'static/'+staticfile)

def generateSVG(htmlfile,output=""):
  # generateSVG(htmlfile,output="")
  #
  # use phantomjs and the local crowbar to make the svg file

  if len(output) == 0:
    output = htmlfile.replace(".html",".svg")
  import subprocess  
  status = subprocess.check_output("phantomjs static/shift-crowbar.js {0} shiftsvg {1}".format(htmlfile,output),shell=True)

  return output

def generatePDF(filename,program="rsvg"):
  # generatePDF(filename,program="rsvg")
  #
  # use rsvg or inkscape to make a PDF from the SVG
  
  output = filename.replace(".svg","")
  import subprocess
  if program == "rsvg":
    command = "rsvg-convert --format=eps {0} > {1}.eps".format(filename,output)
    status = subprocess.check_output(command,shell=True)
    command = "epstopdf {0}.eps".format(output)
    status = subprocess.check_output(command,shell=True)
    return '{0}.pdf'.format(output)
  elif program == "inkscape":
    command = "/Applications/Inkscape.app/Contents/Resources/bin/inkscape -f $(pwd)/{0} -A $(pwd)/{1}.pdf".format(filename,output)
    status = subprocess.check_output(command,shell=True)
    return '{0}.pdf'.format(output)

def shiftPDF(scoreList,wordList,refFreq,compFreq,outFile):
  # shiftPDF(scoreList,wordList,refFreq,compFreq,outFile)
  #
  # generate a PDF wordshift directly from frequency files!
  # outfile should probably end in .html
  # and this will make a file that ends in .svg,.eps,and .pdf
  # in addition to html file, in making the wordshift
  
  shiftHtml(scoreList,wordList,refFreq,compFreq,outFile)
  svgfile = generateSVG(htmlfile)
  pdffile = generatePDF(svgfile)
  command = "open {0}".format(pdffile)
  status = subprocess.check_output(command,shell=True)
  
if __name__ == '__main__':
  # run from standard in
  import fileinput
  labMT = emotionFileReader(0.0)
  happsList = [emotion(line,labMT) for line in fileinput.input()]
  
  for value in happsList:
    print(value)
    
  






