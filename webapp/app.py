# -*- coding: utf-8 -*-
"""
Created on Sun Dec 16 00:55:48 2018

@author: Kunal N Pandey
"""

from flask import Flask, render_template,request
             
app = Flask(__name__)

from bs4 import BeautifulSoup
from requests import get
import re
import matplotlib.pyplot as plt 
import numpy as np
import urllib.request
import time
import datetime

def actual_name(response):
    movie_page=BeautifulSoup(response.text, 'lxml')
    title_bar=movie_page.find('div',class_='title_wrapper')
    name=str(title_bar.find('h1').text)
    return name[0:-8]
    
    
def IMDB_rating(response):
    rating_bar=BeautifulSoup(response.text, 'lxml')
    page_text=rating_bar.find('div',class_='ratingValue')
    rating=str(page_text.find('span',itemprop='ratingValue').text)
    return rating

def rotten_tomato(response):
    page=BeautifulSoup(response.text, 'lxml')
    critics_rating_bar=page.find('div' , id="scoreStats").text
    critics_rating=critics_rating_bar[25::]
    critics_rating=critics_rating.strip()
    e1_index=critics_rating.index('/')
    aud_rating_bar=page.find('div' , class_='audience-info hidden-xs superPageFontColor').text
    aud_rating=aud_rating_bar[25::]
    aud_rating=aud_rating.strip()
    e2_index=aud_rating.index('/')
    return critics_rating[0:e1_index],aud_rating[0:e2_index]
    
def no_of_votes(response):
    movie_page=BeautifulSoup(response.text, 'lxml')
    votes=str(movie_page.find('span',itemprop='ratingCount').text)
    return votes
    
def release_year(response):
    movie_page=BeautifulSoup(response.text, 'lxml')
    try:
        year=movie_page.find('span',id='titleYear').text
        year=str(year[1:len(year)-1])
        return year
    except AttributeError:
        return "Not Available"
    
    
def imdb_cast(response):
    txt=response.text
    start = [m.start() for m in re.finditer('Stars', txt)]
    txt=txt[start[0]::]
    end = [m.start() for m in re.finditer('<span', txt)]
    txt=txt[0:end[0]]
    end = [m.start() for m in re.finditer('<a', txt)]
    txt=txt[end[0]::]
    l=[];
    while(len(txt)>0):
        try:
            end = [m.start() for m in re.finditer('>', txt)]
            txt=txt[end[0]+1::]
            end = [m.start() for m in re.finditer('<', txt)]
            l.append(txt[0:end[0]])
            end = [m.start() for m in re.finditer('<a', txt)]
            txt=txt[end[0]::]
        except IndexError:
            break
        
    return l

def wiki_cast(response):
    l=[]
    try:
        txt=response.text
        start = [m.start() for m in re.finditer('Starring', txt)]
        txt=txt[start[0]::]
        end = [m.start() for m in re.finditer('/td>', txt)]
        txt=txt[0:end[0]]
        end = [m.start() for m in re.finditer('<a', txt)]
        txt=txt[end[0]::]
        while(len(txt)>0):
            try:
                end = [m.start() for m in re.finditer('">', txt)]
                txt=txt[end[0]+2::]
                end = [m.start() for m in re.finditer('<', txt)]
                l.append(txt[0:end[0]])
                end = [m.start() for m in re.finditer('<a', txt)]
                txt=txt[end[0]::]
            except IndexError:
                break        
        return l
    except IndexError:
        return l

