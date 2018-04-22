"""
   Since switching to requests over urllib (so the program can handle https) this example should work. It takes a little while to complete. 
"""
from bs4 import BeautifulSoup 
import requests

links = [] 
allLinks = [] 

def initialPage(url):
    with requests.get(url) as html: #request page and read in file 
        htmlPage = html.content
    
    soup = BeautifulSoup(htmlPage, "html.parser") #parse html with beautiful soup
    
    #get all links concerning google 
    for link in soup.findAll("a"): #the findAll() function accepts a string of the html element you want returned and returns a list of that element.
                                   #each dictitonary object in the list has a field for attributes found for that element (href, src, id etc.) 
        if(link['href'][0] != '#' and 'google' in link['href']): #if the link is not on the same page (#) and 'google' is in the link
            links.append(link["href"])  #append link to a list of links concerning the domain www.google.com
    
def extraPages():
    for link in links[:3]: #visit the first three links found at google.com and collect links from the those pages (same process as above) 
        with requests.get(link) as html:
            htmlPage = html.content
            soup = BeautifulSoup(htmlPage, "html.parser")
    
            #get all links concerning google 
            for link2 in soup.findAll("a"):
                allLinks.append(link2["href"])
        allLinks.append(link)
    for allLink in allLinks:
        print(allLink)
        
if __name__ == "__main__":
    initialPage('https://www.google.com')
    extraPages() 
