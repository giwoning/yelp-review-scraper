[English](Readme-en.md)

# Yelp Scraper
이 코드는 Yelp의 레스토랑 정보, 레스토랑에 등록된 리뷰, 사용자 프로필 정보를 수집하기 위해 작성되었습니다. 수집하고자 하는 대상에 맞게 아래 3가지 모드가 지원됩니다.

### Restaurant
이 모드는 Yelp 레스토랑 정보를 수집합니다. 수집하고자하는 Yelp에 등록된 식당의 **Yelp ID가 담겨있는 파일** (이하 대상 리스트 파일)만 준비하면 됩니다.

수집되는 정보는 아래와 같습니다.
* Yelp ID: Yelp 상의 식당 ID입니다.
* Name: Yelp 상에 등록된 식당 이름입니다.
* Closed: 폐점여부입니다.
* Verified: Yelp로부터 Verified License를 취득하였는지의 여부입니다.
* Rating: 해당 레스토랑의 평균 평점입니다.
* Review: 해당 레스토랑에 등록된 리뷰 개수입니다.
* Photos: 해당 레스토랑의 리뷰에 등록된 사진 개수입니다.
* Price Range: 해당 레스토랑의 1인당 비용을 범위로 표시한 것입니다. $($10 미만)부터 $$$$($61 초과)까지 있습니다.
* Category List: 해당 레스토랑에서 판매하고 있는 음식의 분류입니다.
* Phone Number: 해당 레스토랑의 전화번호입니다.
* Address: 해당 레스토랑의 주소입니다.
* Opening Times: 해당 레스토랑의 영업 시간입니다.
* More Business Info: 해당 레스토랑의 영업 정보입니다.

### Review
이 모드는 Yelp 레스토랑 사이트에서 제공하는 리뷰를 수집합니다. 대상 리스트 파일만 준비하면 됩니다.

수집되는 정보는 아래와 같습니다.

* Yelp ID: Yelp 상의 식당 ID입니다.
* Establishment: Yelp 상에 등록된 식당 이름입니다.
* User ID: 식당에 리뷰를 작성한 사용자의 고유 ID입니다.
* Review: 리뷰의 본문입니다.
* Ratings: 리뷰에서 사용자가 부여한 평점(1~5점)입니다.
* Rating Date: 리뷰를 남긴 날짜입니다.
* ROTD: '**R**eview **O**f **T**he **D**ay'의 줄임말로, 해당 리뷰가 다른 사용자들에게 큰 도움이 되었음을 의미합니다.
* Updated: 해당 리뷰가 수정되었는지의 여부입니다.
* Number of Photos: 해당 리뷰에 같이 첨부된 사진 개수입니다.
* Number of Usefuls: 해당 리뷰가 받은 'Useful' 개수입니다.
* Number of Funnys: 해당 리뷰가 받은 'Funny' 개수입니다.
* Number of Cools: 해당 리뷰가 받은 'Cools' 개수입니다.
* Owner Replied: 식당 관계자가 해당 리뷰에 답글을 남겼는지의 여부입니다.
* Owner Reply Date: 식당 관계자가 답글을 남긴 날짜입니다.
* Owner Reply: 식당 관계자의 답글입니다.
* Previous Average Ratings: 이전에 남겼던 리뷰 평점의 평균입니다.
* Previous Average Usefuls: 이전에 남겼던 리뷰들의 Useful 개수의 평균입니다.
* Previous Average Funnys: 이전에 남겼던 리뷰들의 Funny 개수의 평균입니다.
* Previous Average Cools: 이전에 남겼된 리뷰들의 Cool 개수의 평균입니다.

### Profile
이 모드는 Yelp 사용자 프로필 페이지에서 제공하는 정보들을 수집합니다. 수집하고자하는 Yelp 사용자들의 **User ID가 담겨있는 파일** (이하 대상 리스트 파일)만 준비하면 됩니다.

수집되는 정보는 아래와 같습니다.

