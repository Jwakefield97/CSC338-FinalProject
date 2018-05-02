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
import os 

DOMAIN = "" # Ex: https://www.google.com
MAX_PAGE_COUNT = 1000 #max number of threads the user wants to limit each process to.
THREADS_IN_USE = [] #threads that are currently working
URLS_TO_VISIT = mp.Queue() #urls to be visited
URLS_VISITED = [] #urls that have been visited

"""
    Description: get number of cpus and setup/manage processes.
"""
def processManager():
    #get number of cpus
    #spawn the process with the threadManager as the function to execute
    #start the processes
    cpu_count = mp.cpu_count()

    while len(URLS_VISITED) < MAX_PAGE_COUNT and URLS_TO_VISIT.qsize() > 0:
        processes = []
        number_of_pages = URLS_TO_VISIT.qsize() // cpu_count
        balanced_number_of_pages = URLS_TO_VISIT.qsize()//cpu_count + URLS_TO_VISIT.qsize()%cpu_count
        for i in range(cpu_count):
            local_links = []
            if i < cpu_count:
                for i in range(number_of_pages):
                    local_links.append(URLS_TO_VISIT.get())
                p = mp.Process(target = parsePage, args = [local_links])
                p.start()
            else:
                for i in range(balanced_number_of_pages):
                    local_links.append(URLS_TO_VISIT.get())
                p = mp.Process(target = parsePage, args = [local_links])
                p.start()
        exit = [p.wait() for p in processes]
        for p in processes:
            p.wait()

    output()
"""
    Description: function that spawns the threads for the process and manages the threads. Uses a set number
                 threads (thread pool).
"""
def threadManager():
    #if the max thread count hasn't been reached, acquire a lock to access URLS_TO_VISIT,
    #while if URLS_TO_VISIT isn't empty, grab URLS_TO_VISIT[0] remove it from the list, acquire the lock
    #to access URLS_VISITED and push URLS_TO_VISIT[0].
    #spawn a new thread to visit the url. Don't forget to release all locks after access the info needed.
    pass


"""
    Description: visit page distributed by inital page using a thread of the processes. This function gets
                 gets called by the threads.
"""
def parsePage(urls):
    #visit url and parse the return html.
    #if the links contains the domain and aren't in URLS_VISITED (acquire lock for list), acquire the lock
    #for URLS_TO_VISIT and push the valid link to the list. 
    #don't forget to release all locks after using them and try catch any network request or parsing. k 
    print(os.getpid())
    print(URLS_TO_VISIT)
    for url in urls: 
        try:
            with requests.get(url) as html: #get page and parse 
                htmlPage = html.content 
                soup = BeautifulSoup(htmlPage, "html.parser")
                
                for link in soup.findAll("a"): #loop through links 
                    try:
                        if(DOMAIN in link['href']): #if it is on the same domain append url 
                            URLS_TO_VISIT.put(link["href"])
                    except:
                        print("no href error occured") 
        except:
            print("network error occured")

"""
    Description: block for processes and threads to end then display stats/output links to a file.
"""
def output():
    print(len(URLS_VISITED))
    print(len(URLS_TO_VISIT))
    #block for all processes to be finished.
    #then output stats about the runtime and links.
    #output all links to text file
    file = open("output.txt","w")
    for link in URLS_TO_VISIT: 
        file.write(link + " \n") 
    for link in URLS_VISITED: 
        file.write(link + " \n") 
    file.close()   



"""
    Description: entry point to the application. Grabs url from command line and passes it to initalPage(). After
                 the inital links are collected processManager() is called and the links are distributed amongst them.
"""
if __name__ == "__main__":
    DOMAIN = sys.argv[1]
    MAX_PAGE_COUNT = int(sys.argv[2]) #get thread pool size from command line
    parsePage([DOMAIN])
    processManager()
