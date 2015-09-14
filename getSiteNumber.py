import urllib2
from bs4 import BeautifulSoup
import time
import os
import shutil
import re
import json

import unirest
import ssl

class getSiteNumber(object):

    def __init__(self,url=None,filename=None):
        self.set_url(url)
        self.filename = filename
        # if hasattr(ssl, '_create_unverified_context'):
        #     ssl._create_default_https_context = ssl._create_unverified_context

    def set_url(self,url):
        self.url = url
        if url:
            self.baseurl = self.getBaseUrl(url)
        self.page_links=[]
        self.gone_through=[]
        self.possibleNumbers = []
        self.writtenNumbers = []

    def isPhoneNumber(self,number):
        if number[0] == "0":
            if len(number) == 11:
                return True
        if number[0] == "+":
            if number[1:3] == "44":
                if len(number) == 13:
                    return True
        return False

    def getBaseUrl(self,url):
        k = -1
        for i in range(len(url)):
            if url[i] == "/":
                if i < len(url) - 1 and (url[i+1] == "/" or url[i-1] == "/"):
                    continue
                else:
                    k = i
                    break
        return str(url[:k])

    def isFileName(self,link):
        k = 0
        for i in link:
            if i == ".":
                k += 1
            if i == "/":
                return False
        if k == 1:
            return True
        return False

    def get_number(self):
        self.gone_through.append(self.url)
        print("Gone through: {}".format(self.gone_through))
        print("Using the url: {}".format(self.url))
        page = urllib2.urlopen(self.url)
        return self.crawl_page(page)

    def crawl_page(self,response):
        # print(response.body)
        soup = BeautifulSoup(response.read(), "lxml")
        if not soup.body:
            return None
        _page_links = soup.findAll("a", href=True)
        # print("All page links: {}".format(page_links))
        for link in _page_links:
            if self.url in link['href']:
                if link['href'] not in self.page_links:
                    self.page_links.append(link['href'])
                continue
            if link['href'][0] == "/":
                l = self.baseurl + link['href']
                if l not in self.page_links:
                    self.page_links.append(l)
                continue
            if self.isFileName(link['href']):
                l = self.baseurl + "/" +link['href']
                if l not in self.page_links:
                    self.page_links.append(l)
                continue

        possibleNumbers = []
        phoneNumber = ""

        for n, char in enumerate(soup.body.text):
            if(len(phoneNumber) >= 11):
                if(self.isPhoneNumber(phoneNumber)):
                    if phoneNumber not in possibleNumbers:
                        if phoneNumber[0] == "+":
                            phoneNumber = "00"+phoneNumber[1:]
                        possibleNumbers.append(str(phoneNumber))

            if char == " ":
                continue
            if char == "0" and soup.body.text[n-1] == "(" and soup.body.text[n+1] == ")":
                continue
            if char.isalpha():
                phoneNumber = ""
                continue
            if char == "+" and phoneNumber == "":
                phoneNumber += char
                continue
            if char.isdigit():
                phoneNumber += char
                continue
        self.possibleNumbers += possibleNumbers
        if len(self.possibleNumbers) < 1:
            for link in self.page_links:
                if not link in self.gone_through and link != "" and link != None:
                    self.url = link
                    self.get_number()
                    if len(self.possibleNumbers) > 0:
                        break
        if len(self.possibleNumbers) > 0:
            if self.possibleNumbers[0] not in self.writtenNumbers:
                self.writtenNumbers.append(self.possibleNumbers[0])
                with open(self.filename, "a") as myfile:
                    myfile.write(self.baseurl + "\t" + self.possibleNumbers[0] + "\n")
            return self.possibleNumbers
        return []