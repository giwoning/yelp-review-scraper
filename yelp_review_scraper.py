import argparse
import time
import random
import logging
import sys
import io
import os
import platform
import traceback
import json
from timeit import default_timer as timer
from datetime import timedelta, datetime

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

# Mode Option
parser.add_argument('--collected_object', choices=['restaurant', 'review', 'profile'], required=True)

# Scraper Options
parser.add_argument('--min_index', default=0, type=int)
parser.add_argument('--max_index', default=-1, type=int)
parser.add_argument('--wait_time_for_new_index', default=10, type=int)
parser.add_argument('--wait_time_for_establishment', default=10, type=int)
parser.add_argument('--wait_time_for_next_page', default=10, type=int)
parser.add_argument('--index_specified_mode', default=False, type=bool)

# Log Options
parser.add_argument('--verbose', default=True, type=bool)
parser.add_argument('--save_log', default=False, type=bool)

# Dataset Option
parser.add_argument('--target_list_name', default='User_List', type=str)

# AWS Options
parser.add_argument('--aws_mode', default=False, type=bool)

# Chrome Option
parser.add_argument('--open_chrome', default=False, type=bool)

# Save Option
parser.add_argument('--index_suffix', default=True, type=bool)

args = parser.parse_args()

# Logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

formatter = logging.Formatter('[%(asctime)s][%(levelname)s] >> %(message)s')

if args.save_log:
    fileHandler = logging.FileHandler('./logs/yelp_review_result-' + datetime.now().strftime('%Y_%m_%d-%I_%M_%S_%p')
                                      + '.txt', mode='w', encoding='cp949')
    fileHandler.setFormatter(formatter)
    logger.addHandler(fileHandler)

streamHandler = logging.StreamHandler()
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

success_num = 0
fail_num = 0
fail_list = []
invalid_object_list = []
reviews = {}
profiles = {}
restaurants = {}

