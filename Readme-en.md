[Korean](README.md)

# Yelp Review Scraper

This code is designed for scraping reviews from Yelp. It must be provided with **a file that contains target Yelp IDs** in `.csv` format (the "target list"). `Res_List_From_Inspection.csv` is an example file.

The following data will be collected:

* Yelp ID: It is the restaurant unique ID on Yelp.
* Establishment: It is the restaurant name on Yelp.
* User ID: It is the user's unique ID who left a review (NOTE: It is different from the actual user ID).
* Review: It is a review content.
* Ratings: It is a user-rated scoring (from 1 to 5, only integer) in a review.
* Rating Date: It is a date when a review was left.
* ROTD: It is the abbreviation of '**R**eview **O**f **T**he **D**ay', which means the review was a great help to other users.
* Updated: It is whether a review was edited at least once.
* Number of Photos: It is the number of photos attached to a review.
* Number of Usefuls: It is the number of 'Useful' for a review.
* Number of Funnys: It is the number of 'Funny' for a review.
* Number of Cools: It is the number of 'Cools' for a review.
* Owner Replied: It is whether a restaurant staff (manager or owner) replied a review.
* Owner Reply Date: It is a date when a reply was left.
* Owner Reply: It is a reply content.
* Previous Average Ratings: It is the average rating of all previous reviews of a user.
* Previous Average Usefuls: It is the average number of 'Useful' of all previous reviews of a user.
* Previous Average Funnys: It is the average number of 'Funny' of all previous reviews of a user.
* Previous Average Cools: It is the average number of 'Cools' of all previous reviews of a user.

## How it works?
This code is written in Python 3 and Selenium is selected as a tool for scraping. The program assigns an index to each restaurant in the target list from 0. A user can arbitrarily narrow down the range of target restaurants by specifying the min and max index. It scrapes reviews of the given target restaurants in the order of indices. Note that it scrapes _only English reviews_, although Yelp provides multi-lingual reviews.

A restaurant whose reviews are more than 10 has several review pages because Yelp displays at most 10 reviews on a page. Yelp automatically detect scraping with high probablility if reviews are scraped in page order. Hence, this program scrapes reviews by changing another page randomly after all reviews of one page get scraped.

If an error occurs during scraping reviews of a restaurant, then this program does not save them and move to next restaurant. After visiting all restaurants, it reports _the number of rastaurants whose reviews are successfully scraped_, _the number of rastaurants whose reviews fail to be scraped and the indices of such rastaurnats_. Finally, it saves all reviews to `.csv` format. 

## Target List
The target list is a `.csv` file in which target Yelp IDs are contained. It should include a column named `yelp_id` like below:
| yelp_id |
| ----- |
| benemon-new-york |
| bxl-cafe-new-york-2 |
| locanda-verde-new-york |
| zoralie-restaurant-new-york |
| porteno-restaurant-new-york |
...

If AWS mode is on, the target list must be located in S3 Bucket. Otherwise, the code and target list must be in the same folder.

## Specify Indices
You can specifiy indices which the program will work on by typing indices on `index_set.txt`. The distinct indices must be separated by comma (','). If some indices in `index_set.txt` are out of index range, the program will detect it and be terminated immediately.

## Setup
All code was developed ans tested on Windows 10 Version 21H2 with Python 3.7.6 and Selenium 4.0.0.

If you installed Anaconda 3, execute Anaconda prompt, change the directory to a folder to which you cloned this GitHub, setup an virtual environment to run the code like below:

```shell
conda create -n yelp_review_scraper           # Create a virtual environment named 'yelp_review_scraper'
conda activate yelp_review_scraper            # Activate 'yelp_review_scraper'
conda install pip                             # Install pip (skip if you alreay installed it)
pip install -r requirements.txt               # Install dependencies
python yelp_review_scraper.py --end_index=10  # Execute the main code with options
# ...
conda deactivate
```