* User ID: Yelp상의 사용자 ID입니다 (주의: 로그인 ID와는 다릅니다).
* Name: 사용자 이름입니다.
* Nickname: 사용자 별칭입니다.
* Profile Photo URLs: 프로필에 업로드한 사진들의 URL입니다.
* Friends: 친구수입니다.
* Reviews: 작성한 리뷰 개수입니다.
* Photos: 리뷰에 첨부한 사진 개수입니다.
* Elites: Yelp Elite에 뽑힌 연도입니다.
* Tagline: 한 줄 소개입니다.
* Rating Distribution: 사용자가 내린 평점의 분포입니다. 
* Review Votes: 사용자의 리뷰에 다른 사용자들이 평가한 유익함입니다.
* Compliment: 다른 사용자들에게 받은 찬사입니다.
* Location: 사용자의 거주지입니다.
* Yelping Since: Yelp를 사용하기 시작한 시점입니다.
* Etc: 그 외 개인적인 정보입니다. 
  * Things I Love, Find Me In, My Hometown, My Blog Or Website, When I’m Not Yelping..., Why You Should Read My Reviews, My Second Favorite Website, The Last Great Book I Read, My First Concert, My Favorite Movie, My Last Meal On Earth, Don’t Tell Anyone Else But..., Most Recent Discovery, Current Crush
 
## How it works?
이 코드는 Python 3으로 작성되었으며, Selenium을 이용한 웹 크롤링을 수행합니다. 이 코드는 수집 대상이 파일로 존재한다고 가정하기 때문에, 반드시 대상 리스트 파일을 사전에 준비하여야 합니다. `index_set.txt`에 있는 인덱스나 최소 인덱스에 대응하는 식당부터 최대 인덱스에 대응하는 대상까지 순서대로 각 대상의 정보를 수집합니다. 리뷰의 경우, Yelp에서는 다중 언어의 리뷰를 볼 수 있으나, 이 프로그램은 _영어 리뷰만 수집합니다_.

어떤 대상의 정보 수집 중 오류가 발생하면, 그때까지 수집하였던 정보는 저장하지 않고 다음 대상으로 넘어갑니다. 모든 대상의 정보 수집이 완료가 되면, _성공적으로 정보를 수집한 대상 개수_ 와 _정보 수집에 실패한 대상 개수 및 그 대상들의 인덱스들_ 을 보고한 뒤, csv 파일로 저장하며 프로그램을 종료합니다.

## Target List
이 프로그램이 수집할 대상들의 ID를 담은 파일입니다. `.csv` 파일로 아래와 같은 형식으로 되어있어야합니다. Yelp ID와 User ID가 담긴 열의 첫 행은 반드시 각각 `yelp_id`와 `user_id`로 설정해야합니다.
| yelp_id |
| ----- |
| benemon-new-york |
| bxl-cafe-new-york-2 |
| locanda-verde-new-york |
| zoralie-restaurant-new-york |
| porteno-restaurant-new-york |
...

| user_id |
| ----- |
| 7pSl0bgTkOzuvMU937Oaeg |
| sb8y8mjEzoZWgKuLadPMiw |
| H7lo8f4fuL2n3ubtmnfUsg |
| O4iAzVQSAyWDcx7k-sCJpA |
| noD5q49ct4IrXDI8Z1V4OQ |
...

AWS Mode를 이용할 경우, 이 파일은 Bucket에 저장되어 있어야합니다. 그 외에는 이 코드가 저장되어 있는 폴더에 해당 파일을 저장해주십시오. 

## Specify Indices
만약 특정 지정한 인덱스에 대해서만 작업을 수행하고 싶다면, `index_set.txt` 파일에 인덱스들을 입력하십시오. 서로 다른 인덱스들은 반드시 콤마(',')로 분리되어야 합니다. 만약 범위를 벗어난 인덱스가 있을 경우, 프로그램은 이를 감지하여 프로그램이 즉시 종료됩니다.

## Setup
모든 코드는 Python 3.7.6, Windows 10 Version 21H2 및 Selenium 4.0.0에서 개발되었고 테스트 되었습니다.