def res_scraper(driver, index, res):
    url = "https://www.yelp.com/biz/" + res['yelp_id']
    driver.get(url)
    time.sleep(args.wait_time_for_new_index)

    error_404 = len(driver.find_elements(By.CLASS_NAME, 'page-status')) > 0
    if error_404:
        logger.error('This page has been removed.')
        invalid_object_list.append(index)
        raise

    error = []

    # Name
    res_name = ""
    name_element = driver.find_elements(By.XPATH, '//h1[@class="css-wbh247"]')
    if len(name_element) > 0:
        res_name = name_element[0].text
    else:
        error.append("Name")
        res_name = "NA"

    # Closed
    is_closed = len(driver.find_elements(By.XPATH, '//*[contains(text(), \'Yelpers report this location has closed.\')]')) > 0
    if is_closed:
        if res_name != "":
            logger.info('[' + res_name + '] This location has closed.')
        else:
            logger.info('This location has closed.')

    # Ratings
    rating_element = driver.find_elements(By.XPATH, '//yelp-react-root/div[1]/div[3]/div[1]/div[1]/div/div/div[2]/div[1]/span/div')
    if len(rating_element) > 0:
        ratings = rating_element[0].get_attribute('aria-label')
        ratings = float(ratings[:ratings.find(" ")])
    else:
        error.append("Ratings")
        ratings = "NA"

    # Number of Total Reviews
    num_reviews_element = driver.find_elements(By.XPATH,
                                               '//yelp-react-root/div[1]/div[3]/div[1]/div[1]/div/div/div[2]/div[2]/span')
    if len(num_reviews_element) > 0:
        num_reviews = int(num_reviews_element[0].text[:num_reviews_element[0].text.find(" ")])
    else:
        error.append("Number of Total Reviews")
        num_reviews = "NA"

    # Claimed
    claimed_element = driver.find_elements(By.XPATH,
                                           '//yelp-react-root/div[1]/div[3]/div[1]/div[1]/div/div/span[1]/span/div/span')
    if len(claimed_element) > 0:
        claimed = claimed_element[0].text
    else:
        error.append("Claimed")
        claimed = "NA"

    # Price Range
    pricerange_element = driver.find_elements(By.XPATH, '/yelp-react-root/div[1]/div[3]/div[1]/div[1]/div/div/span[2]/span')
    if len(pricerange_element) > 0:
        pricerange = pricerange_element[0].text
    else:
        error.append("Price Range")
        priceranges = "NA"

    # Category list
    category_elements = driver.find_elements(By.XPATH, 'yelp-react-root/div[1]/div[3]/div[1]/div[1]/div/div/span[3]/span/a')
    if len(category_elements) > 0:
        category_list = ''
        first = True
        for element in category_elements:
            category = element.text
            if first:
                category_list = category
                first = False
            else:
                category_list = category_list + ", " + category
    else:
        error.append("Category List")
        category_lists = "NA"

    # Number of Photos Posted in Reviews
    photo_num_element = driver.find_elements(By.XPATH, '//a[@class="css-1enow5j"]/span')
    if len(photo_num_element) > 0:
        if photo_num_element[0].text == 'Add photo or video':
            photo_num = 0
        else:
            photo_num = int(photo_num_element[0].text.split(" ")[1])
    else:
        error.append("Number of Photos Posted in Reviews")
        photo_num = "NA"

    ############# Phone Number #############
    phone_icon_element = driver.find_elements(By.XPATH,
                                              '//span[@class="icon--24-phone-v2 icon__09f24__zr17A css-147xtl9"]')
    if len(phone_icon_element) == 0:
        phone_icon_element = driver.find_elements(By.XPATH,
                                                  '//span[@class="icon--24-phone-v2 icon__373c0__viOUw css-nyitw0"]')
    if len(phone_icon_element) == 0:
        error.append("Phone Number")
        phone_numbers = "NA"
    else:
        phone_number = phone_icon_element[0].find_elements(By.XPATH,
                                                           './../preceding-sibling::div/p[@class=" css-1h7ysrc"]')
        if len(phone_number) == 0:
            phone_number = phone_icon_element[0].find_elements(By.XPATH,
                                                               './../preceding-sibling::div/p[@class=" css-oe5jd3"]')
        phone_numbers = phone_number[0].text

    ############# Address #############
    direction_icon_element = driver.find_elements(By.XPATH,
                                                  '//span[@class="icon--24-directions-v2 icon__09f24__zr17A css-nyitw0"]')
    if len(direction_icon_element) == 0:
        direction_icon_element = driver.find_elements(By.XPATH,
                                                      '//span[@class="icon--24-directions-v2 icon__373c0__viOUw css-nyitw0"]')
    if len(direction_icon_element) == 0:
        error.append("Address")
        addresses = "NA"
    else:
        address = direction_icon_element[0].find_elements(By.XPATH,
                                                          './../../preceding-sibling::div/p[@class=" css-v2vuco"]')
        if len(address) == 0:
            address = direction_icon_element[0].find_elements(By.XPATH,
                                                              './../../preceding-sibling::div/p[@class=" css-1ccncw"]')
        if len(address) == 0:
            error.append("Address")
            addresses = "NA"
        else:
            addresses = address[0].text

    ############# Amenities #############
    possible_buttons = driver.find_elements(By.XPATH, '//button[@class=" css-zbyz55"]')

    # Check elements are really more attributes button
    for button in possible_buttons:
        button_name = button.find_elements(By.XPATH, './span/p')
        if len(button_name) > 0:
            if button_name[0].text.find("More Attributes") != -1:
                button.click()
                break
        else:
            continue

    amenities_elements = driver.find_elements(By.XPATH,
                                              '//div[@class=" arrange__373c0__3yvT_ gutter-2__373c0__1fwxZ layout-wrap__373c0__1j3yL layout-2-units__373c0__25Mue border-color--default__373c0__2s5dW"]/div')
    if len(amenities_elements) == 0:
        amenities_elements = driver.find_elements(By.XPATH,
                                                  '//div[@class=" arrange__09f24__LDfbs gutter-2__09f24__CCmUo layout-wrap__09f24__GEBlv layout-2-units__09f24__PsGVW border-color--default__09f24__NPAKY"]/div')
    if len(amenities_elements) == 0:
        error.append("Amenities")
        amenities = "NA"
    else:
        amenities_list = []
        class_names = [[' css-1h7ysrc', ' css-1ccncw'], [' css-oe5jd3', ' css-v2vuco']]
        amenity_desc = ''
        for amenities_element in amenities_elements:
            for name in class_names[0]:
                info = amenities_element.find_elements(By.XPATH, './/span[@class="' + name + '"]')
                if len(info) > 0:
                    amenity_desc = info[0].text
                    amenities_list.append(amenity_desc)
                    break

        if len(amenity_desc) == 0:
            for amenities_element in amenities_elements:
                for name in class_names[1]:
                    info = amenities_element.find_elements(By.XPATH, './/span[@class="' + name + '"]')
                    if len(info) > 0:
                        amenity_desc = info[0].text
                        amenities_list.append(amenity_desc)
                        break
        amenities = ", ".join(amenities_list)

    ############# Hours #############
    table_elements = driver.find_elements(By.XPATH,
                                          '//table[@class=" hours-table__373c0__2YHlD table__373c0__1FIZ8 table--simple__373c0__3QsR_"]/tbody/tr[@class=" table-row__373c0__1F6B0"]')
    if len(table_elements) == 0:
        table_elements = driver.find_elements(By.XPATH,
                                              '//table[@class=" hours-table__09f24__KR8wh table__09f24__J2OBP table--simple__09f24__vy16f"]/tbody/tr[@class=" table-row__09f24__YAU9e"]')
    if len(table_elements) == 0:
        error.append("Operating Hours")
        day_and_operating_times = "NA"
    else:
        day_and_operating_times = ''
        for tr in table_elements:
            day = tr.find_elements(By.XPATH, './th/p')[0].text
            if len(day) == 0:
                continue
            operating_times = []
            operating_times_element = tr.find_elements(By.XPATH, './td/ul/li')
            for element in operating_times_element:
                operating_time = element.find_element(By.XPATH, './p').text
                operating_times.append(operating_time)

            if len(day_and_operating_times) == 0:
                if len(operating_times) > 1:
                    day_and_operating_times = day + ": " + ", ".join(operating_times)
                else:
                    day_and_operating_times = day + ": " + operating_times[0]
            else:
                if len(operating_times) > 1:
                    day_and_operating_times = day_and_operating_times + " | " + day + ": " + ", ".join(operating_times)
                else:
                    day_and_operating_times = day_and_operating_times + " | " + day + ": " + operating_times[0]

    if len(error) == 0:
        logger.info('[' + res_name + ']: Done. All information has been successfully collected.')
    else:
        logger.info('[' + res_name + ']: Done. But some information was failed to be collected:')
        logger.info(", ".join(error))

    this_res_info = [res['yelp_id'], name, is_closed, claimed, ratings, num_reviews, priceranges, category_lists,
                     photo_num, phone_numbers, addresses, day_and_operating_times, amenities]
    restaurants[index] = this_res_info