def box_office_wiki(response):
    s=""
    txt=response.text
    start = [m.start() for m in re.finditer('Box office', txt)]
    txt=txt[start[0]::]
    start = [m.start() for m in re.finditer('Box office', txt)]
    end = [m.start() for m in re.finditer('/td>', txt)]
    txt=txt[0:end[0]]
    txt2=""
    try:
        end = [m.start() for m in re.finditer('wrap">', txt)]
        txt=txt[end[0]+6::]
        end = [m.start() for m in re.finditer('<', txt)]
        s=s+txt[0:end[0]]
        end = [m.start() for m in re.finditer('/span>', txt)]
        txt=txt[end[0]+6::]
        txt2=txt
        end = [m.start() for m in re.finditer('<', txt)]
        txt=txt[0:end[0]]
        s=s+" "+txt
    except IndexError:
        start = [m.start() for m in re.finditer('<td>', txt)]
        txt=txt[start[0]+4::]
        end=[m.start() for m in re.finditer('<', txt)]
        s=s+txt[0:end[0]]
    s.strip()
    if (len(s)<=8):
        try:
            end = [m.start() for m in re.finditer('/span>', txt2)]
            txt2=txt2[end[0]+6::]
            end = [m.start() for m in re.finditer('<', txt2)]
            txt2=txt2[0:end[0]]
        except IndexError:
            txt2=txt2.strip()
            
        s=s+" "+txt2
        
    return s

def box_office_imdb(response):
    try:
        txt=response.text
        start = [m.start() for m in re.finditer('Worldwide Gross:', txt)]
        txt=txt[start[0]::]
        end = [m.start() for m in re.finditer('/div>', txt)]
        txt=txt[22:end[0]]
        end=[m.start() for m in re.finditer('<', txt)]
        txt=txt[0:end[0]]
        txt.strip()
        return txt
    except IndexError:
        s=""
        return s
def get_other_details(response):
    li=[]
    page=BeautifulSoup(response.text,'lxml')
    details=(page.find('div',class_="subtext")).text
    for i in range(0,3):
        index=details.find('|')
        s=details[0:index].strip()
        s=s.replace("\n","")
        if(len(li)==0):
            if(s[0]=='1'):
                li.append('UA')
            elif(s[0]=='2'):
                li.append('UA')
        li.append(s)
        details=details[index+1::]   
    return li

def get_poster_array(response):
    txt=response.text
    start = [m.start() for m in re.finditer('class="poster"', txt)]
    txt=txt[start[0]::]
    end = [m.start() for m in re.finditer('</a>', txt)]
    txt=txt[0:end[0]]
    start = [m.start() for m in re.finditer('src="', txt)]
    txt=txt[start[0]+5::]
    end=[m.start() for m in re.finditer('" />', txt)]
    txt=txt[0:end[0]]
    resource=urllib.request.urlopen(txt)
    output = open("static/file01.jpg","wb")
    output.write(resource.read())
    output.close()
    '''
    img=plt.imread('/static/file01.jpg',1)
    plt.axis('off')
    plt.title("Poster of " +title)
    plt.imshow(img)
    plt.show()
    return img
    '''
def show_poster(img,title):
    plt.axis('off')
    plt.title("Poster of " +title)
    plt.imshow(img)
    plt.show()
    

    
def get_link(movie_name,key,z):
    url="https://in.search.yahoo.com/search?p="+movie_name+"+"+key
    response=get(url)
    html_soup=BeautifulSoup(response.text, 'lxml')
    page_link=""
    for link in html_soup.find_all('a',href=True): 
        if z in link['href']:  
            page_link=link['href']
            break
    return page_link

def bar_plot(name,rating,title,max_limit):
    x = np.arange(len(name))
    plt.title(title)
    plt.xticks(x, name)
    plt.ylabel("Rating")
    plt.ylim(0,max_limit,1)
    barlist=plt.bar(x, rating)
    plt.grid(1,'major','y')
    for i in range(0,len(barlist)):
        if(rating[i]/max_limit<0.65):
            barlist[i].set_color('r')
        elif(rating[i]/max_limit>=0.8):
            barlist[i].set_color('g')
        else:
            barlist[i].set_color('y')
    for a,b in zip(x, rating):
        plt.text(a, b, str(b)[0:3], fontsize=10)
    plt.show()
    
    
