from selenium import webdriver
import os
import pandas as pd
import pyperclip
import time
import pickle


def spell_check_first(i, review, new_reviews):
    if len(review) > 1000 :
        review = review[:1000]

    driver = webdriver.Chrome('C://Users//korea//Desktop//chromedriver')
    driver.get('http://alldic.daum.net/grammar_checker.do')
    driver.find_element_by_xpath('//*[@id="tfSpelling"]').send_keys(review)
    driver.find_element_by_xpath('//*[@id="btnCheck"]').click()
    time.sleep(1)
    try:
        driver.find_element_by_xpath('//*[@id="btnCopy"]').click()
    except:
        print('교정될 부분이 없음. 다시 복사하기..')
        time.sleep(2)
        driver.find_element_by_xpath('//*[@id="btnCopy"]').click()

    time.sleep(1)
    new_review = pyperclip.paste()
    new_reviews.append(new_review)
    print(review)
    print(new_review)

    return new_reviews, driver

def spell_check_after(i, review, new_reviews, driver, temp_dir):

    try:
        if len(review) > 1000:
            review = review[:1000]
    except:
        review = '리뷰없음'

    time.sleep(2)
    try:
        driver.find_element_by_xpath('//*[@id="btnRewrite"]').click()
    except:
        time.sleep(1)
        driver.find_element_by_xpath('//*[@id="btnRewrite"]').click()
    time.sleep(1)

    try:
        driver.find_element_by_xpath('//*[@id="tfSpelling"]').send_keys(review)
    except TypeError:
        print('리뷰가 없음')
        review = '리뷰없음'
        driver.find_element_by_xpath('//*[@id="tfSpelling"]').send_keys(review)
    except :
        print('지원안됨')
        review = '지원안됨'
        driver.find_element_by_xpath('//*[@id="tfSpelling"]').send_keys(review)


    driver.find_element_by_xpath('//*[@id="btnCheck"]').click()
    time.sleep(2)

    try:
        driver.find_element_by_xpath('//*[@id="btnCopy"]').click()
    except:
        print('교정될 부분이 없음. 다시 복사하기..')
        time.sleep(3)
        driver.find_element_by_xpath('//*[@id="btnCopy"]').click()




    time.sleep(1)
    new_review = pyperclip.paste()
    print(i)
    print(review)
    print(new_review)
    new_reviews.append(new_review)

    if i % 20 == 0:

        temp_filename = os.path.join(temp_dir, '{}.bin'.format(i))

        with open(temp_filename, 'wb') as f:
            pickle.dump(new_reviews, f)

    # print(new_reviews)


def spell_check_wrapper(cosmetic_csv_path):

    filename = os.path.splitext(os.path.basename(cosmetic_csv_path))[0]
    dirname = os.path.dirname(cosmetic_csv_path)
    new_filename = filename +'_checked2'
    new_cosmetic_csv_path = os.path.join(dirname, '{}.csv'.format(new_filename))

    temp_dir = os.path.join(dirname, 'tmp')
    if not os.path.isdir(temp_dir):
        os.makedirs(temp_dir)

    cosmetic_df = pd.read_csv(cosmetic_csv_path)
    reviews = cosmetic_df['review']

    if len(os.listdir(temp_dir)) > 0 :
        temp_filenames = sorted(os.listdir(temp_dir), key=lambda tmp : int(os.path.splitext(tmp)[0]) )
        last_checked = temp_filenames[-1]
        print(temp_filenames)
        last_temp_path = os.path.join(temp_dir, last_checked)
        print(last_temp_path)

        with open(last_temp_path, 'rb') as f:
            new_reviews= pickle.load(f, encoding='utf-8')

        last_count = len(new_reviews)
        last_count = last_count + 1

        print('*'*30)
        print(reviews[last_count])
        print('부터 다시 시작....')
        print('*'*30)

        new_reviews, driver = spell_check_first(last_count, reviews[last_count], new_reviews)


    else:
        new_reviews=[]
        last_count = 0
        new_reviews, driver = spell_check_first(last_count, reviews[last_count], new_reviews)


    for i, review in enumerate(reviews[last_count+1:]):
        i = i+last_count
        spell_check_after(i, review, new_reviews, driver, temp_dir)

    cosmetic_df['checked_review'] = new_reviews
    cosmetic_df.to_csv(new_cosmetic_csv_path)

    return cosmetic_df



if __name__=="__main__":
    cosmetic_csv_path = './/cosmetic_review_crawling//foundation//foundation.csv'
    spell_check_wrapper(cosmetic_csv_path)