def profile_scraper(driver, index, reviewer):
    logger.info('Current working index: ' + str(index) + '. User ID is ' + reviewer['user_id'] + '.')

    url = 'https://www.yelp.com/user_details?userid=' + reviewer['user_id']
    driver.get(url)
    time.sleep(args.wait_time_for_new_index)

    error_404 = len(driver.find_elements(By.XPATH, '//div[@class="arrange_unit arrange_unit--fill"]/p')) > 0
    if error_404:
        logger.error('This user has been removed.')
        invalid_object_list.append(index)
        raise

    profile_photo_urls = []

    photo_info = "yelp.www.init.user_details.initPhotoSlideshow(\".js-photo-slideshow-user-details\", "
    photo_slide_script = ""
    script_element = driver.find_elements(By.XPATH, '//*[contains(text(), \'yelp.www.init.user_details.initPhotoSlideshow\')]')
    if len(script_element) > 0:
        photo_slide_script = script_element[0].get_attribute('innerHTML')

    # No Photos or Only One Photo
    if photo_slide_script == "":
        photo_src = driver.find_elements(By.CLASS_NAME, 'photo-box-img')[0].get_attribute('src')
        if photo_src.find('user_large_square.png') == -1:
            profile_photo_urls.append(photo_src)
    else:
        start_index = photo_slide_script.find(photo_info)
        end_index = photo_slide_script.find(")", start_index)
        photo_list = json.loads(photo_slide_script[start_index + len(photo_info):end_index])

        for elm in photo_list:
            profile_photo_urls.append(elm['source_url'])
    profile_photo_urls = ', '.join(profile_photo_urls)

    user_profile_info = driver.find_elements(By.XPATH, '//div[@class="user-profile_info arrange_unit"]')[0]
    name = ""
    nickname = ""
    name_element = user_profile_info.find_elements(By.XPATH, './h1')
    if len(name_element) > 0:
        full_name = name_element[0].text
        if full_name.find("\"") != -1:
            name = full_name[:full_name.find("\"")] + full_name[full_name.rfind("\"") + 2:]
            nickname = full_name[full_name.find("\"") + 1:full_name.rfind("\"")]
        else:
            name = full_name

    user_passport_stats = user_profile_info.find_elements(By.XPATH, './/div[@class="clearfix"]/ul')[0]
    friend_count_element = user_passport_stats.find_elements(By.XPATH, '//li[@class="friend-count"]')[0]
    review_count_element = user_passport_stats.find_elements(By.XPATH, '//li[@class="review-count"]')[0]
    photo_count_element = user_passport_stats.find_elements(By.XPATH, '//li[@class="photo-count"]')[0]

    friends = int(friend_count_element.find_element(By.XPATH, './strong').text)
    reviews = int(review_count_element.find_element(By.XPATH, './strong').text)
    photos = int(photo_count_element.find_element(By.XPATH, './strong').text)

    elites = []
    badges = user_profile_info.find_elements(By.XPATH, './/div[@class="clearfix u-space-b1"]/a[1]/span')
    if len(badges) > 0:
        for badge in badges:
            if badge.get_attribute("class").find('show-tooltip') != -1:
                continue
            year_text = badge.text
            if year_text.find('Elite') != -1:
                year = year_text.split(' ')[1]
            else:
                year = "20" + str(int(year_text[1:]))
            elites.append(year)
    elites = ', '.join(elites)

    tagline = ""
    tagline_element = user_profile_info.find_elements(By.XPATH, './p[@class="user-tagline"]')
    if len(tagline_element) > 0:
        tagline = tagline_element[0].text[1:-1]

    about_elements = driver.find_elements(By.XPATH, '//div[@class="user-details-overview_sidebar"]/div')

    # Rating Distribution
    star_5 = 0
    star_4 = 0
    star_3 = 0
    star_2 = 0
    star_1 = 0

    # Review Votes
    useful = 0
    funny = 0
    cool = 0

    # Stats
    tips = 0
    review_updates = 0
    bookmarks = 0
    firsts = 0
    followers = 0
    lists = 0

    # Compliments
    thank_you = 0  # compliment
    cute_pic = 0  # heart
    good_writer = 0  # pencil
    hot_stuff = 0  # flame
    just_a_note = 0  # file
    like_your_profile = 0  # profile
    write_more = 0  # write_more
    you_are_cool = 0  # cool
    great_photos = 0  # camera
    great_lists = 0  # list
    you_are_funny = 0  # funny

    # etc_info
    location = ""
    yelping_since = ""
    things_i_love = ""

    find_me_in = ""
    my_hometown = ""
    my_blog_or_website = ""
    when_im_not_yelping = ""
    why_ysrmr = ""
    my_second_fw = ""
    last_great_book = ""
    my_first_concert = ""
    my_favorite_movie = ""
    my_last_meal_on_earth = ""
    dont_tell_anyone_else_but = ""
    most_recent_discovery = ""
    current_crush = ""

    for ysection in about_elements:
        h4 = ysection.find_elements(By.XPATH, './h4')
        if len(h4) > 0:
            section_name = h4[0].text
            # Rating Distribution
            if section_name.find('Rating Distribution') != -1:
                row_elements = ysection.find_elements(By.XPATH, './table/tbody/tr')
                for row_element in row_elements:
                    rating_num = int(row_element.find_elements(By.XPATH, './td/table/tbody/tr/td[2]')[0].text)
                    if row_element.get_attribute('class').find('1') != -1:
                        star_5 = rating_num
                    elif row_element.get_attribute('class').find('2') != -1:
                        star_4 = rating_num
                    elif row_element.get_attribute('class').find('3') != -1:
                        star_3 = rating_num
                    elif row_element.get_attribute('class').find('4') != -1:
                        star_2 = rating_num
                    elif row_element.get_attribute('class').find('5') != -1:
                        star_1 = rating_num

            # Review Votes
            elif section_name.find('Review Votes') != -1:
                votes_elements = ysection.find_elements(By.XPATH, './ul/li')
                for votes_element in votes_elements:
                    votes_text = votes_element.text
                    votes_num = int(votes_element.find_elements(By.XPATH, './strong')[0].text)
                    if votes_text.find('Useful') != -1:
                        useful = votes_num
                    elif votes_text.find('Funny') != -1:
                        funny = votes_num
                    elif votes_text.find('Cool') != -1:
                        cool = votes_num

            # Stats
            elif section_name.find('Stats') != -1:
                stats_elements = ysection.find_elements(By.XPATH, './ul/li')
                for stats_element in stats_elements:
                    stats_text = stats_element.text
                    stats_num = int(stats_element.find_elements(By.XPATH, './strong')[0].text)
                    if stats_text.find('Tips') != -1:
                        tips = stats_num
                    elif stats_text.find('Review Updates') != -1:
                        review_updates = stats_num
                    elif stats_text.find('Bookmarks') != -1:
                        bookmarks = stats_num
                    elif stats_text.find('Firsts') != -1:
                        firsts = stats_num
                    elif stats_text.find('Followers') != -1:
                        followers = stats_num
                    elif stats_text.find('Lists') != -1:
                        lists = stats_num

            # Compliments
            elif section_name.find('Compliments') != -1:
                compliment_elements = ysection.find_elements(By.XPATH, './ul/li')
                if len(compliment_elements) > 0:
                    for compliment_element in compliment_elements:
                        compliment_type = compliment_element.find_elements(By.XPATH, './div[1]/span')[0].get_attribute(
                            'class')
                        compliment_num = int(compliment_element.find_elements(By.XPATH, './div[2]/small')[0].text)
                        if compliment_type.find('icon--18-compliment') != -1:
                            thank_you = compliment_num
                        elif compliment_type.find('icon--18-heart') != -1:
                            cute_pic = compliment_num
                        elif compliment_type.find('icon--18-pencil') != - 1:
                            good_writer = compliment_num
                        elif compliment_type.find('icon--18-flame') != -1:
                            hot_stuff = compliment_num
                        elif compliment_type.find('icon--18-file') != -1:
                            just_a_note = compliment_num
                        elif compliment_type.find('icon--18-profile') != -1:
                            like_your_profile = compliment_num
                        elif compliment_type.find('icon--18-write-more') != -1:
                            write_more = compliment_num
                        elif compliment_type.find('icon--18-cool') != -1:
                            you_are_cool = compliment_num
                        elif compliment_type.find('icon--18-camera') != -1:
                            great_photos = compliment_num
                        elif compliment_type.find('icon--18-list') != -1:
                            great_lists = compliment_num
                        elif compliment_type.find('icon--18-funny') != -1:
                            you_are_funny = compliment_num

        # Etc..
        ul_element = ysection.find_elements(By.XPATH, './ul')
        if len(ul_element) > 0:
            if ul_element[0].get_attribute('class') == 'ylist':
                extra_elements = ul_element[0].find_elements(By.XPATH, './li')
                if len(extra_elements) > 0:
                    for extra_element in extra_elements:
                        title = extra_element.find_elements(By.XPATH, './h4')[0].text
                        content = extra_element.find_elements(By.XPATH, './p')[0].text
                        if title.find("Location") != -1:
                            location = content
                        elif title.find("Yelping Since") != -1:
                            yelping_since = content
                        elif title.find("Things I Love") != -1:
                            things_i_love = content
                        elif title.find("Find Me In") != -1:
                            find_me_in = content
                        elif title.find("My Hometown") != -1:
                            my_hometown = content
                        elif title.find("My Blog Or Website") != -1:
                            my_blog_or_website = content
                        elif title.find("When I’m Not Yelping...") != -1:
                            when_im_not_yelping = content
                        elif title.find("Why You Should Read My Reviews") != -1:
                            why_ysrmr = content
                        elif title.find("My Second Favorite Website") != -1:
                            my_second_fw = content
                        elif title.find("The Last Great Book I Read") != -1:
                            last_great_book = content
                        elif title.find("My First Concert") != -1:
                            my_first_concert = content
                        elif title.find("My Favorite Movie") != -1:
                            my_favorite_movie = content
                        elif title.find("My Last Meal On Earth") != -1:
                            my_last_meal_on_earth = content
                        elif title.find("Don’t Tell Anyone Else But...") != -1:
                            dont_tell_anyone_else_but = content
                        elif title.find("Most Recent Discovery") != -1:
                            most_recent_discovery = content
                        elif title.find("Current Crush") != -1:
                            current_crush = content

    this_profile = [reviewer['user_id'], name, nickname, profile_photo_urls, friends, reviews, photos, elites, tagline,
                    star_5, star_4, star_3, star_2, star_1, useful, funny, cool, tips, review_updates, bookmarks, firsts,
                    followers, lists, thank_you, cute_pic, good_writer, hot_stuff, just_a_note, like_your_profile,
                    write_more, you_are_cool, great_photos, great_lists, you_are_funny, location, yelping_since,
                    things_i_love, find_me_in, my_hometown, my_blog_or_website, when_im_not_yelping, why_ysrmr,
                    my_second_fw, last_great_book, my_first_concert, my_favorite_movie, my_last_meal_on_earth,
                    dont_tell_anyone_else_but, most_recent_discovery, current_crush]
    profiles[index] = this_profile

