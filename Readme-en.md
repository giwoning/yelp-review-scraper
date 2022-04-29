# Yelp Review Scraper

This code is made for scraping reviews from Yelp website. You have to prepare a file in csv in which **name and Yelp ID** of target restaurants are contained.

The following data will be collected:

* Yelp ID: It is the restaurant unique ID on Yelp.
* Establishment: It is the restaurant name on Yelp.
* User ID: It is the user's unique ID who left a review (NOTE: It is different from the actual user ID).
* Review: It is a review content.
* Ratings: It is a user-rated scoring (from 1 to 5, only integer) in a review.
* Rating Date: It is a date when a review was left.
* ROTD: It is the abbreviation of '**R**eview **O**f **T**he **D**ay', which means the review was a great help to other users.
* Updated: It is whether a review was modified at least once.
* Number of Photos: It is the number of photos attached to a review.
* Number of Usefuls: It is the number of 'Useful' for a review.
* Number of Funnys: It is the number of 'Funny' for a review.
* Number of Cools: It is the number of 'Cools' for a review.
* Owner Replied: It is whether any restaurant staff (manager, or owner) replied a review.
* Owner Reply Date: It is a date when reply was left.
* Owner Reply: 식당 관계자의 답글입니다.
* Previous Average Ratings: 이전에 남겼던 리뷰 평점의 평균입니다.
* Previous Average Usefuls: 이전에 남겼던 리뷰들의 Useful 개수의 평균입니다.
* Previous Average Funnys: 이전에 남겼던 리뷰들의 Funny 개수의 평균입니다.
* Previous Average Cools: 이전에 남겼된 리뷰들의 Cool 개수의 평균입니다.

## How it works?
This code is written by Python 3. It is for web scraping using Selenium library. You have to the restaurant list file in advance. It scrapes all reviews of each restaurant in the order of restaurants in the restaurant list file. Note that it scrapes _only English reviews_, although Yelp provides multi-lingual reviews.
Yelp provides at most 10 reviews on a page. So, if a restaurant has more than 10 reviews, then it has several review pages. Yelp automatically detect scraping with high probablility if reviews are scraped in page order. Hence, this program scrapes reviews by changing another page randomly after all reviews of one page get scraped.
If an error occurs during scraping reviews of a restaurant, then this program does not save them and move to next restaurant. After visiting all restaurants, it reports _the number of rastaurants whose reviews are successfully scraped_, _the number of rastaurants whose reviews fail to be scraped and the indices of such rastaurnats_. Finally, it saves all reviews to `.csv` format. 

## Restaurant List File
이 프로그램이 수집할 식당들의 이름과 Yelp ID를 담은 파일입니다. 식당 이름은 반드시 Yelp에 등록되어 있는 식당 이름과 같을 필요가 없습니다. `.csv` 파일로 아래와 같은 형식으로 되어있어야합니다. 특히 Column 이름(`res_name` 및 `yelp_id`)이 같은지 반드시 확인하여 주십시오.
| res_name | yelp_id |
| ----- | ----- |
| Benemon | benemon-new-york |
| BXL Cafe | bxl-cafe-new-york-2 |
| Locanda Verde | locanda-verde-new-york |
| Zoralie Restaurant | zoralie-restaurant-new-york |
| Porteno Restaurant | porteno-restaurant-new-york |
...

AWS Mode를 이용할 경우, 이 파일은 Bucket에 저장되어 있어야합니다. 그 외에는 이 코드가 저장되어 있는 폴더에 해당 파일을 저장해주십시오. 

## Setup
모든 코드는 Python 3.7.6, Windows 10 Version 21H2 및 Selenium 4.0.0에서 개발되었고 테스트 되었습니다.

Windows 환경에서 Anaconda3가 설치되어 있다면, Anaconda Prompt를 실행하여 경로를 이 GitHub에서 Clone한 폴더로 설정하고, 아래의 가상환경을 설정하여 코드를 실행할 수 있습니다:

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
이 코드를 정상적으로 실행하기 위해 아래의 패키지들이 설치되어 있는지 확인하여 주십시오.
* pandas 1.4.2
* selenium 4.0.0
* boto3 1.21.32
* webdriver-manager 3.5.4

## AWS Mode
만약 AWS EC2와 S3를 사용한다면, 코드 실행시 `--aws_mode=1` 인자를 포함시켜 AWS 모드를 활성화할 수 있습니다. `aws_key.ini` 파일에서 개인의 AWS 서비스에 접근하기 위한 4가지의 정보를 입력해야합니다.

## Command Line Arguments
코드 실행 시 아래와 같은 옵션을 설정할 수 있습니다.

### Scraper Options
| Argument | Type | Description | Default |
| ----- | ----- | ----- | ----- |
| `--start_index` | unsigned int | 시작 인덱스 값입니다. `전체 식당 개수 - 1`보다 클 수 없습니다.| 0 |
| `--end_index` | unsigned int | 끝 인덱스 값입니다. 시작 인덱스 값보다는 크고, `전체 식당 개수 - 1`보다 작아야 합니다. -1로 설정하면, 마지막 인덱스로 설정됩니다.| -1 |
| `--wait_time_for_new_index` | unsigned int | 한 식당에서 다른 식당으로 넘어갈 때 대기 시간(초)입니다. | 10 |
| `--wait_time_for_establishment` | unsigned int | 식당의 Yelp 상에 등록된 이름을 성공적으로 불러올 때 까지의 대기 시간(초)입니다. | 10 |
| `--wait_time_for_next_page` | unsigend int | 식당의 한 리뷰 페이지에서 다음 리뷰 페이지로 넘어갈 때 대기 시간(초)입니다. | 10 |

### Display Option
| Argument | Type | Description | Default |
| ----- | ----- | ----- | ----- |
| `--verbose` | boolean | 1이면 리뷰 수집 중 그 상황을 자세히 보고합니다. | 1 |

### Dataset Option
| Argument | Type | Description | Default |
| ----- | ----- | ----- | ----- |
| `--dataset_name` | string | 식당 리스트 파일의 이름입니다. | 'Res_List_From_Inspection' |

### AWS Option
| Argument | Type | Description | Default |
| ----- | ----- | ----- | ----- |
| `--aws_mode` | boolean | 1이면 AWS 모드를 활성화합니다 (**AWS Mode** 섹션 참고). | 0 |

### Chrome Option
| Argument | Type | Description | Default |
| ----- | ----- | ----- | ----- |
| `--chrome_open` | boolean | 1이면 크롬 창을 띄워 리뷰를 수집 중인 식당 웹페이지를 실시간으로 볼 수 있습니다. Windows가 아닌 환경에서는 항상 0으로 강제 설정됩니다. | 0 |

### Save Options
| Argument | Type | Description | Default |
| ----- | ----- | ----- | ----- |
| `--index_suffix` | boolean | 결과 파일을 저장할 때, 파일명 뒤에 시작 인덱스 값과 끝 인덱스 값을 붙입니다. (yelp_review_**from_0_to_100**.csv) | 1 |

## Keys for Scraping
The class names in Yelp Web HTML are not intuitive. Moreover, they are frequently changed. If the program fail to scrape any reviews of resturants, you should check whether some class names are changed. Note that `keys_for_scraping.ini` contains all class names needed for scraping.
