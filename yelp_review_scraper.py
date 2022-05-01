import argparse
import time
import random
import logging
import sys
import io
import os
import platform
from timeit import default_timer as timer
from datetime import timedelta

import pandas as pd
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

import boto3

import utils

parser = argparse.ArgumentParser()
FORMAT = '[%(levelname)s: %(filename)s: %(lineno)4d] %(message)s'
logging.basicConfig(level=logging.INFO, format=FORMAT, stream=sys.stdout)
logger = logging.getLogger(__name__)

# Scraper Options
parser.add_argument('--start_index', default=0, type=int)
parser.add_argument('--end_index', default=-1, type=int)
parser.add_argument('--wait_time_for_new_index', default=10, type=int)
parser.add_argument('--wait_time_for_establishment', default=10, type=int)
parser.add_argument('--wait_time_for_next_page', default=10, type=int)

# Display Option
parser.add_argument('--verbose', default=1, type=int)

# Dataset Option
parser.add_argument('--dataset_name', default='Res_List_From_Inspection', type=str)

# AWS Options
parser.add_argument('--aws_mode', default=0, type=int)

# Chrome Option
parser.add_argument('--open_chrome', default=0, type=int)

# Save Option
parser.add_argument('--index_suffix', default=1, type=int)

last_index = -1
success_num = 0
fail_num = 0
fail_list = []
reviews = {}

