from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By 
from selenium.webdriver.common.keys import Keys
import argparse 
import time
import requests
from requests_html import HTMLSession
from bs4 import BeautifulSoup
import re
from geopy.geocoders import Nominatim

service = Service()
options = Options() 
options.add_argument('--headless')
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
# Objeto webdriver
browser = webdriver.Chrome(service=service,options=options)
#OBJETO
links = list()
lists = []
webs = str
tel = str
html =""
scroll = True
query = ""
i=0
locs = Nominatim(user_agent="Geopy Library")
emails = set()
session = HTMLSession()

def scrape_buttons_in_website(url):
    response = session.get(url) # send a GET request to the url
    soup = BeautifulSoup(response.content, 'html.parser') # extract the html content

    data = str(soup.find_all('a')) # find all <a> tags
    matches = []

    # Extract links from the HTML content
    for match in re.finditer('href="/', data):
        find = data[match.start() + 6:match.end() + 30]
        find = find[:find.find('"')].strip()
        
        # Construct the final URL
        if find != "/":
            final_url = f'{url}{find}'
            matches.append(final_url)

    return matches

def scrape_email_from_website(url):
    matches = scrape_buttons_in_website(url)
    # Iterate through the links and scrape emails
    for link in matches:
        try:
            response = session.get(link)
            soup = BeautifulSoup(response.content, 'html.parser')
            email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
            emails.update(set(re.findall(email_pattern, soup.get_text())))
        except Exception as e:
            print(f'Error: {e}')
            continue

    return list(emails)

class Servicio:
    def __init__(self, nombre, link, webs, dir,email,telefono,sociales):
        self.nombre=nombre
        self.link=link
        self.webs=webs
        self.dir=dir
        self.email=email
        self.telefono=telefono
        self.sociales=sociales

    def __str__(self):
        return f"Nombre={self.nombre}, Maps Link={self.link}, Página web={self.webs}, Dirección={self.dir}, Email={self.email}, Sociales={self.telefono}"
    
def loc(n):
    n.replace(" ","+")

def pl(pls):
    return pls


# Url de google maps
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Buscar en maps")
    parser.add_argument('--loc', help='Empresa a buscar')
    parser.add_argument('--pl',help="Lugar de búsqueda",nargs='+')
    args = parser.parse_args()

if args.loc:
    with open('Maps.txt','w') as f:    
        loc(args.loc)
        l=" ".join(pl(args.pl))
        getLoc = locs.geocode(l)
        url = "https://www.google.com/maps/search/"+args.loc+"/@"+str(getLoc.latitude)+","+str(getLoc.longitude)+",12z/data=!4m2!2m1!6e5?authuser=0&hl=en&entry=ttu&g_ep=EgoyMDI0MTIwNC4wIKXMDSoASAFQAw%3D%3D"
        browser.get(url)
        divSideBar=browser.find_element(By.XPATH,f'//*[@aria-label="Results for {args.loc}"]')
        #Buscamos el link de maps de cada elemento(map).
        while(scroll):
            title = browser.find_elements(By.TAG_NAME,"a")
            divSideBar.send_keys(Keys.PAGE_DOWN)
            try:
                html=browser.find_element(By.CLASS_NAME, 'HlvSq').text
            except Exception as e:
                html
            if(html=="You've reached the end of the list."):
                scroll=False
        #Itera en los links.
        for pepe in title:
            try: 
                stars = pepe.get_attribute("href")
                links.append(stars)
            except Exception as e:
                print("No se econtró\n")

        #Empieza a scrappear los links.        
        while len(links)>1: 
            x = links.pop()
            browser.get(x)
            time.sleep(2)
            #Conseguir nombre
            try:
                title = browser.find_element(By.CLASS_NAME, "DUwDvf.lfPIob")
                nombre = title.text
            except Exception as e:
                nombre = "NONAME"

            #Conseguir Telefono
            try:
                title = browser.find_element(By.XPATH,'//button[@data-tooltip="Copy phone number"]')
                tel = title.get_attribute("data-item-id")
                tel = tel.replace("phone:tel:","")
            except Exception as e:
                tel ="No tiene telefono"
            
            #Por ahora sociales se mantiene con lo de la web.
            sociales = "Sin sociales."
            #

            #Conseguir web
            title = browser.find_elements(By.TAG_NAME,"a")
            webs = "Sin página web."
            for pepe in title:
                try:
                    if(pepe.get_attribute("data-tooltip") == "Open website"):
                        stars = pepe.get_attribute("href")
                        webs = stars
                except Exception as e:
                    webs = "Sin página web"

            if (webs.find("instagram") or webs.find("facebook")):
                sociales = webs
                webs = "Sin página web."

            #Conseguir Locación
            try:
                loca = browser.find_element(By.CLASS_NAME,"Io6YTe.fontBodyMedium.kR99db.fdkmkc").text
            except Exception as e:
                loca = "NADA"
            
            #Conseguir el email desde su página web
            try:
                result = scrape_email_from_website(webs)
                y = emails.pop()
            except Exception as e:
                y = "Sin email."
            if (nombre != "NONAME"):
                lists.append(Servicio(nombre,x,webs,loca,y,tel,sociales))
                f.write("Nombre= %s\n Maps Link= %s\n Página web= %s\n Dirección= %s\n Email= %s\n Telefono= %s\n Sociales= %s \n\n"%(nombre,x,webs,loca,y,tel,sociales))