Windows 환경에서 Anaconda3가 설치되어 있다면, Anaconda Prompt를 실행하여 경로를 이 GitHub에서 Clone한 폴더로 설정하고, 아래의 가상환경을 설정하여 코드를 실행할 수 있습니다:

```shell
conda create -n yelp_review_scraper                                      # Create a virtual environment named 'yelp_review_scraper'
conda activate yelp_review_scraper                                       # Activate 'yelp_review_scraper'
conda install pip                                                        # Install pip (skip if you alreay installed it)
pip install -r requirements.txt                                          # Install dependencies
python yelp_review_scraper.py --collected_object=profile --max_index=10  # Execute the main code with options
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
만약 AWS EC2와 S3를 사용한다면, 코드 실행시 `--aws_mode` 인자를 포함시켜 AWS 모드를 활성화할 수 있습니다. `aws_key.ini` 파일에서 개인의 AWS 서비스에 접근하기 위한 4가지의 정보를 입력해야합니다. 위 값들은 모두 작은 따옴표(')로 둘러싸야합니다.
| Value | Description |
| ----- | ----- |
| aws_access_key | https://docs.aws.amazon.com/ko_kr/IAM/latest/UserGuide/id_credentials_access-keys.html 참조 |
| aws_secret_key | https://docs.aws.amazon.com/ko_kr/IAM/latest/UserGuide/id_credentials_access-keys.html 참조 |
| aws_region | AWS 서비스를 사용하는 지역 코드입니다. |
| aws_bucket_name | AWS S3에서 사용자가 설정한 Bucket 이름입니다. |

## Options
코드 실행 시 아래와 같은 옵션을 설정할 수 있습니다.

### Mode Option (Required)
| Argument | Type | Description | Default |
| ----- | ----- | ----- | ----- |
| `--collected_object` | string | 수집 대상을 선택합니다. restaurant, review, profile 중 하나를 선택해야합니다. | - |

### Scraper Options
| Argument | Type | Description | Default |
| ----- | ----- | ----- | ----- |
| `--min_index` | int | 시작 인덱스 값입니다. 끝 인덱스 값보다 작거나 같아야 하고, `전체 식당 개수 - 1`보다 클 수 없습니다.| 0 |
| `--max_index` | int | 끝 인덱스 값입니다. 시작 인덱스 값보다는 크거나 같고, `전체 식당 개수 - 1`보다 작아야 합니다. -1로 설정하면, 마지막 인덱스로 설정됩니다.| -1 |
| `--wait_time_for_new_index` | int | 한 식당에서 다른 식당으로 넘어갈 때 대기 시간(초)입니다. | 10 |
| `--wait_time_for_establishment` | int | 식당의 Yelp 상에 등록된 이름을 성공적으로 불러올 때 까지의 대기 시간(초)입니다. | 10 |
| `--wait_time_for_next_page` | int | 식당의 한 리뷰 페이지에서 다음 리뷰 페이지로 넘어갈 때 대기 시간(초)입니다. | 10 |
| `--index_specified_mode` | bool | True면 리뷰를 수집할 식당의 인덱스들을 `index_set.txt`에서 불러옵니다.  | False |

세 대기 시간 값은 리뷰 수집 속도와 수집 실패 빈도 사이에서 적절히 조절해야 합니다. 너무 짧게 설정하면, 페이지가 모두 로드되기 전에 수집을 시도하기 때문에 오류가 발생하게 됩니다. 반면, 너무 길게 설정하면 리뷰 수집 시간이 지나치게 길어질 수 있습니다.

### Log Options
| Argument | Type | Description | Default |
| ----- | ----- | ----- | ----- |
| `--verbose` | boolean | True면 리뷰 수집 중 그 상황을 자세히 보고합니다. | True |
| `--save_log` | boolean| True면 리뷰 수집 중 발생한 로그들을 파일로 저장합니다. | False |

### Dataset Option
| Argument | Type | Description | Default |
| ----- | ----- | ----- | ----- |
| `--target_list_name` | string | 대상 리스트 파일의 이름입니다. | 'User_List' |

### AWS Option
| Argument | Type | Description | Default |
| ----- | ----- | ----- | ----- |
| `--aws_mode` | boolean | True면 AWS 모드를 활성화합니다 (**AWS Mode** 섹션 참고). | False |

### Chrome Option
| Argument | Type | Description | Default |
| ----- | ----- | ----- | ----- |
| `--open_chrome` | boolean | True면 크롬 창을 띄워 리뷰를 수집 중인 식당 웹페이지를 실시간으로 볼 수 있습니다. Windows가 아닌 환경에서는 항상 False로 강제 설정됩니다. | False |

### Save Options
| Argument | Type | Description | Default |
| ----- | ----- | ----- | ----- |
| `--index_suffix` | boolean | True면 결과 파일을 저장할 때, 파일명 뒤에 시작 인덱스 값과 끝 인덱스 값을 붙입니다. (yelp_review_**from_0_to_100**.csv) | True |

## Keys for Scraping
Yelp HTML의 class 이름은 직관적이지 않고, 때때로 바뀌는 경우가 있습니다. 만약 모든 식당의 리뷰가 정상적으로 수집되지 않는다면, class 이름이 변경되었는지 확인하여야합니다. 리뷰 수집에 필요한 class 이름들은 `keys_for_scraping.ini`에 모두 기록되어 있습니다. 모든 값들은 작은 따옴표(')로 둘러싸야 합니다.

## Change Logs
Ver 1.1.0
### 기능 추가
* Yelp 사용자들의 프로필 정보를 수집하는 기능이 추가됩니다. 필수 옵션 `--collected_object`를 `review`로 설정하면 활성화할 수 있습니다. 

### 수정
* 필수 옵션인 `collected_object`가 추가됩니다. 코드를 실행할 때, `restaurant`, `review`, `profile` 중 하나를 선택하여야합니다. 각각 레스토랑의 정보, 레스토랑의 리뷰, 사용자 프로필 정보를 수집합니다. 
  * restaurant 옵션은 개발 중이기 때문에, 선택시 안내 문구와 함께 프로그램이 종료됩니다.
* 선택 옵션 중, On/Off에 해당하는 옵션들을 bool 형식으로 변경됩니다.
* `dataset_name` 옵션 이름이 `target_list_name`으로 변경됩니다.
* 성공적으로 작업을 모두 완료 후, 프로그램을 종료하기 전, 총 소요시간이 표시됩니다.

### 버그 수정
* 로그 파일에 유니코드 문자가 저장되지 않던 문제가 수정됩니다.

Ver 1.0.2
### 기능 추가
* `save_logfile` 명령어로 로그를 저장할 수 있습니다. `logs`라는 폴더가 사전에 있어야 하며, 그 폴더에 로그 파일이 저장됩니다.

### 수정
* 작업이 끝난 후, 리뷰가 존재하지 않아서 수집하지 못한 식당이 따로 표기됩니다.
* 오류가 발생했을 시, traceback이 자세히 표시됩니다.
* 리뷰 마지막 페이지가 URL로 직접 접속이 되지 않는 경우, 그 페이지는 생략되도록 수정됩니다.
* 작업 진행 로그 메시지가 간결하게 변경됩니다.

### 버그 수정
* `chrome-open` 명령어가 작동하지 않는 버그가 수정됩니다.

Ver 1.0.1
### 기능 추가
* 리뷰를 수집할 식당의 인덱스 값들을 직접 입력할 수 있는 Index Specified Mode가 추가되었습니다.

### 수정
* 파일을 저장할 때, 파일 이름에 리뷰 수집 중 오류가 발생하여 수집하지 못한 식당의 개수가 표시되도록 하였습니다.
* Command Line Arguements 중, `start_index`와 `end_index`의 이름을 각각 `min_index`와 `max_index`로 변경하였습니다.

### 버그 수정
* 리뷰에 등록된 사진 개수가 잘못 수집되는 버그를 수정하였습니다.
