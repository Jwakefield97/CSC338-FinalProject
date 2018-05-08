from multiprocessing import Process, Manager, Queue, Pool
import os 
from bs4 import BeautifulSoup
import requests
DOMAIN = "https://www.missouristate.edu"
MAINDOMAIN = DOMAIN.replace("https://www.","").replace("http://www.","")


def parsePage(urls,queue,MAINDOMAIN):
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


def output(l_list):

    file = open("output.txt","w")
    for link in l_list: 
        file.write(link + " \n")  
    file.close()   


def main(): 

    all_links = []
    count = 1
    while(count > 0):
        cpu_count = 4
        pool = Pool(processes=cpu_count)
        que = Manager().Queue() 
        links = parsePage([DOMAIN],que,MAINDOMAIN) #get inital page links
        for _ in range(que.qsize()):
            all_links.append(que.get())

        link_amount = len(all_links) // cpu_count
        
        for i in range(cpu_count):
            if i == cpu_count-1: 
                pool.apply_async(parsePage,[all_links,que,MAINDOMAIN])
                del all_links[0:]
            else:
                pool.apply_async(parsePage,[all_links[0:link_amount],que,MAINDOMAIN])
                del all_links[0:link_amount]
        pool.close()
        pool.join()

        for obj in range(que.qsize()):
            l = que.get()
            if l[len(l)-1] == "/": #remove slashes at the end of links
                l = l[:len(l)-2]
            if l not in all_links: #only allow unique links 
                all_links.append(l)

        print("length of all_links: "+str(len(all_links)))
        count -=1
    output(all_links)


if __name__ == '__main__':
    main()