def scraper(driver, df, class_names, xpaths):
    for index, res in df.iterrows():
        user_ids = []
        yelp_ids = []
        establishments = []
        review_texts = []
        ratings = []
        rating_dates = []
        num_photoss = []
        num_usefuls = []
        num_funnys = []
        num_cools = []
        is_rotd = []
        is_updated = []
        owner_replied = []
        owner_reply_dates = []
        owner_reply_texts = []
        pr_avg_ratings = []
        pr_avg_usefuls = []
        pr_avg_funnys = []
        pr_avg_cools = []

        recommanded_url = 'https://www.yelp.com/biz/' + res['yelp_id']
        driver.get(recommanded_url)
        time.sleep(args.wait_time_for_new_index)

        establishment = WebDriverWait(driver, args.wait_time_for_establishment).until(
            EC.presence_of_element_located((By.XPATH, '//h1[@class="' + class_names['establishment'] + '"]'))).text

        start = timer()
        logger.info('Current working index: ' + str(index) + '. Establishment is ' + establishment + '.')

        total_page = -1
        total_page_element_candidates = driver.find_elements(By.XPATH,
                                                             '//div[@class="' + class_names[
                                                                 'total_page_element_candidates'] + '"]')
        if len(total_page_element_candidates) > 0:
            for candidate in total_page_element_candidates:
                detect_total_page_element = candidate.find_elements(By.XPATH, './/span[@class="' + class_names[
                    'total_page'] + '"]')
                if len(detect_total_page_element) > 0:
                    total_page = int(detect_total_page_element[0].text.split('of')[1])
                    break

        if total_page == -1:
            logger.info('[' + establishment + ']: Cannot find any reviews.')
            raise

        if args.verbose:
            logger.info('[' + establishment + ']: Found ' + str(total_page) + ' page(s)')

        list_of_page = []
        if total_page > 1:
            list_of_page = ['?start=' + str(i * 10) for i in random.sample(range(1, total_page), total_page - 1)]

        page = 0
        total_review_num = 0
        while (True):
            page = page + 1
            if args.verbose:
                logger.info('[' + establishment + ']: Currently working on ' + str(page) + ' page...')

            if page > 1:
                current_page = list_of_page.pop()
                driver.get(recommanded_url + current_page)
            time.sleep(args.wait_time_for_next_page)

            fake_sections = driver.find_elements(By.XPATH,
                                                 '//section[@class= "' + class_names['fake_sections'] + '"]')
            for section in fake_sections:
                if section.get_attribute('aria-label') == "Recommended Reviews":
                    review_elements = section.find_elements(By.XPATH, xpaths['review_elements'])
                    break

            num_loaded_reviews = len(review_elements)
            if num_loaded_reviews == 0:
                logger.info('[' + establishment + ']: Cannot find any reviews.')
                raise
            else:
                total_review_num = total_review_num + num_loaded_reviews
                for review_element in review_elements:
                    user_id = ""
                    id_div = review_element.find_element(By.XPATH,
                                                         './/div[@class="' + class_names['id_div'] + '"]')
                    id_element = id_div.find_elements(By.XPATH, xpaths['id_element'])
                    if len(id_element) > 0:
                        user_id = id_element[0].get_attribute('href').split('=')[1]

                    rating_date_updated_div = review_element.find_element(By.XPATH,
                                                                          './/div[@class= "' + class_names[
                                                                              'rating_date_updated_div'] + '"]')
                    rating_element = rating_date_updated_div.find_element(By.XPATH, xpaths['rating_element'])
                    date_element = rating_date_updated_div.find_element(By.XPATH, xpaths['date_element'])
                    updated_element = rating_date_updated_div.find_elements(By.XPATH, xpaths['updated_element'])
                    rating = float(rating_element.get_attribute('aria-label').split(" ")[0])
                    date = date_element.text
                    updated = (len(updated_element) > 0)

                    num_photos = 0
                    ROTD = False
                    photo_rotd_review_div = review_element.find_elements(By.XPATH,
                                                                         './/div[@class="' + class_names[
                                                                             'photo_rotd_review_div'] + '"]')
                    if len(photo_rotd_review_div) > 1:  # photo, rotd, extra...
                        for div in photo_rotd_review_div[0].find_elements(By.XPATH, './div'):
                            element = div.find_elements(By.XPATH, './span/a')
                            if len(element) > 0:  # photo or rotd
                                info = element[0].text
                                if info.find('photos') != -1:
                                    num_photos = float(info.split(" ")[0])
                                elif info.find('ROTD') != -1:
                                    ROTD = True
                                else:  # empty string. Maybe more than one photos.
                                    num_photos = 1
                            else:  # check-in or badge info.
                                continue
                        review_text_element = photo_rotd_review_div[1].find_element(By.XPATH, './p/span')
                        review_text = review_text_element.text

                    else:
                        review_text_element = photo_rotd_review_div[0].find_element(By.XPATH, './p/span')
                        review_text = review_text_element.text

                    useful = 0
                    funny = 0
                    cool = 0
                    helpfulness_div = review_element.find_element(By.XPATH,
                                                                  './/div[@class="' + class_names[
                                                                      'helpfulness_div'] + '"]')
                    useful_element = helpfulness_div.find_elements(By.XPATH,
                                                                   xpaths['useful_element'])
                    funny_element = helpfulness_div.find_elements(By.XPATH,
                                                                  xpaths['funny_element'])
                    cool_element = helpfulness_div.find_elements(By.XPATH,
                                                                 xpaths['cool_element'])
                    if len(useful_element) > 0:
                        useful = float(useful_element[0].text)
                    if len(funny_element) > 0:
                        funny = float(funny_element[0].text)
                    if len(cool_element) > 0:
                        cool = float(cool_element[0].text)

                    owner_reply = False
                    owner_reply_date = ""
                    owner_reply_text = ""
                    num_prs = 0
                    sum_pr_ratings = 0
                    sum_pr_useful = 0
                    sum_pr_funny = 0
                    sum_pr_cool = 0
                    avg_pr_useful = 0
                    avg_pr_funny = 0
                    avg_pr_cool = 0
                    avg_pr_ratings = 0
                    or_n_pr1_div = review_element.find_elements(By.XPATH,
                                                                './/div[@class="' + class_names['or_n_pr1_div'] + '"]')
                    if len(or_n_pr1_div) > 0:
                        for div in or_n_pr1_div:
                            if len(div.find_elements(By.XPATH, xpaths['pr1_element'])) > 0:  # Previous Review
                                num_prs = num_prs + 1
                                button = div.find_element(By.XPATH, xpaths['pr1_button'])
                                driver.execute_script("arguments[0].click();", button)
                                this_rating = float(div.find_element(By.XPATH, xpaths['pr1_rating']).get_attribute(
                                    'aria-label').split(" ")[0])
                                sum_pr_ratings = this_rating + sum_pr_ratings

                                this_useful_element = div.find_elements(By.XPATH, xpaths['pr1_useful'])
                                this_funny_element = div.find_elements(By.XPATH, xpaths['pr1_funny'])
                                this_cool_element = div.find_elements(By.XPATH, xpaths['pr1_cool'])

                                this_useful = 0
                                this_funny = 0
                                this_cool = 0
                                if len(this_useful_element) > 0:
                                    this_useful = float(this_useful_element[0].text)
                                if len(this_funny_element) > 0:
                                    this_funny = float(this_funny_element[0].text)
                                if len(this_cool_element) > 0:
                                    this_cool = float(this_cool_element[0].text)

                                sum_pr_useful = this_useful + sum_pr_useful
                                sum_pr_funny = this_funny + sum_pr_funny
                                sum_pr_cool = this_cool + sum_pr_cool
                            else:  # Owner Reply
                                owner_reply = True
                                button = div.find_element(By.XPATH, xpaths['owner_button'])
                                driver.execute_script("arguments[0].click();", button)
                                owner_reply_date = div.find_element(By.XPATH, xpaths['owner_reply_date']).text
                                owner_reply_text = div.find_element(By.XPATH, xpaths['owner_reply_text']).text

                    extra_prs_div = review_element.find_elements(By.XPATH,
                                                                 './/div[@class="' + class_names[
                                                                     'extra_prs_div'] + '"]')
                    if len(extra_prs_div) > 0:
                        for div in extra_prs_div:
                            num_prs = num_prs + 1
                            button = div.find_element(By.XPATH, xpaths['extra_pr_button'])
                            driver.execute_script("arguments[0].click();", button)
                            this_rating = float(
                                div.find_element(By.XPATH, xpaths['extra_pr_rating']).get_attribute(
                                    'aria-label').split(" ")[0])
                            sum_pr_ratings = this_rating + sum_pr_ratings

                            this_useful_element = div.find_elements(By.XPATH, xpaths['extra_pr_useful'])
                            this_funny_element = div.find_elements(By.XPATH, xpaths['extra_pr_funny'])
                            this_cool_element = div.find_elements(By.XPATH, xpahts['extra_pr_cool'])

                            this_useful = 0
                            this_funny = 0
                            this_cool = 0
                            if len(this_useful_element) > 0:
                                this_useful = float(this_useful_element[0].text)
                            if len(this_funny_element) > 0:
                                this_funny = float(this_funny_element[0].text)
                            if len(this_cool_element) > 0:
                                this_cool = float(this_cool_element[0].text)

                            sum_pr_useful = this_useful + sum_pr_useful
                            sum_pr_funny = this_funny + sum_pr_funny
                            sum_pr_cool = this_cool + sum_pr_cool

                    if num_prs > 0:
                        avg_pr_ratings = sum_pr_ratings / num_prs
                        avg_pr_useful = sum_pr_useful / num_prs
                        avg_pr_funny = sum_pr_funny / num_prs
                        avg_pr_cool = sum_pr_cool / num_prs

                    user_ids.append(user_id)
                    ratings.append(rating)
                    rating_dates.append(date)
                    review_texts.append(review_text)
                    is_rotd.append(ROTD)
                    is_updated.append(updated)
                    num_photoss.append(num_photos)
                    num_usefuls.append(useful)
                    num_funnys.append(funny)
                    num_cools.append(cool)
                    owner_replied.append(owner_reply)
                    owner_reply_dates.append(owner_reply_date)
                    owner_reply_texts.append(owner_reply_text)
                    pr_avg_ratings.append(avg_pr_ratings)
                    pr_avg_usefuls.append(avg_pr_useful)
                    pr_avg_funnys.append(avg_pr_funny)
                    pr_avg_cools.append(avg_pr_cool)

            yelp_ids.extend([res['yelp_id']] * num_loaded_reviews)
            establishments.extend([establishment] * num_loaded_reviews)

            TheEnd = False
            if len(list_of_page) == 0:
                TheEnd = True

            if TheEnd:
                end = timer()
                global reviews, last_index, success_num
                last_index = index
                success_num += 1
                logger.info('[' + establishment + ']: Done. ' + str(total_review_num) + ' reviews are collected.')
                if args.verbose:
                    logger.info('Elapsed Time: ' + str(timedelta(seconds=(end - start))))
                this_reviews = [yelp_ids, establishments, user_ids, ratings, rating_dates, review_texts, is_rotd,
                                is_updated, num_photos, num_usefuls, num_funnys, num_cools, owner_replied,
                                owner_reply_dates, owner_reply_texts, pr_avg_ratings, pr_avg_usefuls, pr_avg_funnys,
                                pr_avg_cools]
                reviews[index] = this_reviews
                break

