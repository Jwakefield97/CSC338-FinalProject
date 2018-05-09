"""
    Group: PacMan
    Authors: Connor Jansen (cjjansen95), Eric McCullough (eam96), Jacob Wakefield (jwakefield97), John Bell (jab331)
    Assignment: CSC338 final project

    Description: A web crawler that takes an inital url from the command line and collects the links on that page. It then
                 links that are from the same origin. From those links it visits links that are from the same origin. It continues
                 this process until no more links from the starting origin are found. In other words it crawls through a website discovering
                 all of it's pages. The program does this by detecting how many cpu's the computer running it has, it then splits the initial
                 load (links) from the entry page amongst the processes which spawn threads to handle any further links that are discovered on
                 subsequent pages.
    Tech: Python 3, multiprocessing, threading, time (timing of threads/processes and overall program), sys (command line args),
          beautiful soup (parse html response), and requests (make network requests)

    Execution Flow: command line arg (entry domain) is passed to parsePage() which collects the all the links that are on the same domain.
                    The processManager() function is then called which sets up the processes based on the system cpu count and spreads
                    the links collected from  the initial page across the processes. Once the processes are initalized, they are all started.
                    Once the process is started it initializes a pool of threads to be used in the recursive link collection process.
                    Once a link is found on the same origin, a thread (one that is not busy working on another page) is used to process
                    the page and collect links (thread calls parsePage() which visits the page and processes links).
                    If all threads in the pool are busy then the process waits until a thread is freed up. Once each process is done collecting
                    /visiting the links it calls output() which waits for all processes to complete before gathering stats (execuetion time, number
                    of links etc.) and outputing all the links to a file.
"""

from bs4 import BeautifulSoup
from threading import Thread
import requests
import multiprocessing as mp
import sys
import time

DOMAIN = "" # Ex: https://www.google.com
MAINDOMAIN = DOMAIN.replace("https://www.","").replace("http://www.","")

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
        links_visited += links_to_visit
        
        for i in range(cpu_count): 
            if i == cpu_count-1: 
                pool.apply_async(parsePage,[list(links_to_visit),queue,MAINDOMAIN])
                list(links_to_visit)
                del links_to_visit[0:]
                set(links_to_visit)
            else:
                pool.apply_async(parsePage,[list(links_to_visit[0:link_amount]),queue,MAINDOMAIN])
                list(links_visited)
                del links_to_visit[0:link_amount]
                set(links_to_visit)
        pool.close()
        pool.join()

        for obj in range(queue.qsize()):
            link = queue.get()
            if link[len(link)-1] == "/": #remove slashes at the end of links
                link = link[:len(link)-2]
            if link not in links_to_visit: #only allow unique links 
                links_to_visit.add(link)

        print("length of links_to_visit: "+str(len(links_to_visit)))
        pageCount -= 1
        isFirst = False
    output(links_to_visit)


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
def output(links):
    #block for all processes to be finished.
    #then output stats about the runtime and links.
    #output all links to text file

    file = open("output.txt","w")
    for link in links: 
        file.write(link + " \n") 
    file.close()   


"""
    Description: entry point to the application. Grabs url from command line and passes it to initalPage(). After
                 the inital links are collected processManager() is called and the links are distributed amongst them.
"""
if __name__ == "__main__":
    DOMAIN = sys.argv[1]
    max_page_count = int(sys.argv[2]) #number of cycles to run the webcrawler on
    processManager(max_page_count)
