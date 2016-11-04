#!/usr/local/bin/python3

import sys
import re
import requests

# functions

def normalizeUrl(url, currentUrl):
    url = url[:-1]
    url = url.replace('href=\"', "")

    if (url[0] == "."):
        url = re.sub(r'\.\.\/', "", url)
        url = currentUrl + url
    elif (url[0] == "/"):
        url = rootURL + url
    elif (url.startswith("http://") == False):
        url = rootURL + "/" + url

    return url
        

def parsePage():
    newLink = awaitingLinks.pop()

    if (newLink in blockedLinks):
        return
    
    blockedLinks.add(newLink)
    currentUrl = newLink

    try:
        site = requests.get(currentUrl, allow_redirects=False)
        matchURL = urlREO.findall(site.text)
        matchEmail = emailREO.findall(site.text)

        for url in matchURL:
            normUrl = normalizeUrl(url, currentUrl)
            if (normUrl not in blockedLinks):
                awaitingLinks.add(normUrl)

        for email in matchEmail:
            email = re.sub(r'^mailto%3a', "", email)
            emails.add(email)
    except requests.exceptions.RequestException as e:
        # Mainly for filtering DNS lookup error
        # It was usefull when redirects was allowed
        print(e)

if len(sys.argv)  < 3:
	print("Invalid amount of input arguments")
	sys.exit()

url = sys.argv[1]
matchURL = re.fullmatch(r'http[s]?\:\/\/[a-zA-Zа-яА-Я.-]+\.[a-zA-Zрф]+', url, flags=0)

if not matchURL:
    print("There is no web address to parse or invalid structure")
    print("Example url: http://google.com")
    sys.exit()

if not sys.argv[2].isnumeric():
    print("There is no boundary for parse")
    print("You need to set number of pages to parse or 0 if you want to parse all pages")
    sys.exit()

boundary = int(sys.argv[2])

#check if slash at the end
rootURL = "http://www.csd.tsu.ru"


# RegEx Patterns
emailPattern = r'[a-zA-Z0-9-]+(?:[._+%-]+[a-zA-Z0-9]+)*@(?:[a-zA-Z0-9]+[.-]?)+[.][a-zA-Z]{2,}'

urlPattern = r'href="(?:<siteURL>)?(?:\.\.)*(?:\/?[a-zA-Z0-9%-])+\??(?:[a-zA-Z0-9]+\=[a-zA-Z0-9_%-]+[;&]?)*(?:\.html|\.htm|\/)?"'
tempURL = rootURL.replace("/", "\/")
tempURL = tempURL.replace(".", "\.")
tempURL = tempURL.replace("-", "\-")
urlPattern = urlPattern.replace("<siteURL>", tempURL)

# RegEx Objects
emailREO = re.compile(emailPattern)
urlREO = re.compile(urlPattern)


# Manager Lists
awaitingLinks = set()
blockedLinks = set()

emails = set()

awaitingLinks.add(rootURL)

while (len(awaitingLinks) != 0 and len(blockedLinks) < boundary):
    parsePage()
    print(str(len(blockedLinks)) + " was parsed")

f = open('siteLinks.txt', 'w')
f.write("There " + str(len(blockedLinks)) + " links\n")
for link in blockedLinks:
    f.write(link + '\n')
f.close()

f = open('result.txt', 'w')
f.write("Was parsed " + str(len(blockedLinks)) + " links\n")
f.write("Found " + str(len(emails)) + " emails\n\n")
for email in emails:
    f.write(email + '\n')
f.close()

print("Done")