def main(args, obj):
    if platform.system() != 'Windows' or args.open_chrome == 0:
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

    class_names, xpaths = utils.load_class_name_and_xpath('keys_for_scraping.ini')

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # Load restaurant list file.
    if args.aws_mode:
        yelp_target_df = pd.read_csv(io.BytesIO(obj['Body'].read()))
    else:
        yelp_target_df = pd.read_csv(args.dataset_name + '.csv', encoding='utf-8')

    if not 'yelp_id' in yelp_target_df.columns:
        logger.error('Cannot find yelp_id column in your list file. The program will be terminated.')
        exit()

    if args.verbose:
        logger.info('The restaurant list file has been successfully loaded.')
        logger.info('The total number of restaurants is ' + str(len(yelp_target_df)) + '.')

    # Check end index
    if args.end_index == -1:
        end_index = len(yelp_target_df) - 1
    else:
        if args.end_index > len(yelp_target_df) - 1:
            logger.warning('End index is too large. It is set to the last index ' + str(len(yelp_target_df) - 1) + '.')
            end_index = len(yelp_target_df) - 1
        else:
            end_index = args.end_index

    yelp_target_df = yelp_target_df[args.start_index:end_index + 1]
    if args.verbose:
        logger.info('The number of target restaurants is ' + str(end_index - args.start_index + 1) + '.')

    all_work_done = False

    while(True):
        global last_index, success_num, fail_num
        if last_index == end_index:
            all_work_done = True

        if all_work_done:
            break
        try:
            scraper(driver, yelp_target_df, class_names, xpaths)
        except:
            fail_num += 1
            if last_index == -1:
                error_index = args.start_index
            else:
                error_index = last_index + 1
            fail_list.append(error_index)
            logger.error(sys.exc_info()[0])
            logger.error('Index ' + str(error_index) +': Error occured. This restaurant gets skipped.')
            if error_index + 1 > end_index:
                all_work_done = True
            else:
                yelp_target_df = yelp_target_df.loc[error_index + 1:end_index + 1]
            last_index = error_index


    logger.info('-----------------')
    logger.info('Report')
    logger.info('Total Number of Target Restaurants: ' + str(end_index - args.start_index + 1))
    logger.info('Success: ' + str(success_num))
    logger.info('Fail: ' + str(fail_num))
    if fail_num > 0:
        msg = ", ".join(map(str, fail_list))
        logger.info(msg)
    logger.info('-----------------')

    if success_num == 0:
        logger.info('Nothing to save because NO REVIEWS ARE COLLECTED :(')
        logger.info('Please check class names and xpaths in keys_for_scraping.ini file. They may be not valid.')

    else:
        logger.info('Saving the collected reviews...')
        global reviews
        all_reviews = utils.set_to_df(reviews)
        file_name = 'yelp_review.csv'
        if args.index_suffix:
            file_name = 'yelp_review_from_' + str(args.start_index) + '_to_' + str(end_index) + '.csv'

        if args.aws_mode:
            with io.StringIO() as csv_buffer:
                all_reviews.to_csv(csv_buffer, index=False)
                response = s3.put_object(Bucket=bucket_name, Key=file_name, Body=csv_buffer.getvalue())
                status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")
                if status == 200:
                    logger.info(
                        'Done. All work you requested has been finished. The program will be terminated.')
                else:
                    logger.error('Failed to save the result file to your S3 bucket.')
        else:
            all_reviews.to_csv(file_name, encoding='utf-8', index=False)
            logger.info('Done. All work you requested has been finished. The program will be terminated.')