def review_scraper(driver, index, res, class_names, xpaths):
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
        invalid_object_list.append(index)
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
            if current_page == '?start=' + str((total_page - 1) * 10):
                logger.info('[' + establishment + ']: Oops. Skip this page.')
            else:
                logger.error('[' + establishment + ']: Page Load Failed.')
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
                            if info.find('photos') != -1 or info.find('photo') != -1:
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
                        this_cool_element = div.find_elements(By.XPATH, xpaths['extra_pr_cool'])

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

            if len(list_of_page) == 0:
                end = timer()
                global reviews
                logger.info('[' + establishment + ']: Done. ' + str(total_review_num) + ' reviews are collected.')
                if args.verbose:
                    logger.info('Elapsed Time: ' + str(timedelta(seconds=(end - start))))
                this_reviews = [yelp_ids, establishments, user_ids, ratings, rating_dates, review_texts, is_rotd,
                                is_updated, num_photoss, num_usefuls, num_funnys, num_cools, owner_replied,
                                owner_reply_dates, owner_reply_texts, pr_avg_ratings, pr_avg_usefuls, pr_avg_funnys,
                                pr_avg_cools]
                reviews[index] = this_reviews
                break

def main(args, obj):
    chrome_options = webdriver.ChromeOptions()
    if platform.system() != 'Windows' or args.open_chrome == 0:
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
        yelp_target_df = pd.read_csv(args.target_list_name + '.csv', encoding='utf-8')

    object_name = ""
    if args.collected_object == 'profile':
        if not 'user_id' in yelp_target_df.columns:
            logger.error('Cannot find user_id column in your list file. The program will be terminated.')
            exit()
        object_name = "user"
    else:
        if not 'yelp_id' in yelp_target_df.columns:
            logger.error('Cannot find yelp_id column in your list file. The program will be terminated.')
            exit()
        object_name = "restaurant"

    if args.verbose:
        logger.info('The target list file has been successfully loaded.')
        logger.info('The total number of ' + object_name + 's is ' + str(len(yelp_target_df)) + '.')

    if args.index_specified_mode:
        index_set = sorted(utils.load_index_set('index_set.txt'))
        if not utils.check_index_list(index_set, len(yelp_target_df) - 1):
            logger.error('Check your index_set.txt. It may contains invalid indices. The program will be terminated.')
            exit()

    else:
        # Check max index
        if args.max_index == -1:
            max_index = len(yelp_target_df) - 1
        else:
            if args.max_index > len(yelp_target_df) - 1:
                logger.warning('Max index is too large. It is set to the last index ' + str(len(yelp_target_df) - 1) + '.')
                max_index = len(yelp_target_df) - 1
            else:
                max_index = args.max_index
        index_set = list(range(args.min_index, max_index + 1, 1))

    target_obj_num = len(index_set)
    yelp_target_df = yelp_target_df.loc[index_set]
    if args.verbose:
        logger.info('The number of target ' + object_name + 's is ' + str(target_obj_num))

    start = timer()
    while(True):
        global success_num, fail_num
        if len(index_set) == 0:
            break

        try:
            for index, object in yelp_target_df.iterrows():
                if args.collected_object == 'profile':
                    profile_scraper(driver, index, object)
                elif args.collected_object == 'review':
                    review_scraper(driver, index, object, class_names, xpaths)
                else:
                    res_scraper(driver, index, object)
                success_num += 1
                index_set.pop(0)
        except:
            fail_num += 1
            error_index = index_set.pop(0)
            if not error_index in invalid_object_list:
                fail_list.append(error_index)
            logger.error(sys.exc_info()[0])
            logger.error(traceback.format_exc())
            logger.error('Index ' + str(error_index) +': Error occured. This ' + object_name + ' gets skipped.')
            if len(index_set) > 0:
                yelp_target_df = yelp_target_df.loc[index_set]

    logger.info('-----------------')
    logger.info('Report')
    logger.info('Total Number of Targets: ' + str(target_obj_num))
    logger.info('Success: ' + str(success_num))
    logger.info('Fail: ' + str(fail_num))
    if fail_num > 0:
        msg = ", ".join(map(str, fail_list))
        logger.info(msg)
        if len(invalid_object_list) > 0:
            msg2 = ', '.join(map(str, invalid_object_list))
            logger.info('The following ' + object_name + 's has no information: ' + msg2)
    logger.info('-----------------')

    if success_num == 0:
        logger.info('Nothing to save because NO DATA HAVE BEEN COLLECTED :(')
        logger.info('Please check class names and xpaths in keys_for_scraping.ini file. They may be not valid.')

    else:
        logger.info('Saving the result...')
        global reviews, profiles, restaurants
        if args.collected_object == 'profile':
            results = utils.set_to_df(profiles, 'profile')
        elif args.collected_object == 'review':
            results = utils.set_to_df(reviews, 'review')
        else:
            results = utils.set_to_df(restaurants, 'restaurant')

        if args.collected_object == 'profile':
            file_name = 'yelp_profile.csv'
        elif args.collected_object == 'review':
            file_name = 'yelp_review.csv'
        else:
            file_name = 'yelp_res_info.csv'

        if args.index_suffix:
            if args.index_specified_mode:
                if args.collected_object == 'profile':
                    file_name = 'yelp_profile_index_specified (' + str(success_num) + ' of ' + str(target_obj_num) + ' users).csv'
                elif args.collected_object == 'review':
                    file_name = 'yelp_review_index_specified (' + str(success_num) + ' of ' + str(target_obj_num) + ' reviews).csv'
                else:
                    file_name = 'yelp_res_info_index_specified (' + str(success_num) + ' of ' + str(target_obj_num) + ' reviews).csv'
            else:
                if fail_num == 0:
                    if args.collected_object == 'profile':
                        file_name = 'yelp_profile_from_' + str(args.min_index) + '_to_' + str(max_index) + '.csv'
                    elif args.collected_object == 'review':
                        file_name = 'yelp_review_from_' + str(args.min_index) + '_to_' + str(max_index) + '.csv'
                    else:
                        file_name = 'yelp_res_info_from_' + str(args.min_index) + '_to_' + str(max_index) + '.csv'
                else:
                    if args.collected_object == 'profile':
                        file_name = 'yelp_profile_from_' + str(args.min_index) + '_to_' + str(max_index) + \
                                    ' (' + str(fail_num) + ' fails).csv'
                    elif args.collected_object == 'review':
                        file_name = 'yelp_review_from_' + str(args.min_index) + '_to_' + str(max_index) + \
                                ' (' + str(fail_num) + ' fails).csv'
                    else:
                        file_name = 'yelp_res_info_' + str(args.min_index) + '_to_' + str(max_index) + \
                                ' (' + str(fail_num) + ' fails).csv'
        end = timer()
        if args.aws_mode:
            with io.StringIO() as csv_buffer:
                results.to_csv(csv_buffer, index=False)
                response = s3.put_object(Bucket=bucket_name, Key=file_name, Body=csv_buffer.getvalue())
                status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")
                if status == 200:
                    logger.info(
                        'Done. All work you requested has been finished. The program will be terminated.')
                else:
                    logger.error('Failed to save the result file to your S3 bucket.')
        else:
            results.to_csv(file_name, encoding='utf-8', index=False)
            logger.info('Done. All work you requested has been finished. The program will be terminated.')
        logger.info('Total Elapsed Time: ' + str(timedelta(seconds=(end - start))))

if __name__ == '__main__':
    parser_error = False
    # args check
    if args.index_specified_mode:
        if not os.path.exists('index_set.txt'):
            print('index_set.txt cannot be found. The program will be terminated.')
            exit()

        if len(utils.load_index_set('index_set.txt')) == 0:
            print('index_set.txt is empty or invalid. The program will be terminated.')
            exit()

    else:
        if args.min_index < 0:
            parser_error = True
            parser.error('Min index cannot be negative.')

        if args.max_index != -1 & args.max_index < 0:
            parser_error = True
            parser.error('Max index must be -1 or non-negative.')

        if (args.max_index != -1) & (args.min_index > args.max_index):
            parser_error = True
            parser.error('Min index cannot be larger than max index.')

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
            prefix = args.target_list_name + '.csv'
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
                    print(args.target_list_name + '.csv cannot be found. The program will be terminated.')
                    exit()
    else:
        if not os.path.exists(args.target_list_name + '.csv'):
            print(args.target_list_name + '.csv cannot be found. The program will be terminated.')
            exit()

    if not os.path.exists('keys_for_scraping.ini'):
        print('keys_for_scraping.ini cannot be found. The program will be terminated.')
        exit()

    main(args, obj)