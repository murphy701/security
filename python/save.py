import requests
from bs4 import BeautifulSoup

def crawl_community_page(url):
    # GET 요청 보냄
    response = requests.get(url)

    # status code 200을 확인 
    if response.status_code == 200:
        # HTML 콘텐츠 파싱
        soup = BeautifulSoup(response.text, 'html.parser')

        # 페이지에서 요소를 찾는 과정
        titles = soup.find_all('a', class_='tit_txt')
        dates = soup.find_all('span', class_='date_time')
        nicknames = soup.find_all('a', class_='sub_txt')

        # 추출하여 리스트로 저장
        title_texts = [title.get_text() for title in titles]
        date_texts = [date.get_text() for date in dates]
        nickname_texts = [nickname.get_text() for nickname in nicknames]

        return title_texts, date_texts, nickname_texts
    else:
        # 에러 처리
        print("Failed to fetch the page. Status code:", response.status_code)
        return None, None, None

def save_to_file(titles, dates, nicknames, filename):
    # 데이터를 확인
    if titles and dates and nicknames:
        with open(filename, 'w') as file:
            for title, date, nickname in zip(titles, dates, nicknames):
                data = f"Title: {title} Date: {date} Nickname: {nickname}\n"
                file.write(data)
    else:
        print("No data to save.")

# URL을 입력값으로 받아 처리
user_input = input("Please enter the URL: ")
url = user_input

titles, dates, nicknames = crawl_community_page(url)

# 데이터를 출력
if titles and dates and nicknames:
    for title, date, nickname in zip(titles, dates, nicknames):
        print("Title:", title, "Date:", date, "Nickname:", nickname)
    # 출력 후 저장
    save_to_file(titles, dates, nicknames, 'result.txt')
else:
    print("No data fetched. Check the URL or try again later.")
#dc인사이드 특정 요소를 크롤링, 다른 사이트의 경우 출력이 안되며 수정이 필요함