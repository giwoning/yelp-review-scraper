import configparser

import pandas as pd

def load_class_name_and_xpath(_path):
    names = {}
    xpaths = {}

    parser = configparser.ConfigParser()
    parser.read(_path)

    for option in parser.options('Class Names'):
        names[option] = parser.get('Class Names', option)[1:-1]

    for option in parser.options('XPaths'):
        xpaths[option] = parser.get('XPaths', option)[1:-1]

    return names, xpaths

def load_aws_keys(_path):
    aws_info = {}

    parser = configparser.ConfigParser()
    parser.read(_path)

    for option in parser.options('AWS Keys'):
        aws_info[option] = parser.get('AWS Keys', option)[1:-1]

    return aws_info['aws_access_key'], aws_info['aws_secret_key'], aws_info['aws_region'], aws_info['aws_bucket_name']

def load_index_set(_path):
    iset = set()
    with open(_path, 'r') as f:
        for line in f:
            line = line.strip().split(',')
            if '' in line:
                line.remove('')
            iset.update([int(index) for index in line])
    return iset

def check_index_list(ilist, max_index):
    pass_ = True
    for index in ilist:
        if index < 0 or index > max_index:
            pass_ = False
    return pass_

def set_to_df(_set):
    review_info = ['userid', 'yelpid', 'establishment', 'review', 'rating', 'rating_date', 'rotd', 'updated', 'photos',
                   'useful', 'funny', 'cool', 'owner_replied', 'owner_reply_date', 'owner_reply', 'pr_avg_ratings',
                   'pr_avg_usefuls', 'pr_avg_funnys', 'pr_avg_cools']
    all_reviews = pd.DataFrame(columns=review_info)

    for reviews in _set.values():
        yelp_ids = reviews[0]
        establishments = reviews[1]
        user_ids = reviews[2]
        ratings = reviews[3]
        rating_dates = reviews[4]
        review_texts = reviews[5]
        is_rotd = reviews[6]
        is_updated = reviews[7]
        num_photos = reviews[8]
        num_usefuls = reviews[9]
        num_funnys = reviews[10]
        num_cools = reviews[11]
        owner_replied = reviews[12]
        owner_reply_dates = reviews[13]
        owner_reply_texts = reviews[14]
        pr_avg_ratings = reviews[15]
        pr_avg_usefuls = reviews[16]
        pr_avg_funnys = reviews[17]
        pr_avg_cools = reviews[18]

        this_reviews = pd.DataFrame({'userid': user_ids,
                                      'yelpid': yelp_ids,
                                      'establishment': establishments,
                                      'review': review_texts,
                                      'rating': ratings,
                                      'rating_date': rating_dates,
                                      'rotd': is_rotd,
                                      'updated': is_updated,
                                      'photos': num_photos,
                                      'useful': num_usefuls,
                                      'funny': num_funnys,
                                      'cool': num_cools,
                                      'owner_replied': owner_replied,
                                      'owner_reply_date': owner_reply_dates,
                                      'owner_reply': owner_reply_texts,
                                      'pr_avg_ratings': pr_avg_ratings,
                                      'pr_avg_usefuls': pr_avg_usefuls,
                                      'pr_avg_funnys': pr_avg_funnys,
                                      'pr_avg_cools': pr_avg_cools})

        all_reviews = pd.concat([all_reviews, this_reviews])

    return all_reviews