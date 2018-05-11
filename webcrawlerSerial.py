from bs4 import BeautifulSoup 
import requests
import sys
import time

# I tested this with https://www.missouristate.edu with 15 as the page limit 

DOMAIN = ""   #domain to be crawled
PAGE_LIMIT = 0 #number of pages the user wants to visit
URLS_TO_VISIT = [] #urls that have been discovered to visit
URLS_VISITED = [] #urls that have been visited
MAINDOMAIN = DOMAIN.replace("https://www.","").replace("http://www.","")


def crawl():
    while(len(URLS_VISITED) < PAGE_LIMIT and len(URLS_TO_VISIT) > 0): #if the page limit not reached and there are urls to visit
        parsePage(URLS_TO_VISIT[0])
    
def parsePage(url):
    if(url not in URLS_VISITED): #if the url hasn't been visited 
        if(len(URLS_TO_VISIT) > 0): #if this isn't the first call to parsePage() 
            URLS_TO_VISIT.remove(url) #remove the url that is about to be visited
        URLS_VISITED.append(url) #add to visited urls 
        try:
            with requests.get(url) as html: #get page and parse 
                htmlPage = html.content 
                soup = BeautifulSoup(htmlPage, "html.parser")
                
                for link in soup.findAll("a"): #loop through links 
                    try:
                        if(link not in URLS_TO_VISIT):
                            if(link['href'][0] != "#" and MAINDOMAIN in link['href'] or link['href'][0] == '/'): #if it is on the same domain append url 
                                if(link['href'][0] == '/'):
                                    URLS_TO_VISIT.append(DOMAIN + link["href"])
                                else:
                                    URLS_TO_VISIT.append(link["href"])
                    except:
                        print("no href error occured") 
        except:
            print("network error occured")
    else:
        if(len(URLS_TO_VISIT) > 0): #if this isn't the first call to parsePage() 
            URLS_TO_VISIT.remove(url)

def output():
    #output all links to text file
    file = open("output.txt","w")
    for link in URLS_TO_VISIT: 
        file.write(link + " \n") 
    for link in URLS_VISITED: 
        file.write(link + " \n") 
    file.close()   
    print(len(URLS_TO_VISIT))

if __name__ == "__main__":
    DOMAIN = sys.argv[1]
    PAGE_LIMIT = int(sys.argv[2])
    start_time = time.time()
    parsePage(DOMAIN)
    crawl()
    output()
    print("--- %s seconds ---" % (time.time() - start_time))
