from bs4 import BeautifulSoup 
import requests
import sys

# I tested this with https://www.missouristate.edu with 15 as the page limit 

DOMAIN = ""   #domain to be crawled
PAGE_LIMIT = 0 #number of pages the user wants to visit
URLS_TO_VISIT = [] #urls that have been discovered to visit
URLS_VISITED = [] #urls that have been visited

def crawl():
    while(len(URLS_VISITED) < PAGE_LIMIT and len(URLS_TO_VISIT) > 0): #if the page limit not reached and there are urls to visit
        parsePage(URLS_TO_VISIT[0])
    
def parsePage(url):
    if(url not in URLS_VISITED): #if the url hasn't been visited 
        if(len(URLS_TO_VISIT) != 0): #if this isn't the first call to parsePage() 
            URLS_TO_VISIT.remove(url) #remove the url that is about to be visited
        URLS_VISITED.append(url) #add to visited urls 
        try:
            with requests.get(url) as html: #get page and parse 
                htmlPage = html.content 
                soup = BeautifulSoup(htmlPage, "html.parser")
                
                for link in soup.findAll("a"): #loop through links 
                    try:
                        if(DOMAIN in link['href']): #if it is on the same domain append url 
                            URLS_TO_VISIT.append(link["href"])
                    except:
                        print("no href error occured") 
        except:
            print("network error occured")

def output():
    #output all links to text file
    file = open("output.txt","w")
    for link in URLS_TO_VISIT: 
        file.write(link + " \n") 
    for link in URLS_VISITED: 
        file.write(link + " \n") 
    file.close()   

if __name__ == "__main__":
    DOMAIN = sys.argv[1]
    PAGE_LIMIT = int(sys.argv[2])
    parsePage(DOMAIN)
    crawl()
    output()
