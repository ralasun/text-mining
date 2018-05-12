import os
from selenium import webdriver
from bs4 import BeautifulSoup
import argparse
import time
import pandas as pd
import csv
from pprint import pprint

def get_keywords(dir_for_search):
    cos_names = pd.read_excel(dir_for_search, header=None)
    cos_name_list = sorted(cos_names[0].tolist())
    return cos_name_list

def check_page_available(current_driver, word_for_src):
    time.sleep(1)
    print("waiting for check if reviews for {} are integrated in naver shopping page..".format(word_for_src))
    page_for_check = current_driver.page_source
    bsobj_chc = BeautifulSoup(page_for_check, 'html.parser')
    integrated_or_not = bsobj_chc.find('li', {'class':'_model_list _itemSection'})

    if integrated_or_not :
        page_state = True
    else:
        page_state = False
    return page_state

def cosmetic_review_crawler_(html, root_dir, word_for_src, num):
    bsobj = BeautifulSoup(html, 'html.parser')
    reviews = bsobj.find_all('div', {'class':'atc_area'})

    for i, each_review in enumerate(reviews):
        review_score = each_review.find('span', {'class':'curr_avg'}).get_text()
        review_title = each_review.find('p', {'class':'subjcet'}).get_text()
        review_content = each_review.find('div', {'class':'atc'}).get_text()
        print('*'*100)
        print('{} : {}번째 리뷰, 점수 : {}, 내용: {}'.format(num, i+1, review_score, review_content))

        if  not ( review_title == review_content[:len(review_title)]
                  or review_title[:-3] == review_content[:len(review_title[:-3])]):
            review_content = review_title + ' ' + review_content


        file_name_path = os.path.join(root_dir, '{}.txt'.format(word_for_src))
        with open(file_name_path, 'a', encoding='utf-8') as f:
            fieldnames=['점수', '내용']
            writer = csv.DictWriter(f, fieldnames = fieldnames)
            writer.writerow({'점수':review_score, '내용':review_content})

    print('\n')

def cosmetic_reviews_crawler(driver, root_dir, word_for_src):
    start_indx = 1
    start_page = 0
    next = True
    while next:
        old_pages=[]
        try:
            html = driver.page_source
            bsobj = BeautifulSoup(html, 'html.parser')
            page_counts = len(bsobj.find('div', {'id':'_review_paging'}).find_all('a'))
            old_pages=[i+1 for i in range(page_counts)]
        except AttributeError:
            print('there is no more than one page.')

        old_pages.insert(start_indx-1, start_page)

        if len(old_pages) <= 11 :
            next = False
            pages = old_pages
        else:
            pages = old_pages[:-1]

        print(old_pages, start_indx)
        for num, info in enumerate(pages):

            if num < (start_indx - 1) :
                continue

            if num == (start_indx - 1) :
                if start_indx == 1:

                    html = driver.page_source
                    cosmetic_review_crawler_(html, root_dir, word_for_src, num)
                else:
                    continue

            if (num > (start_indx - 1)) :
                new_xpath = '//*[@id="_review_paging"]/a[{}]'.format(info)
                try:
                    driver.find_element_by_xpath(new_xpath).click()
                    time.sleep(1)
                except:
                    print('restarting....')
                    time.sleep(1)
                    driver.find_element_by_xpath(new_xpath).click()
                    time.sleep(1)

                html = driver.page_source
                cosmetic_review_crawler_(html, root_dir, word_for_src, num)

        if len(old_pages) > 11:
            start_indx = 3

        time.sleep(1)

def cosmetic_reviews_crawler_wrapper(url_to_crawl, dir_for_chromedriver, word_for_src, root_dir):

    driver = webdriver.Chrome(dir_for_chromedriver)
    driver.get(url_to_crawl)
    elem = driver.find_element_by_xpath('//*[@id="autocompleteWrapper"]/input[1]')
    elem.send_keys(word_for_src)
    time.sleep(1)
    driver.find_element_by_xpath('//*[@id="autocompleteWrapper"]/a[2]').click()
    driver.implicitly_wait(10)

    driver.find_element_by_xpath('//*[@id="_sort_review"]/a').click()
    driver.implicitly_wait(10)

    page_state = check_page_available(driver, word_for_src)

    if page_state:
        print('There exists integrated review pages for {}, KEEP CRAWLING!!'.format(word_for_src))
        parent_elem = driver.find_element_by_xpath('//*[@id="_search_list"]/div[1]/ul/li[@class="_model_list _itemSection"]')
        parent_elem.find_element_by_xpath('.//a').click()
        driver.implicitly_wait(10)

        window_after = driver.window_handles[1]
        driver.switch_to.window(window_after)

        cosmetic_reviews_crawler(driver, root_dir, word_for_src)
        driver.quit()

    else:
        print('There does not exist integrated review pages for {}, PASS ONTO NEXT WORD!!!'.format(word_for_src))
        print('\n')
        driver.quit()
        return


def main():
    parser = argparse.ArgumentParser(description='crawling naver shop homepage')
    parser.add_argument('-k', '--kind', default='foundation',
                        help='kind of makeup products')
    parser.add_argument('-u','--url',
                        type=str,
                        default="http://pc.shopping2.naver.com/",
                        help='which site to be crawled')
    parser.add_argument('-d', '--dir',
                        type=str,
                        default='C://Users//korea//Desktop//chromedriver',
                        help='location of chromedriver')
    parser.add_argument('-s', '--search',
                        type=str,
                        default='.//foundation.xlsx',
                        help='directory for the file which contains whole keywords for search')
    parser.add_argument('-sd', '--savedir',
                        type=str,
                        default='./cosmetic_review_crawling')

    args = vars(parser.parse_args())
    kind = args['kind']
    save_dir = args['savedir']
    url_to_crawl = args['url']
    dir_for_chromedriver = args['dir']
    dir_for_excel = args['search']

    root_dir = os.path.join(save_dir, kind)
    if not os.path.exists(root_dir):
        os.makedirs(root_dir)

    cos_name_lists = get_keywords(dir_for_excel)
    try:
        crawled_lists = sorted(os.listdir(root_dir))
        print(crawled_lists)
        final_crawled = crawled_lists[-1]
        print(final_crawled)

        for i, check_word in enumerate(cos_name_lists):
            if check_word == os.path.splitext(final_crawled)[0]:
                print('{}번째 {}까지는 크롤링 끝남.'.format(i-1, cos_name_lists[i-1]))
                restart = i
                break

        os.remove(os.path.join(root_dir, final_crawled))
    except IndexError:
        restart = 1
        print('restarting from scratch')


    for i, word_for_src in enumerate(cos_name_lists[restart:]):
        print('{}번째 : {}'.format(i+1, word_for_src))
        cosmetic_reviews_crawler_wrapper(url_to_crawl, dir_for_chromedriver,
                                         word_for_src, root_dir)

if __name__ == "__main__":
    main()



