#!/usr/bin/env python
#sudo apt-get install python2.7
#sudo apt-get install mplayer
#sudo apt-get install lame
#pip install requests
#pip install pafy

import requests
import pafy
import os, sys, re, platform, time
from subprocess import call


def downloadSong(url):
  video = pafy.new(url)
  best = video.getbest(preftype="mp4")
  title = re.sub('[\s\W]+', "_", video.title)
  time.sleep(2)
  best.download(quiet=False, filepath="video."+best.extension)
  time.sleep(2)
  call(["mplayer", "-novideo", "-nocorrect-pts", "-ao", "pcm:waveheader",  "video."+best.extension])
  time.sleep(2)
  call(["lame", "-h", "-b", "192", "audiodump.wav", title + ".mp3"])
  time.sleep(2)
  os.remove("audiodump.wav")
  os.remove("video."+best.extension)
  time.sleep(3)


while True:
  print "1. Download a youtube video"
  print "2. Download a youtube playlist"
  print "3. Exit\n"
  print "Select an action: "
  action = raw_input("> ")
  if action == str(1):
    songUrl = raw_input("Enter youtube url: ")
    downloadSong(songUrl)
  elif action == str(2):
    playlistUrl = raw_input("Enter playlist url: ")
    playlist = pafy.get_playlist(playlistUrl)
    for i in range(0, len(playlist['items'])):
      if platform.system() == 'Linux':
        os.system('clear')
      elif platform.system() == 'Darwin':
        os.system('clear')
      elif platform.system() == 'Windows':
        os.system('cls')

      print u"{} / {} - {}".format(i+1, len(playlist['items'])+1, playlist['items'][i]['pafy'].title)
      downloadSong(playlist['items'][i]['pafy'].videoid) 
  elif action == str(3):
    raise SystemExit()
  else:
    print "Not a valid option!\n"
  


