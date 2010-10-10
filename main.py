#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from google.appengine.ext import webapp
from google.appengine.ext.webapp import util, template
from google.appengine.api import urlfetch
from BeautifulSoup import BeautifulSoup
from icalendar import Calendar, Event
from urllib import urlencode

import re

def findIcal(url):
    textToParse = urlfetch.fetch(url)
    parsed = BeautifulSoup(textToParse.content)
    icsUrls = parsed.findAll(href=re.compile(".*.ics"))
    if len(icsUrls) == 0:
        return ""
    else:
        return icsUrls[0]['href']

def parseIcal(url):
    iCalContent = urlfetch.fetch(url).content
    return Calendar.from_string(iCalContent).walk()
 

class FindHandler(webapp.RequestHandler):
    def post(self):
        textToParse = findIcal(self.request.get('url'))
        self.response.out.write(textToParse)

class ParseHandler(webapp.RequestHandler):
    def post(self):
        parsedICal = parseIcal(self.request.get('url'))
        vCalendar = parsedICal[0]
        vEvent = parsedICal[1]
        self.response.out.write("Name:" + vCalendar['X-WR-CALNAME']) 
        self.response.out.write("<br/>") 
        self.response.out.write("When:" + str(vEvent['DTSTART'])) 
        self.response.out.write("<br/>") 
        self.response.out.write("Where:" + vEvent['LOCATION']) 
        self.response.out.write("<br/>") 
        self.response.out.write("More Info:" + vCalendar['X-ORIGINAL-URL']) 
        self.response.out.write("<br/>") 
        self.response.out.write("Description:" + vEvent['DESCRIPTION']) 

class FindAndParseHandler(webapp.RequestHandler):
    def post(self):
        urlIcal = findIcal(self.request.get('url'))
        parsedICal = parseIcal(urlIcal)
        vCalendar = parsedICal[0]
        vEvent = parsedICal[1]
        self.response.out.write("Name:" + vCalendar['X-WR-CALNAME']) 
        self.response.out.write("<br/>") 
        self.response.out.write("When:" + str(vEvent['DTSTART'])) 
        self.response.out.write("<br/>") 
        self.response.out.write("Where:" + vEvent['LOCATION']) 
        self.response.out.write("<br/>") 
        self.response.out.write("More Info:" + vCalendar['X-ORIGINAL-URL']) 
        self.response.out.write("<br/>") 
        self.response.out.write("Description:" + vEvent['DESCRIPTION']) 

class MainHandler(webapp.RequestHandler):
    def get(self):
        self.response.out.write(template.render('templates/main.html', locals()))

def main():
    application = webapp.WSGIApplication([('/', MainHandler),
                                          ('/find-ical', FindHandler),
                                          ('/parse-ical', ParseHandler),
                                          ('/find-and-parse-ical', FindAndParseHandler),
                                         ],debug=True)
    util.run_wsgi_app(application)

if __name__ == '__main__':
    main()
