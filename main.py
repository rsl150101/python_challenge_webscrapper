import os, csv, requests
from bs4 import BeautifulSoup

os.system("cls")
alba_url = "http://www.alba.co.kr"

url = requests.get(alba_url)
soup = BeautifulSoup(url.text, "html.parser")    
max_job_count = 50

def search_company():
    goodsbox = soup.find("div", {"id" : "MainSuperBrand"})
    brands = goodsbox.find_all("li", {"class" : "impact"})
    company_and_link = {}
    for brand in brands:
        company_and_link[brand.find("span", {"class" : "company"}).string.replace("/", "_")] = brand.find("a")["href"]
    return company_and_link

def last_page(link):
    url = requests.get(link)
    soup = BeautifulSoup(url.text, "html.parser")
    
    job_count = int(soup.find("div", {"class": "goodsList"}).find("strong").string.replace(",", ""))
    page = int(job_count/max_job_count)

    if job_count%max_job_count == 0:
        page = page
    else:
        page = page + 1
    return page

def job_brand_data(info):
    place = info.find("td", {"class" : "local"}).get_text()
    title =  info.find("span", {"class" : "company"}).get_text()
    time = info.find("td", {"class" : "data"}).find("span").get_text()
    pay = info.find("span", {"class" : "number"}).get_text()
    date = info.find("td", {"class" : "regDate"}).get_text()
    return [place, title, time, pay, date]

def job_brand_info(dict):
    jobs_dict = {}
    for company, links in dict.items():
        jobs = []
        pages = last_page(links)
        
        if pages == 0 :
            jobs_dict[company] = "채용공고가 없습니다."
            continue

        for page in range(pages):
            page = page + 1
            link = f"{links}job/brand/?page={page}&pagesize=50"
            url = requests.get(link)
            soup = BeautifulSoup(url.text, "html.parser")
            
            try:
                job_info = soup.find("div", {"class" : "goodsList"}).find_all("tr")
            except:
                link = f"{links}?page={page}&pagesize=50"
                url = requests.get(link)
                soup = BeautifulSoup(url.text, "html.parser")
                job_info = soup.find("div", {"class" : "goodsList"}).find_all("tr")
            
            for info in job_info[1::2]:
                job = job_brand_data(info)
                jobs.append(job)
        jobs_dict[company] = jobs
    return jobs_dict
    
def create_csv(dict):
    for company in dict.keys():
        file = open(f"{company}.csv", mode="w", encoding = "utf-8", newline="")
        writer = csv.writer(file)
        writer.writerow(["place", "title", "time", "pay", "date"])
        for job in range(len(dict[company])):
            writer.writerow(dict[company][job])
    return

brand_name_link = search_company()
brand_job = job_brand_info(brand_name_link)
create_csv(brand_job)