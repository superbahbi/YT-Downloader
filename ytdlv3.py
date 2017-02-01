#!/usr/bin/python
# sudo pip install --upgrade google-api-python-client
from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser
import json
import requests
import pafy
import zipfile
import Queue
import os, sys, re, platform, time
from subprocess import call
from bottle import route, run, get, post, request, static_file, redirect
import sys

reload(sys)
sys.setdefaultencoding('utf-8')

import thread, threading

import time
from Queue import Queue, Empty
button_pressed = Queue()
stats = Queue()
# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.
DEVELOPER_KEY = "AIzaSyCKM-VT2P72mzXb5XqVHljvS_lZuOuh4-k"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)



def clearScreen():
  if platform.system() == 'Linux':
    os.system('clear')
  elif platform.system() == 'Darwin':
    os.system('clear')
  elif platform.system() == 'Windows':
    os.system('cls')
def check_youtube_video(youtube, id):
  search_response = youtube.videos().list(
      id=id,
      part="contentDetails,status"
    ).execute()
  print (json.dumps(search_response, indent=4, sort_keys=True))

  for search_result in search_response.get("items", []):
    if "regionRestriction" in search_result["contentDetails"]:
      for res in search_result["contentDetails"]["regionRestriction"]["blocked"]:
        if res == "US":
          return "This video contains content from columbia. It is not available in your country."
    if "rejectionReason" in search_result["status"]:
      return search_result["status"]["rejectionReason"]
    if "privacyStatus" in search_result["status"]:
       if search_result["status"]["privacyStatus"] != "public":
          return search_result["status"]["privacyStatus"]
  return 0

def downloadSong(video, path, currentNum, lastNum):
  best = video.getbest(preftype="mp4")
  #title = (video.title).encode("utf-8")
  title = re.sub('[\s\W]+', "_", video.title)
  print ("Download video from youtube")
  print 'Downloading %d/%d  %s(%s)' % (currentNum, lastNum, title, 0)
  best.download(quiet=False, filepath="video."+best.extension)
  time.sleep(2)
  print ("Decoding video to wav")
  #call(["mplayer", "-really-quiet", "-novideo", "-nocorrect-pts", "-ao", "pcm:waveheader",  "video."+best.extension])
  call(["mplayer", "-novideo", "-nocorrect-pts", "-ao", "pcm:waveheader",  "video."+best.extension])
  time.sleep(2)
  print ("Converting wav to mp3")
  #call(["lame", "-h", "-b", "192", "--quiet", "audiodump.wav", title + ".mp3"])
  call(["lame", "-h", "-b", "192", "audiodump.wav", title + ".mp3"])
  time.sleep(2)
  #print ("Adding id3v2 tag")
  #call(["id3v2", "-t {}".format(video.title), "-a {}".format(path), title + ".mp3" ])
  #time.sleep(2)
  print ("Moving " + title + ".mp3 to " + path + " folder")
  call(["mv", title + ".mp3",  path ])
  #mvstr = "mv {}.mp3 '{}.mp3'".format(title, (video.title).encode("utf-8"))
  #call([mvstr])
  #time.sleep(2)
  print ("Deleting temp files")
  os.remove("audiodump.wav")
  os.remove("video."+best.extension)
  print ("Done")
  time.sleep(3)
  return title

def youtube_search(options):
  youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey=DEVELOPER_KEY)
  if options["video"] and options["channel"] == True:
    print "Getting video info"
    status = check_youtube_video(youtube, options["video"])
    if status == 0:
      clearScreen()
      folderName = options["video"]
      video = pafy.new(options["video"])
      title = downloadSong(video, folderName, 1, 1)
    else:
      print (status)
  elif options["channel"] or options["playlist"]:
    if options["channel"]:
      print "Getting channel info"
      search_response = youtube.channels().list(
        id=options["channel"],
        part="snippet"
      ).execute()
      youtube_list_request = youtube.search().list(
        order="date",
        channelId=options["channel"],
        part="id",
        maxResults=options["max_results"])
    elif options["playlist"]:
      print "Getting playlist info"
      search_response = youtube.playlists().list(
        id=options["playlist"],
        part="snippet"
      ).execute()
      youtube_list_request = youtube.playlistItems().list(
        playlistId=options["playlist"],
        part="snippet",
        maxResults=options["max_results"])

    for search_result in search_response.get("items", []):
      folder  = search_result["snippet"]["localized"]["title"]
      folderName = folder.encode('utf-8')
      print "Folder name : " + folderName
    if not os.path.exists(folder):
      os.makedirs(folder)
    # Get all video id in a playlist
    ids = set()
    while youtube_list_request:
      youtube_list_response = youtube_list_request.execute()
      #print json.dumps(youtube_list_response, indent=4, sort_keys=True)
      for youtube_item in youtube_list_response["items"]:
        if options["channel"]:
          if youtube_item["id"]["kind"] == "youtube#video":
            video_id = youtube_item["id"]["videoId"]
        elif options["playlist"]:
          video_id = youtube_item["snippet"]["resourceId"]["videoId"]
        ids.add(video_id)
      if options["channel"]:
        youtube_list_request = youtube.search().list_next(
          youtube_list_request, youtube_list_response)
      if options["playlist"]:
        youtube_list_request = youtube.playlistItems().list_next(
          youtube_list_request, youtube_list_response)
    currentNum = 0
    lastNum = len(ids) + 1

    for id in ids:
      status = check_youtube_video(youtube, id)
      currentNum = currentNum + 1
      if status == 0:
        #clearScreen()
        video = pafy.new(id)
        #print '{} {} {} {}'.format(id, folderName, currentNum, lastNum)
        downloadSong(video, folderName, currentNum, lastNum)
      else:
        print (status)
  return folderName + ".zip"


def do_download(id):
  options = {}
  options["video"] = False
  options["channel"] = False
  options["playlist"] = False
  options["max_results"] = 50

  search_response = youtube.search().list(
    q=id,
    part="id,snippet",
    maxResults=options["max_results"]
  ).execute()

  # Add each result to the appropriate list, and then display the lists of
  # matching videos, channels, and playlists.
  for search_result in search_response.get("items", []):
    if search_result["id"]["kind"] == "youtube#video":
        options["video"] = id
    elif search_result["id"]["kind"] == "youtube#channel":
        options["channel"] = id
    elif search_result["id"]["kind"] == "youtube#playlist":
        options["playlist"] = id
    else:
        print ("Invalid input.")
  #print json.dumps(search_response)
  download = youtube_search(options)
if __name__ == '__main__':
  #do_download('PL89CB5B15DF43F606')
  do_download('p_2r3C30rzo')
