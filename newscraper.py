#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import configparser

class APNewsScraper():
    def __init__(self):
        self.target_url = 'https://apnews.com/'
        self.r = requests.get(self.target_url)
        self.soup = BeautifulSoup(self.r.text, "html.parser")
    

    def findBlocks(self):
        list, inbredList = []
        #specific class relevant to relevatn stories
        parents = self.soup.find_all(class_= "PagePromo")
        for parent in parents:
            child = parent.find(class_ = "PagePromo-content")
            if child:
                grandson = child.find("a")
                list.append(grandson)

        for i in list:
            newList = [i.get_text(), i.get("href")]
            inbredList.append(newList)
        return inbredList#list of list, where each list is: [article headline, link to article]
    
    #function for finding other relevant headlines
    def findBlocks(self):
        list, inbredList = [], []
        #specific class relevant to relevatn stories
        parents = self.soup.find_all(class_= "PagePromo")
        for parent in parents:
            child = parent.find(class_ = "PagePromo-content")
            if child:
                grandson = child.find("a")
                list.append(grandson)

        for i in list:
            newList = [i.get_text(), i.get("href")]
            inbredList.append(newList)
        return inbredList#list of list, where each list is: [article headline, link to article]
    
    def convertingListHtml(self, list):
    
        #Gets the main headline
        firstElement = self.soup.find(class_ = "PagePromo-title")
        link = firstElement.find("a")
        firstElement = firstElement.get_text()
        link = link.get("href")

        html_body = "<h1>News Articles of the Day</h1>"
        html_body += f'<h2>Main Story:</h2> <h3>{firstElement} <a href = "{link}"><b>Read More</strong></b></a></h3>' 
        html_body += "<h5>SECONDARY STORIES:</h5><ul>"
        
        #Only writing out first 11 entries considering many of the stories at the bottom of the page are irrelevent/ads
        #Plan: WRITE ALGO TO ADD WEIGHTS TO KEY WORDS (TRUMP, UKRAINE, CHINA, FATAL, ETC) AND FETCH MOST RELEVANT STORIES BASED ON WEIGHT
        for i in range(0, 4):
            html_body += f'<li><p>{list[i][0]} <a href = "{list[i][1]}"><b>Read More<strong></b><a/></p></li>'

        html_body += "</ul><h5>OTHER RELEVANT STORIES</h5><ul>"
        for i in range(4, 10):
            html_body += f'<li><p>{list[i][0]} <a href = "{list[i][1]}. "><b>Read More</strong></b><a/></p></li>'

        return html_body


if __name__ == '__main__':
    #start the config
    config = configparser.ConfigParser()
    config.read("conf.conf")

    #Create AP scraper instance
    ap_scraper = APNewsScraper()
    block_list = ap_scraper.findBlocks()
    html_body = ap_scraper.convertingListHtml(block_list)

    #code for initialzing email
    msg = MIMEMultipart()
    msg["Subject"] = "Today's News"
    me = config["DEFAULT"]["SENDER_EMAIL"]
    family = config["DEFAULT"]["RECEIVER_EMAIL"]
    friend = config["DEFAULT"]["FRIEND_RECEIVER_EMAIL"]
    msg["From"] = me
    msg["To"] = me
    msg.attach(MIMEText(html_body, "html"))

    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587

    try:
        s = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        s.starttls()

        s.login(me, config["DEFAULT"]["APP_PASSWORD"])

        s.sendmail(me, [family], msg.as_string())
        s.sendmail(me, [friend], msg.as_string())
        s.quit()

        print("Sucesseful Email")
    except Exception as e:
        print(f"Error {e}")
