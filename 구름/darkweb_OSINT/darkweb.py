import subprocess
import requests
from bs4 import BeautifulSoup
import time
from stem import Signal
from stem.control import Controller
import logging
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from pymongo import MongoClient
from datetime import datetime

# 로그 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.StreamHandler()])

TOR_PATH = r"C:\Users\Laiika\Desktop\Tor Browser\Browser\TorBrowser\Tor\tor.exe"

text2 = """Algeria Angola Benin Botswana Burkina Burundi Cameroon CapeVerde CentralAfricanRepublic Chad Comoros Congo DemocraticRepublicofCongo Djibouti Egypt EquatorialGuinea Eritrea Ethiopia Gabon Gambia Ghana Guinea GuineaBissau IvoryCoast Kenya Lesotho Liberia Libya Madagascar Malawi Mali Mauritania Mauritius Morocco Mozambique Namibia Niger Nigeria Rwanda SaoTomeandPrincipe Senegal Seychelles SierraLeone Somalia SouthAfrica SouthSudan Sudan Swaziland Tanzania Togo Tunisia Uganda Zambia Zimbabwe Afghanistan Bahrain Bangladesh Brunei Burma Myanmar Cambodia China EastTimor India Indonesia Iran Iraq Japan Jordan Kazakhstan NorthKorea SouthKorea Kuwait Kyrgyzstan Laos Lebanon Malaysia Maldives Mongolia Nepal Oman Pakistan Philippines Qatar Russia RussianFederation SaudiArabia Singapore SriLanka Syria Tajikistan Thailand Turkmenistan UnitedArabEmirates Uzbekistan Vietnam Yemen Albania Armenia Austria Azerbaijan Belarus Belgium Bulgaria Croatia Cyprus CzechRepublic Denmark Estonia Finland France Georgia Germany Greece Hungary Iceland Ireland Italy Latvia Liechtenstein Lithuania Luxembourg Macedonia Malta Moldova Monaco Montenegro Netherlands Norway Poland Portugal Romania SanMarino Serbia Slovakia Slovenia Sweden Switzerland Ukraine UnitedKingdom VaticanCity Australia Fiji Kiribati MarshallIslands Micronesia Nauru NewZealand Palau PapuaNewGuinea Samoa SolomonIslands Tonga VanuatuSouth America Argentina Bolivia Brazil Chile Colombia Ecuador Guyana Paraguay Peru Suriname Uruguay Venezuela AntiguaandBarbuda Bahamas Barbados Belize Canada CostaRica Cuba Dominica DominicanRepublic ElSalvador Grenada Guatemala Haiti Honduras Jamaica Mexico Nicaragua Panama SaintKittsandNevis SaintLucia SaintVincentandtheGrenadines TrinidadandTobago UnitedStates"""

# 전역 Tor 컨트롤러
controller = None

