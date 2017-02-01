from bottle import route, run, get, post, request, static_file
import requests
import pafy
import os, sys, re, platform
from subprocess import call

@route('/')
def index():
	return static_file("index.html", root='')

@route('/download/<filename:re:.*\.mp3>')
def send_mp3(filename):
	return static_file(filename, root='', download=filename)

@post('/download')
def do_download():
	link = request.forms.get('link')
	download = downloadSong(link)
	return "<a href=/download/"+download+">download</a>"

def downloadSong(url):
  video = pafy.new(url)
  best = video.getbest(preftype="mp4")
  title = re.sub('[\s\W]+', "_", video.title)
  best.download(quiet=False, filepath="video."+best.extension)
  call(["mplayer", "-novideo", "-nocorrect-pts", "-ao", "pcm:waveheader",  "video."+best.extension])
  call(["lame", "-h", "-b", "192", "audiodump.wav", title + ".mp3"])
  os.remove("audiodump.wav")
  os.remove("video."+best.extension)
  return title + ".mp3"

run(host='0.0.0.0', port=80)