def movieDetail(s):
    msg=""
    imdb_rating=[]
    rot_tom_critics=[]
    rot_tom_audience=[]
    average_rating=[]
    name=[]
    poster=[]
    li=list(map(str,s.split(',')))
    #li=['The GodFather','Boss(Hindi)' ,'P K']
    f=0
    for movie in li: 
            
        imdb_page_link=get_link(movie,"movie+imdb","www.imdb.com")
        wiki_page_link=get_link(movie,"movie+wikipedia" , 'https://en.wikipedia.org' )
        rotten_tomato_page_link=get_link(movie,"movie+rotten+tomato" ,'https://www.rottentomatoes.com')
        response_1=get(imdb_page_link)
    
        response_2=get(wiki_page_link)
        
        response_3=get(rotten_tomato_page_link)
        
        
        act_name=actual_name(response_1)
        poster.append(get_poster_array(response_1))
        
        name.append(act_name)
        msg=msg+"\nMovie Name : " +act_name
        
        year=release_year(response_1)
        msg=msg+"\nRelease Year : " +year
        
        
        rating=IMDB_rating(response_1)
        votes=no_of_votes(response_1)        
        msg=msg+"\nIMDB Rating : "+str(rating)+"/10 (based on "+str(votes)+" votes)"
        imdb_rating.append(float(rating))
        
        try:
            critics,audience=rotten_tomato(response_3)
            rot_tom_critics.append(float(critics))
            rot_tom_audience.append(float(audience))
            average_rating.append((float(rating)+float(critics)+float(audience)*2)/3)
            msg=msg+"\nRotten Tomato Critics rating : "+critics+"/10"
            msg=msg+"\nRotten Tomato Audience rating : "+audience+"/5"
        except AttributeError:
            f=1
        
        lis=get_other_details(response_1)
        if(len(lis)>=3):
            msg=msg+"\nGenre : "+lis[2]    
            msg=msg+"\nCertificate : "+lis[0]
            msg=msg+"\nDuration : "+lis[1]
        
        collection=box_office_imdb(response_1)
        if(len(collection)==0):
            try:    
                collection=box_office_wiki(response_2)
                if(len(collection)>8):
                    msg=msg+"\nBox Office Collection : "+collection
                else:
                    msg=msg+"\nBox Office Collection : Not Available"
            except IndexError:
                msg=msg+"\nBox Office Collection : Not Available"
        else:
            msg=msg+"\nBox Office Collection : "+collection
        
        starring_1=imdb_cast(response_1)
        starring_2=wiki_cast(response_2)
        starring=starring_1 + list(set(starring_2) - set(starring_1))
        msg=msg+"\nStarring : "
        for i in range(len(starring)):
           msg=msg+"\n"+str(i+1)+'.'+starring[i]
           
        msg=msg+"\n\n\n"
    '''
    if(len(li)>=2):
        if f==0:
            bar_plot(name,imdb_rating,"IMDB Rating",10)
            bar_plot(name,rot_tom_critics,"Critics Rating(Rotten Tomato)",10)
            bar_plot(name,rot_tom_audience,"Audience Rating(Rotten Tomato)",5)
            bar_plot(name,average_rating,"Average Rating(Based on IMDB and Rotten Tomato)",10)
        else:
            bar_plot(name,imdb_rating,"IMDB Rating",10)

        s=input("Do you want the posters of your Queried Movies?\n")
        s=s.lower()
        if(s=="yes"):
            for i in range(len(poster)):
                show_poster(poster[i],name[i])
    else:
        show_poster(poster[0],name[0])

    print("Hint-If You are not getting the desired result try searching \n\twith including the original language of the movie")
    '''
    return msg