if __name__ == '__main__':
    args = parser.parse_args()

    parser_error = False
    # args check
    if args.start_index < 0:
        parser_error = True
        parser.error('Start index cannot be negative.')

    if args.end_index != -1 & args.end_index < 0:
        parser_error = True
        parser.error('End index must be -1 or non-negative.')

    if (args.end_index != -1) & (args.start_index > args.end_index):
        parser_error = True
        parser.error('Start index cannot be larger than end index.')

    if args.wait_time_for_new_index < 0:
        parser_error = True
        parser.error('Wait time for new index cannot be negative.')

    if args.wait_time_for_establishment < 0:
        parser_error = True
        parser.error('Wait time for establishment cannot be negative.')

    if args.wait_time_for_next_page < 0:
        parser_error = True
        parser.error('Wait time for next page cannot be negative.')

    if parser_error:
        print('Some arguments you entered are not valid. The program will be terminated.')
        exit()

    # file existence check
    obj = None
    if args.aws_mode:
        if not os.path.exists('aws_key.ini'):
            print('aws_key.ini cannot be found. The program will be terminated.')
            exit()

        else:
            AWSAccessKeyID, AWSSecretKey, region, bucket_name = utils.load_aws_keys('aws_key.ini')
            prefix = args.dataset_name + '.csv'
            try:
                s3 = boto3.client('s3', aws_access_key_id=AWSAccessKeyID, aws_secret_access_key=AWSSecretKey,
                              region_name=region)
            except:
                print('Cannot access your AWS S3 service. Check access Key ID, secret Key, and region. The program will'
                      ' be terminated.')
                exit()
            else:
                try:
                    obj = s3.get_object(Bucket=bucket_name, Key=prefix)
                except:
                    print(args.dataset_name + '.csv cannot be found. The program will be terminated.')
                    exit()
    else:
        if not os.path.exists(args.dataset_name + '.csv'):
            print(args.dataset_name + '.csv cannot be found. The program will be terminated.')
            exit()

    if not os.path.exists('keys_for_scraping.ini'):
        print('keys_for_scraping.ini cannot be found. The program will be terminated.')
        exit()

    main(args, obj)