def start_tor():
    global controller
    try:
        logging.info("Starting Tor process...")
        tor_process = subprocess.Popen([TOR_PATH], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(10)  # Tor 서비스가 완전히 시작될 때까지 대기
        logging.info("Tor process started.")
        # Tor 컨트롤러 연결
        controller = Controller.from_port(port=9051)
        controller.authenticate()
        return tor_process
    except Exception as e:
        logging.error(f"Error starting Tor: {e}")
        return None

def stop_tor(tor_process):
    global controller
    if tor_process:
        logging.info("Stopping Tor process...")
        tor_process.terminate()
        tor_process.wait()
        logging.info("Tor process stopped.")
    if controller:
        logging.info("Closing Tor controller...")
        controller.close()
        controller = None

def renew_tor_ip():
    global controller
    """
    Tor 네트워크에 새로운 IP 주소를 요청하여 IP를 갱신하는 함수.
    """
    logging.info("Renewing Tor IP...")
    try:
        controller.signal(Signal.NEWNYM)
        time.sleep(5)  # IP 갱신 후 잠시 대기
        logging.info("Tor IP renewed.")
    except Exception as e:
        logging.error(f"Error renewing Tor IP: {e}")

def get_html(url):
    """
    URL에서 HTML을 가져오는 함수. 가져오는 데 실패하면 Tor 노드 서킷을 갱신하고 다시 시도.
    """
    while True:
        try:
            session = requests.Session()
            session.proxies = {
                'http': 'socks5h://127.0.0.1:9050',
                'https': 'socks5h://127.0.0.1:9050'
            }
            response = session.get(url, timeout=60)  # 타임아웃 60초로 설정
            response.raise_for_status()
            logging.info(f"Fetched {url} successfully.")
            return response.text
        except requests.RequestException as e:
            logging.error(f"Error fetching {url}: {e}")
            logging.info("Retrying...")
            renew_tor_ip()  # Tor IP 갱신
            time.sleep(5)  # 5초 대기 후 다시 시도

def parse_homepage(html):
    soup = BeautifulSoup(html, 'html.parser')
    post_links = []

    for th in soup.find_all('th', class_='News'):
        onclick_value = th.get('onclick', '')
        match = re.search(r"viewtopic\('([^']+)'\)", onclick_value)
        if match:
            post_id = match.group(1)
            post_link = f"http://mbrlkbtq5jonaqkurjwmxftytyn2ethqvbxfu4rgjbkkknndqwae6byd.onion/topic.php?id={post_id}"
            post_links.append(post_link)

    logging.info(f"Found {len(post_links)} post links on homepage.")
    return post_links

def save_html(identifier, html, prefix="page"):
    filename = f"{prefix}_{identifier}.html"
    with open(filename, 'w', encoding='utf-8') as file:
        file.write(html)
    logging.info(f"HTML saved to {filename}")

def save_html_to_mongodb(filename, html):
    try:
        logging.info(f"Connecting to MongoDB to save HTML content: {filename}")
        client = MongoClient('mongodb://localhost:27017/')
        db = client['darkweb']
        
        # 현재 날짜 확인
        current_date = datetime.now().strftime('%Y-%m-%d')
        collection = db[current_date]
        
        data_dict = {
            'filename': filename,
            'html_content': html,
            'date_saved': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        # HTML 내용 저장
        logging.info(f"Inserting HTML content for {filename}")
        collection.update_one(
            {'filename': data_dict['filename']},
            {'$set': data_dict},
            upsert=True
        )
        
        logging.info(f"HTML content for {filename} saved to MongoDB successfully.")
        client.close()

    except Exception as e:
        logging.error(f"Error connecting to MongoDB or saving HTML content: {e}")

def scrape_post(url):
    logging.info(f"Fetching post: {url}")
    html = get_html(url)
    if html:
        # 파일명으로 사용할 게시물 ID 추출
        post_id = url.split('=')[-1]
        save_html(post_id, html, prefix="post")
        save_html_to_mongodb(f"post_{post_id}.html", html)  # MongoDB에 HTML 내용 저장
    else:
        logging.error(f"Failed to fetch post: {url}")

def scrape_site(base_url):
    all_urls = []
    page_number = 1
    tor_process = start_tor()

    try:
        # 첫 페이지에서 마지막 페이지 번호를 찾기
        initial_page_url = f"{base_url}index.php?page={page_number}"
        logging.info(f"Fetching {initial_page_url}...")
        initial_html = get_html(initial_page_url)
        if not initial_html:
            stop_tor(tor_process)
            return all_urls

        save_html(page_number, initial_html)
        save_html_to_mongodb(f"page_{page_number}.html", initial_html)  # MongoDB에 HTML 내용 저장
        last_page_number = parse_last_page_number(initial_html)
        logging.info(f"Last page number found: {last_page_number}")

        while page_number <= last_page_number:
            page_url = f"{base_url}index.php?page={page_number}"
            logging.info(f"Fetching {page_url}...")
            html = get_html(page_url)
            if not html:
                break

            # 페이지 HTML 저장
            save_html(page_number, html)
            save_html_to_mongodb(f"page_{page_number}.html", html)  # MongoDB에 HTML 내용 저장

            post_links = parse_homepage(html)
            all_urls.extend(post_links)

            if not post_links:
                logging.info("No more post links found, ending crawl.")
                break

            # 각 게시글 크롤링 (멀티스레드 사용)
            with ThreadPoolExecutor(max_workers=12) as executor:
                futures = [executor.submit(scrape_post, post_url) for post_url in post_links]
                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        logging.error(f"Error scraping post: {e}")

            page_number += 1
            time.sleep(10)
            renew_tor_ip()

    except Exception as e:
        logging.error(f"Error during scraping site: {e}")

    finally:
        stop_tor(tor_process)
    return all_urls

def parse_last_page_number(html):
    soup = BeautifulSoup(html, 'html.parser')
    last_page = 1

    for span in soup.find_all('span', class_='Page'):
        onclick_value = span.get('onclick', '')
        match = re.search(r"goto_page\('(\d+)'\)", onclick_value)
        if match:
            page_number = int(match.group(1))
            if page_number > last_page:
                last_page = page_number

    return last_page

# HTML 파싱 함수
def parse_page(html):
    if html is None:
        logging.error("Cannot parse NoneType HTML.")
        return None

    try:
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text()
        cleaned_text = remove_emoji(text)
        par_com, par_con, par_url, par_add, par_pub = parse_company_info(cleaned_text)
        leakinfo = []
        for i in range(len(par_com)):
            leakinfo.append({
                "company": par_com[i],
                "country": par_con[i],
                "url": par_url[i],
                "added_date": par_add[i],
                "publication_date": par_pub[i]
            })
            logging.info(f"Leak info: {leakinfo[i]}")
        
        save_to_mongodb(leakinfo)  # MongoDB에 데이터 저장
        logging.info(f"Text: {text}")

        return text
    except Exception as e:
        logging.error(f"Error parsing HTML: {e}")
        return None

def parse_company_info(text):
    companies = []
    country_names = []
    url = []
    added_dates = []
    publication_dates = []
    i = 0
    added_pattern = r"added: (\d{4}-\d{2}-\d{2})"
    publication_date_pattern = r"publication date: (\d{4}-\d{2}-\d{2})"
    lines = re.split(r'(\d+ DAYS BEFORE PUBLICATION|to their data.|\d+PUBLISHED FULL|\d+PUBLISHED)', text)
    result = []

    for i in range(len(lines)):
        if i % 2 == 0:
            result.append(lines[i])
        else:
            result[-1] += lines[i]
    lines = []
    for line in result:
        line = line.strip()
        if line:
            lines.append(line)
    del lines[0]
    del lines[-1]

    for line in lines:
        lines1 = line. split('www')
        added_date = re.search(added_pattern, line)
        publication_date = re.search(publication_date_pattern, line)
        if added_date:
            added_dates.append(added_date.group(1))

        if publication_date:
            publication_dates.append(publication_date.group(1))
        after = lines1[1].split(' ')
        before = lines1[0].split(' ')
        url.append('www'+after[0])
        before = remove_null(before)
        if find_common_words1(before[-1],text2) != False:
            country_names.append(before[-1])
            companies.append(sum_company(before,1))
        elif find_common_words2(before[-2],before[-1],text2) != False:
            country_names.append(before[-2]+" "+before[-1])
            companies.append(sum_company(before, 2))
        elif find_common_words3(before[-3],before[-2],before[-1],text2) != False:
            country_names.append(before[-3]+" "+before[-2]+" "+before[-1])
            companies.append(sum_company(before, 3))
        i += 1

    return companies , country_names , url, added_dates , publication_dates

def find_common_words1(text1, text2):
    words_text2 = text2.split()

    if text1 in words_text2:
        return text1

    else:
        return False


def find_common_words2(text1, text2, text3):
    test_text =text1+text2
    words_text3 = text3.split()

    if test_text in words_text3:
        return text1

    else:
        return False

def find_common_words3(text1, text2, text3, text4):
    test_text = text1+text2+text3
    words_text4 = text4.split()

    if test_text in words_text4:
        return text1

    else:
        return False

def sum_company(before, max):
    company = before[0]
    for j in range(1, len(before) - max):
        if j == len(before) - max:
            company += " " + before[j]
        else:
            company += " " + before[j]

    return company

def remove_null(sample_list):
    sample_list = ' '.join(sample_list).split()
    return sample_list

def remove_emoji(text):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"
                               u"\U0001F300-\U0001F5FF"
                               u"\U0001F680-\U0001F6FF"
                               u"\U0001F1E0-\U0001F1FF"
                               u"\U00002500-\U00002BEF"
                               u"\U00002702-\U000027B0"
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               u"\U0001f926-\U0001f937"
                               u"\U00010000-\U0010ffff"
                               u"\u2640-\u2642"
                               u"\u2600-\u2B55"
                               u"\u200d"
                               u"\u23cf"
                               u"\u23e9"
                               u"\u231a"
                               u"\ufe0f"
                               u"\u3030"
                               "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)

def parse_all_html_files():
    logging.info("Starting to parse all HTML files.")
    
    html_files = [filename for filename in os.listdir() if filename.startswith("page_") and filename.endswith(".html")]
    total_files = len(html_files)
    logging.info(f"Total HTML files to parse: {total_files}")
    logging.info(f"HTML files: {html_files}")  # 파일 목록 출력

    for idx, filename in enumerate(html_files):
        logging.info(f"Parsing file {idx + 1}/{total_files}: {filename}")
        if os.path.isfile(filename):
            try:
                with open(filename, 'r', encoding='utf-8') as file:
                    html = file.read()
                    parse_page(html)
                    logging.info(f"Finished parsing file {idx + 1}/{total_files}: {filename}")
            except Exception as e:
                logging.error(f"Error parsing file {filename}: {e}")
        else:
            logging.error(f"File not found: {filename}")

def save_to_mongodb(data_list):
    try:
        logging.info(f"Connecting to MongoDB and saving data: {data_list}")
        client = MongoClient('mongodb://localhost:27017/')
        db = client['darkweb']
        
        # 현재 날짜 확인
        current_date = datetime.now().strftime('%Y-%m-%d')
        collection = db[current_date]
        
        for data in data_list:
            company = data['company']
            country = data['country']
            site_urls = data['url']
            date_added = data['added_date']
            date_published = data['publication_date']
            
            # 데이터 형식 맞추기 (날짜 형식을 'YYYY-MM-DD'로 통일)
            try:
                date_added = datetime.strptime(date_added, '%Y-%m-%d').strftime('%Y-%m-%d')
                date_published = datetime.strptime(date_published, '%Y-%m-%d').strftime('%Y-%m-%d')
            except ValueError as ve:
                logging.error(f"Date format error in data: {data}. Error: {ve}")
                continue

            data_dict = {
                'company': company,
                'country': country,
                'date_added': date_added,
                'date_published': date_published,
                'site_urls': site_urls
            }

            # 중복 방지 업데이트
            logging.info(f"Inserting/updating data: {data_dict}")
            collection.update_one(
                {'company': data_dict['company'], 'date_added': data_dict['date_added']},
                {'$set': data_dict},
                upsert=True
            )
        
        logging.info("Data insertion/updation completed.")
        client.close()

    except Exception as e:
        logging.error(f"Error connecting to MongoDB: {e}")

if __name__ == "__main__":
    while True:
        try:
            start_time = time.time()  # 시작 시간 기록
            base_url = "http://mbrlkbtq5jonaqkurjwmxftytyn2ethqvbxfu4rgjbkkknndqwae6byd.onion/"  # 다크웹 사이트 URL
            all_post_urls = scrape_site(base_url)
            parse_all_html_files() # 모든 HTML 파일 파싱 시작
            end_time = time.time()  # 종료 시간 기록
            logging.info(f"Found {len(all_post_urls)} posts.")
            logging.info(f"Total execution time: {end_time - start_time:.2f} seconds")  # 실행 시간 로그
            logging.info("Entering sleep mode for 24 hours...")  # 대기 모드 로그
            
            # 24시간을 1시간 간격으로 나누어 상태 로그 출력
            total_sleep_time = 86400  # 24시간
            interval = 3600  # 1시간 간격
            hours_elapsed = 0
            for _ in range(total_sleep_time // interval):
                time.sleep(interval)
                hours_elapsed += 1
                logging.info(f"{hours_elapsed} hours have passed...")  # 현재 상태 로그 출력

            logging.info("Starting next crawl cycle.")

        except Exception as e:
            logging.error(f"Error in main loop: {e}")
