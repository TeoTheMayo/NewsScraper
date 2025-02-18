#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import smtplib 
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import configparser

#Initialze the config
config = configparser.ConfigParser()
config.read("conf.conf")


target_url = "https://apnews.com/"

#Headers to help scrape website
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'en-US,en;q=0.8',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
}


r = requests.get(target_url, headers=headers)#fetch site

soup = BeautifulSoup(r.text, "html.parser")

#function for getting main story on AP news,
#Needs to be improved
def findHeadline(soup):
    firstElement = soup.find(class_ = "PageListStandardE-items")
    list = []
    if firstElement:
        child = firstElement.find(class_ = "PagePromo-title")
        if child:
            grandson = child.find("a")
            if grandson:
                list.append(grandson.get_text())
                list.append(grandson.get("href"))
    return list

#function for finding other relevant headlines
def findBlocks(soup):
    list = []
    inbredList = []
    parents = soup.find_all(class_= "PagePromo")
    for parent in parents:
        child = parent.find(class_ = "PagePromo-content")
        if child:
            grandson = child.find("a")
            list.append(grandson)

    for i in list:
        newList = [i.get_text(), i.get("href")]
        inbredList.append(newList)
    return inbredList

#function for extracting the information from the list and making it neat through html
#Plan: Maybe fetch images as well?
def convertingListHtml(list, firstHeadlineList):
    
    html_body = "<h1>News Articles of the Day</h1>"
    html_body += f'<h3>Main Story: {firstHeadlineList[0]}, <a href = "{firstHeadlineList[1]}">Read More</a></h3>'

        
    html_body += "SECONDARY STORIES:"
    
    #Only writing out first 11 entries considering many of the stories at the bottom of the page are irrelevent/ads
    #Plan: WRITE ALGO TO ADD WEIGHTS TO KEY WORDS (TRUMP, UKRAINE, CHINA, FATAL, ETC) AND FETCH MOST RELEVANT STORIES BASED ON WEIGHT
    for i in range(0, 4):
        html_body += f'<p>{list[i][0]}<a href = "{list[i][1]}">Read More<a/></p>'

    html_body += "<h5>OTHER RELEVANT STORIES</h5>"
    for i in range(4, 10):
        html_body += f'<p>{list[i][0]}<a href = "{list[i][1]}">Read More<a/></p>'

    return html_body


#code for initialzing email
msg = MIMEMultipart()
msg["Subject"] = "Today's News"
me = config["DEFAULT"]["SENDER_EMAIL"]
family = config["DEFAULT"]["RECEIVER_EMAIL"]
msg["From"] = me
msg["To"] = me
html_body = convertingListHtml(findBlocks(soup), findHeadline(soup))
msg.attach(MIMEText(html_body, "html"))

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

try:
    s = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    s.starttls()

    s.login(me, config["DEFAULT"]["APP_PASSWORD"])

    s.sendmail(me, [family], msg.as_string())
    s.quit()

    print("Sucesseful Email")
except:
    print(f"Error")
