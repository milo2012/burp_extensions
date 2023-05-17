# -*- coding: utf-8 -*-

import threading, os, sys, re, zipfile, base64, json
from urlparse import urlparse
from burp import IHttpHeader
from burp import IBurpExtender
from burp import IContextMenuFactory
from burp import IHttpRequestResponse

from java.io import IOException
from java.net import URL
from java.util import List, ArrayList
from javax import swing
from javax.swing import JMenuItem
from javax.swing.filechooser import FileNameExtensionFilter
from java.awt import HeadlessException, Toolkit
from java.awt.datatransfer import DataFlavor, UnsupportedFlavorException

class CustomHeader(IHttpHeader):
    def __init__(self, name, value):
        self._name = name
        self._value = value
        
    def getName(self):
        return self._name
        
    def getValue(self):
        return self._value

class BurpExtender(IBurpExtender, IHttpRequestResponse, IContextMenuFactory):
    
    selectedUrls = []
    regex = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))" # if you have a better one change freely
    
    def registerExtenderCallbacks(self, callbacks):
        self.callbacks = callbacks
        self.helpers = callbacks.getHelpers()
        self.context = None
        callbacks.setExtensionName("Sniff Web Requests (Importer)")
        callbacks.registerContextMenuFactory(self)

    def createMenuItems(self, IContextMenuInvocation):
        self.context = IContextMenuInvocation
        if IContextMenuInvocation.getInvocationContext() == IContextMenuInvocation.CONTEXT_TARGET_SITE_MAP_TREE:
            menu_list = ArrayList()
            menu_list.add(JMenuItem("Add to sitemap from json file", actionPerformed=self.file_importKeith))
            self.selectedUrls=[]
            for selectedMessage in IContextMenuInvocation.getSelectedMessages():
                if (selectedMessage.getHttpService() != None):
                    url = self.helpers.analyzeRequest(selectedMessage.getHttpService(),selectedMessage.getRequest()).getUrl()        
                    self.selectedUrls.append(urlparse(url.toString()).hostname)
            self.selectedUrls = set(self.selectedUrls)
            return menu_list
                
    def file_importKeith(self, event):
        self.sitemap_importer_from_file()
        return
    
    def custom_dialog(self):
        filename = None
        fc = swing.JFileChooser()
        ef = swing.filechooser.FileNameExtensionFilter("", ["*"])
        fc.addChoosableFileFilter(ef)
        files = fc.showDialog(None, "Choose File")
        if files == swing.JFileChooser.APPROVE_OPTION:
            filename = fc.getSelectedFile().getPath()
        return filename

    def sitemap_importer_from_file(self):
        urls = []
        filename = self.custom_dialog()
        if filename and os.path.exists(filename):
            file = open(filename, "r") 
            data = json.load(file)
            for url_data in data["urls"]:
                if url_data["requestBody"]!=None:
                  url = url_data["url"]+"|"+url_data["headers"]+"|"+url_data["requestBody"]
                  urls.append(url)
                else:
                  url = url_data["url"]+"|"+url_data["headers"]+"|"
                  urls.append(url)
            unique = set(urls)
            count_urls = 0
            count_match = 0
            for url in unique:
                count_urls += 1 
                t = threading.Thread(target=self.sitemap_importer, args=[url])
                t.daemon = True
                t.start()
                count_match += 1
        file.close()
        self.callbacks.printOutput("Looking for hosts [Found " + str(count_match) + " unique urls from file and imported in sitemap]")
        #self.callbacks.printError(str(count_urls - count_match) + " url(s) didn't match selected sitemap host(s) and not imported from file!")

    def sitemap_importer(self, http_url):        
        lineList = http_url.split("|")

        reqUrl = lineList[0]
        reqHeaders = base64.b64decode(lineList[1])
        reqBody = ""
        if lineList[2]:
            reqBody = base64.b64decode(lineList[2])
        reqHeaderList=[]
        tmpList = reqHeaders.split("\n")
        for x in tmpList:
            reqHeaderList.append(x)
        sitemapUrl = URL(reqUrl)
        port = 443 if sitemapUrl.protocol == 'https' else 80
        port = sitemapUrl.port if sitemapUrl.port != -1 else port
        httpService = self.helpers.buildHttpService(sitemapUrl.host, port, sitemapUrl.protocol)
        httpRequest = self.helpers.buildHttpRequest(URL(reqUrl))

        requestResponse = self.callbacks.makeHttpRequest(httpService, httpRequest)
        requestInfo = self.helpers.analyzeRequest(requestResponse)        

        headers = requestInfo.getHeaders()
        tmpHeaders = headers
        count = 3
        while count<len(tmpHeaders):
            headers.remove(count)
            count+=1

        for x in reqHeaderList:
            headers.add(x)
        #headers.add("X-XSRF-Token: 4444")        

        request = requestResponse.getRequest()
        analyzedRequest = self.helpers.analyzeRequest(request)
        bodyOffset = analyzedRequest.getBodyOffset()
        requestBody = request[bodyOffset:]

        requestBody = self.helpers.stringToBytes(reqBody)

        message = self.helpers.buildHttpMessage(headers, requestBody)
        messageInfo = self.callbacks.makeHttpRequest(httpService, message)

        self.callbacks.addToSiteMap(messageInfo)

