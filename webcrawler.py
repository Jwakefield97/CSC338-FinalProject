"""
    Group: PacMan
    Authors: Connor Jansen (cjjansen95), Eric McCullough (eam96), Jacob Wakefield (jwakefield97), John Bell (jabell331)
    Assignment: CSC338 final project

    Description: A web crawler that takes an inital url from the command line and collects the links on that page. It then breaks those links up amongst 
                 the number of cpu's in the computer. After the processes join, if the cycles that the users selected via command line argument, the 
                 process of spliting the links up and spawning processes starts again on the freshly found links. Once the cycles are reached, the links
                 that were visited are placed into a text file (output.txt) and the total execuetion time is printed. 
    Tech: Python 3, multiprocessing, threading, time (timing of threads/processes and overall program), sys (command line args),
          beautiful soup (parse html response), and requests (make network requests)
    Libraries to install: beautifulsoup4 and requests. All other libraries used come with python3.
    How to use: py https://domaintovisit.com <number of cycles>
                cycles are how many times you want the crawler to break up the links found and spawn processes to visit those links. 
"""

from bs4 import BeautifulSoup
from threading import Thread
import requests
import multiprocessing as mp
import sys
import time

DOMAIN = "" # Ex: https://www.google.com
MAINDOMAIN = DOMAIN.replace("https://www.","").replace("http://www.","")
STARTTIME = time.time()

"""
    Description: get number of cpus and setup/manage processes.
"""
def processManager(pageCount):
    #get number of cpus
    #spawn the process with the threadManager as the function to execute
    #start the processes
    links_visited = set()
    cpu_count = mp.cpu_count()
    isFirst = True
    while(pageCount > 0):
        links_to_visit = set()
        pool = mp.Pool(processes=cpu_count) #create pool
        queue = mp.Manager().Queue() #create queue

        if isFirst: #if it is the first cycle through get the inital links 
            links = parsePage([DOMAIN],queue,MAINDOMAIN) #get inital page links

            for _ in range(queue.qsize()): #populate links_to_visit with queue results 
                links_to_visit.add(queue.get())

        link_amount = len(links_to_visit) // cpu_count
        links_visited = links_visited.union(links_to_visit)
        
        local_links_to_visit = list(links_to_visit) #conversion from set to list
        for i in range(cpu_count): 
            if i == cpu_count-1: 
                pool.apply_async(parsePage,[local_links_to_visit,queue,MAINDOMAIN])
                del local_links_to_visit[0:]
            else:
                pool.apply_async(parsePage,[local_links_to_visit[0:link_amount],queue,MAINDOMAIN])
                del local_links_to_visit[0:link_amount]
        pool.close()
        pool.join()
        for obj in range(queue.qsize()):
            link = queue.get()
            if link[len(link)-1] == "/": #remove slashes at the end of links
                link = link[:len(link)-2]
            if link not in links_visited:  #if have not visited yet 
                links_to_visit.add(link)#only allow unique links

        pageCount -= 1
        isFirst = False
    output(list(links_visited))


"""
    Description: visit page distributed by inital page using a thread of the processes. This function gets
                 gets called by the threads.
"""
def parsePage(urls,queue,MAINDOMAIN):
    #visit url and parse the return html.
    #if the links contains the domain and aren't in URLS_VISITED (acquire lock for list), acquire the lock
    #for URLS_TO_VISIT and push the valid link to the list. 
    #don't forget to release all locks after using them and try catch any network request or parsing. k 
   
    for url in urls: 
        try:
            with requests.get(url) as html: #get page and parse 
                htmlPage = html.content 
                soup = BeautifulSoup(htmlPage, "html.parser")
                
                for link in soup.findAll("a"): #loop through links 
                    try:
                        if(MAINDOMAIN in link['href'] or link['href'][0] == '/'): #if it is on the same domain append url 
                      
                            if(link["href"][0] == "/"):
                                queue.put(DOMAIN+link["href"])
                            else:
                                queue.put(link["href"])
                    except:
                        print("no href error ignored") 
        except:
            print("network error ignored")

"""
    Description: block for processes and threads to end then display stats/output links to a file.
"""
def output(links_visited):
    #block for all processes to be finished.
    #then output stats about the runtime and links.
    #output all links to text file
    file = open("output.txt","w")
    for link in links_visited: 
        file.write(link + " \n") 
    file.close()
    print("--- %s seconds ---" % (time.time() - STARTTIME))


"""
    Description: entry point to the application. Grabs url from command line and passes it to initalPage(). After
                 the inital links are collected processManager() is called and the links are distributed amongst them.
"""
if __name__ == "__main__":
    DOMAIN = sys.argv[1]
    max_page_count = int(sys.argv[2]) #number of cycles to run the webcrawler on
    processManager(max_page_count)