### Requirements
Please check whether following packages are installed before running the code.
* pandas 1.4.2
* selenium 4.0.0
* boto3 1.21.32
* webdriver-manager 3.5.4

## AWS Mode
If you use AWS EC2 and S3, you can activate AWS mode by including `--aws_mode==1` argument when running the code. When it is activated, all data will be saved into S3 bucket. You should fill out the following values in `aws_key.ini` to access your AWS serivces. All values must be enclosed in single quotes (').

| Value | Description |
| ----- | ----- |
| aws_access_key | Refer to https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html |
| aws_secret_key | Refer to https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html |
| aws_region | It is AWS region your AWS service is working on. |
| aws_bucket_name | It is the name AWS S3 bucket in which the target list is located and the output will be saved. |

## Options
You can control the following options when running the code:

### Scraper Options
| Argument | Type | Description | Default |
| ----- | ----- | ----- | ----- |
| `--min_index` | int | This is an index of a first target restaurant. It must be smaller than or equal to max index, and cannot be larger than `the total number of target restaurants - 1`.| 0 |
| `--max_index` | int | This is an index of a last target restaurant. It must be larger than or equal to min index, and cannot be larger than `the total number of target restaurants - 1`. -1 implies the last index of the target list.| -1 |
| `--wait_time_for_new_index` | int | This is waiting time for a next index. | 10 |
| `--wait_time_for_establishment` | int | This is waiting time for loading the name of a restuarant.  | 10 |
| `--wait_time_for_next_page` | int | The is waiting time for a next review page of a restaurant.  | 10 |
| `--index_specified_mode` | int | 1 = Activate Index Specified Mode (refer to **Specifiy Indices**). | 0

Three waiting times should be decided in a balance between scraping speed and fail frequency. If too short, the work may frequently fail because the program tries to scrape reviews before a page is completely loaded. If too long, the task may drag on unnecessarily. 

### Display Option
| Argument | Type | Description | Default |
| ----- | ----- | ----- | ----- |
| `--verbose` | boolean | 1 = The program will display additional details on the console. | 1 |

### Dataset Option
| Argument | Type | Description | Default |
| ----- | ----- | ----- | ----- |
| `--dataset_name` | string | This is the name of the target list. | 'Res_List_From_Inspection' |

### AWS Option
| Argument | Type | Description | Default |
| ----- | ----- | ----- | ----- |
| `--aws_mode` | boolean | 1 = Activate AWS mode (refer to **AWS Mode**). | 0 |

### Chrome Option
| Argument | Type | Description | Default |
| ----- | ----- | ----- | ----- |
| `--open_chrome` | boolean | 1 = The program will open the Chrome window that shows the process of scraping. Always 0 for non-Windows platform. | 0 |

### Save Options
| Argument | Type | Description | Default |
| ----- | ----- | ----- | ----- |
| `--index_suffix` | boolean | 1 = The program will attach min and max index to a file name when it saves the output. (ex. yelp_review_**from_0_to_100**.csv) | 1 |

## Keys for Scraping
The class names in Yelp HTML are not intuitive. Moreover, they are frequently changed. If the program fails to scrape any reviews of resturants, you should check whether some class names are changed. Note that `keys_for_scraping.ini` contains all class names needed for scraping. All values must be enclosed in single quotes (').

## Change Logs
Ver 1.0.1 - 2022/05/06

### New feature
* Index Specified Mode
  * It allows you to directly input indices of restaurants to collect reviews.
  * Options `start_index` and `end_index` will be ignored.
  * It requires you to create `index_set.txt` file in which indices of retaurants to collect reviews are inputted. Each distinct index must be seperated by comma (',').

### Changes
* Now when `index_suffix` option is turned on, the number of failed cases will be additionally attached to a file name.
* Option names `start_index` and `end_index` are changed to `min_index` and `max_index` resepcitvely.

### Bugs
* Fixed the number of photos attached to a review is inaccruately collected.