def seriesDetail(s):
    myresult = list(map(str,s.split(',')))
    message=""  
    for x in myresult:
        s=""
        for i in range(len(x)):
            if(x[i]==" "):
                s=s+"+"
            else:
                s=s+""+x[i]
        s=s+"+Tv+Series+imdb"
        url1="https://in.search.yahoo.com/search?p="+s
        response1=get(url1)    
        url2=""      
        html_soup1 = BeautifulSoup(response1.text, 'lxml')
        for link in html_soup1.find_all('a',href=True): 
            z="www.imdb.com"
            if z in link['href']:  
                url2=link['href']
                break
        #now opening the link stored in url2
        response2=get(url2)
        html_soup2 = BeautifulSoup(response2.text, 'lxml')
        url3="https://www.imdb.com"
        search_containers = html_soup2.find('div', class_ = 'seasons-and-year-nav')
        link=search_containers.find('a',href=True) #finding the first link in search Container
        url3=url3+link['href']  #url3 is the link to the page which contains information about episodes and seasons

        first_series=""
        response=get(url3)
        html_soup = BeautifulSoup(response.text, 'lxml')
        
        odd_movie_containers = html_soup.find_all('div', class_ = 'list_item odd')
        even_movie_containers = html_soup.find_all('div', class_ = 'list_item even')
        
        index_odd=0    
        index_even=0
        index=0
        
        dic={"Jan.":"01","Feb.":"02","Mar.":"03","Apr.":"04","May.":"05","May":"05","Jun.":"06","Jul.":"07","Aug.":"08","Sep.":"09","Oct.":"10","Nov.":"11","Dec.":"12"}
        message=message+"TV Series : "+x+"\n"  #storing TV series Name
        
        while(index<len(odd_movie_containers)+len(even_movie_containers)):
            date=""
            if((index+1)%2!=0 & index_odd<len(odd_movie_containers)):
                first_series=odd_movie_containers[index_odd]
                first_year = first_series.find('div', class_ = 'airdate')
                date=str(first_year.text)
                index_odd=index_odd+1
            elif((index+1)%2==0 & index_even<len(even_movie_containers)):
                first_series=even_movie_containers[index_even]
                first_year = first_series.find('div', class_ = 'airdate')
                date=str(first_year.text)
                index_even=index_even+1
            date=date.strip()
            
            if(len(date)==0):
                message=message+"Status: All the seasons are finished and no further details are available"+"\n\n"
                break
            else:
                if(len(date)>12):
                    date=date[-12:]
                actual_date=date
                if(len(date)==12):
                    s=date[3:7]   
                    date1=date[0]+date[1]+"/"+dic[s]+"/"+date[8:]
                    date=date1
                elif(len(date)==11):
                    s=date[3:6]
                    if(s=="May"):
                        date=date[0]+date[1]+"/"+dic[s]+"/"+date[7:]
                    else:
                        date="0"+date
                        s=date[3:7]
                        date=date[0]+date[1]+"/"+dic[s]+"/"+date[8:]
                elif(len(date)==10):
                    s=date[2:5]
                    date="0"+date[0]+"/"+dic[s]+"/"+date[6:]
                elif(len(date)==4):           
                    date="01/01/"+date
            
                new_date = time.strptime(date, "%d/%m/%Y")
                present_date=str(time.strftime("%d/%m/%Y"))
                present_date=time.strptime(present_date,"%d/%m/%Y")
                if(new_date>=present_date):
                    if(len(actual_date)==4):
                        message=message+"Status: The next season begins in "+str(actual_date)+"\n\n\n"
                        break
                    else:
                        message=message+"Status: Next episode airs on 20"+date[8:]+"-"+date[3:5]+"-"+date[0:2]+"\n\n"
                        break
                index=index+1             
        
        if(index==len(odd_movie_containers)+len(even_movie_containers)):
          message=message+"Status: All the seasons are finished and no further details are available"+"\n\n"
          
    return message

@app.route("/" , methods=["GET", "POST"])    
def home():
    if request.method == "POST":
        s = request.form["movieName"]
        
        if len(s)>0:
            result = movieDetail(s)
            return render_template("result.html",result=result)

    return render_template("home.html")

@app.route("/episodeTracker" , methods=["GET", "POST"])    
def tvSeries():
    if request.method == "POST":
        s = request.form["seriesName"]
        
        if len(s)>0:
            result = seriesDetail(s)
            return render_template("seriesResult.html",result=result)

    return render_template("series.html")

if __name__ == "__main__":
    app.run(debug=True)