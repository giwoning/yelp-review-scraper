# Yelp Review Scraper

이 코드는 Yelp 사이트에서 제공하는 리뷰를 수집합니다. 수집하고자하는 Yelp에 등록된 식당의 **Yelp ID가 담겨있는 파일** (이하 식당 리스트 파일)만 준비하면 됩니다.

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

## How it works?
이 코드는 Python 3으로 작성되었으며, Selenium을 이용한 웹 크롤링을 수행합니다. 사용자는 반드시 식당 리스트 파일을 사전에 준비하여야 합니다. 시작 인덱스에 대응하는 식당부터 끝 인덱스에 대응하는 식당까지 순서대로, 각 식당에 등록되어 있는 리뷰들을 수집합니다. Yelp에서는 다중 언어의 리뷰를 볼 수 있으나, 이 프로그램은 _영어 리뷰만 수집합니다_.

Yelp에서는 한 페이지당 10개의 리뷰를 볼 수 있습니다. 10개보다 많은 리뷰가 등록된 식당은 여러개의 리뷰 페이지가 있습니다. 만약 페이지 순서대로 리뷰를 수집하게 되면, 매우 높은 확률로 Yelp에서 자동으로 임시 IP 밴을 합니다. 따라서 해당 프로그램은 리뷰 페이지를 임의의 순서대로 방문하도록 코드가 작성되었습니다.

어떤 식당의 리뷰 수집 중 오류가 발생하면, 그때까지 수집하였던 리뷰 정보는 저장하지 않고 다음 식당으로 넘어갑니다. 모든 식당의 리뷰를 수집이 완료가 되면, _성공적으로 리뷰를 수집한 식당 개수_ 와 _리뷰 수집에 실패한 식당 개수 및 그 식당들의 인덱스들_ 을 보고한 뒤, csv 파일로 저장하며 프로그램을 종료합니다.

### More Detail...
프로그램이 실행되면, 우선 Command Line Arguments 들이 올바르게 입력되었는지 확인합니다. 그 후, 필요한 파일이 존재하는 지 확인합니다. 만약 이 단계에서 문제가 발생하면 프로그램은 즉시 종료됩니다.

그 다음으로 Chrome 드라이버를 불러옵니다. 최초 실행시, Chrome 드라이버가 자동으로 다운로드 됩니다. 그 다음, 식당 리스트 파일을 불러오고, 이 리스트 파일에 담긴 식당 개수를 바탕으로 끝 인덱스 값이 제대로 설정되었는지 확인합니다. 만약 끝 인덱스 값이 `전체 식당 개수 - 1`보다 크다면, 끝 인덱스 값을 마지막 인덱스 값으로 변경합니다.

이제 본격적으로 크롤링을 수행합니다. 주어진 Yelp ID에 해당하는 페이지에 접속하고, `wait_time_for_new_index`초 만큼 대기합니다. 그 다음 Yelp 상에 등록된 식당 이름을 불러옵니다 (이때 최대 `wait_time_for_establishment`초만큼 불러와질 때 까지 대기합니다). 그 다음으로, 리뷰 페이지가 얼마나 있는지 찾습니다. 페이지가 정상적으로 불러와졌다면, '1 of x pages' 라는 문구를 페이지 하단에 있습니다. 'x'가 전체 리뷰 페이지 개수입니다. 리뷰 페이지를 순서대로 방문하면 자동 임시 IP밴에 걸리기 때문에, random 패키지의 sample 함수를 이용하여, 방문할 리뷰 페이지를 임의로 결정합니다.

이제 방문할 리뷰 페이지 순서가 결정되었으므로, 그 순서대로 리뷰를 수집합니다. 한 리뷰 페이지에는 최대 10개의 리뷰가 존재합니다. 하나의 리뷰에 **작성자 ID**, **사진과 ROTD 여부**, **유익함**이 기준이 되어(절대경로) 각 리뷰의 나머지 구성요소들(상대경로)을 수집합니다.

식당 관계자의 답글과 작성자가 담긴 과거 리뷰는 약간 독특한 구조를 가집니다. 만약 과거 리뷰들이 2개 이상일 경우, 식당 관계자의 답글과 작성자의 과거 리뷰 하나가 하나의 묶음으로, 나머지 과거 리뷰들이 또 다른 묶음으로 되어있습니다. 과거 리뷰들의 경우, 내용은 수집하지 않고 리뷰에 담긴 평점과 유익함들의 평균을 수집합니다.

한 페이지에 있는 모든 리뷰들이 성공적으로 수집되면, 다음 리뷰 페이지로 넘어가서 `wait_time_for_next_page`초 만큼 대기 후 같은 작업을 반복합니다. 한 식당에서 모든 리뷰 페이지에 있는 리뷰들이 수집이 완료되면, 이 리뷰들을 식당 인덱스가 Key이고, 리뷰들이 Value인 reviews라는 이름의 Dictionary에 저장합니다.

모든 식당들의 리뷰가 수집될 경우, Dictionary를 pandas의 Dataframe으로 변경하고, 이를 다시 csv 파일로 저장합니다. 그 이후 프로그램을 종료합니다.

## Restaurant List File
이 프로그램이 수집할 식당들의 이름과 Yelp ID를 담은 파일입니다. `.csv` 파일로 아래와 같은 형식으로 되어있어야합니다. Yelp ID가 담긴 열의 첫 행은 반드시 `yelp_id`로 설정해야합니다.
| yelp_id |
| ----- |
| benemon-new-york |
| bxl-cafe-new-york-2 |
| locanda-verde-new-york |
| zoralie-restaurant-new-york |
| porteno-restaurant-new-york |
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
만약 AWS EC2와 S3를 사용한다면, 코드 실행시 `--aws_mode=1` 인자를 포함시켜 AWS 모드를 활성화할 수 있습니다. `aws_key.ini` 파일에서 개인의 AWS 서비스에 접근하기 위한 4가지의 정보를 입력해야합니다. 위 값들은 모두 작은 따옴표(')로 둘러싸야합니다.
| Value | Description |
| ----- | ----- |
| aws_access_key | AWS 서비스에 접근하기 위한 아이디입니다. |
| aws_secret_key | AWS 서비스에 접근하기 위한 비밀번호입니다. |
| aws_region | AWS 서비스를 사용하는 지역 코드입니다. |
| aws_bucket_name | AWS S3에서 사용자가 설정한 Bucket 이름입니다. |

## Command Line Arguments
코드 실행 시 아래와 같은 옵션을 설정할 수 있습니다.

### Scraper Options
| Argument | Type | Description | Default |
| ----- | ----- | ----- | ----- |
| `--start_index` | int | 시작 인덱스 값입니다. 끝 인덱스 값보다 작거나 같아야 하고, `전체 식당 개수 - 1`보다 클 수 없습니다.| 0 |
| `--end_index` | int | 끝 인덱스 값입니다. 시작 인덱스 값보다는 크거나 같고, `전체 식당 개수 - 1`보다 작아야 합니다. -1로 설정하면, 마지막 인덱스로 설정됩니다.| -1 |
| `--wait_time_for_new_index` | int | 한 식당에서 다른 식당으로 넘어갈 때 대기 시간(초)입니다. | 10 |
| `--wait_time_for_establishment` | int | 식당의 Yelp 상에 등록된 이름을 성공적으로 불러올 때 까지의 대기 시간(초)입니다. | 10 |
| `--wait_time_for_next_page` | int | 식당의 한 리뷰 페이지에서 다음 리뷰 페이지로 넘어갈 때 대기 시간(초)입니다. | 10 |

세 대기 시간 값은 리뷰 수집 속도와 수집 실패 빈도 사이에서 적절히 조절해야 합니다. 너무 짧게 설정하면, 페이지가 모두 로드되기 전에 수집을 시도하기 때문에 오류가 발생하게 됩니다. 반면, 너무 길게 설정하면 리뷰 수집 시간이 지나치게 길어질 수 있습니다.

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
| `--open_chrome` | boolean | 1이면 크롬 창을 띄워 리뷰를 수집 중인 식당 웹페이지를 실시간으로 볼 수 있습니다. Windows가 아닌 환경에서는 항상 0으로 강제 설정됩니다. | 0 |

### Save Options
| Argument | Type | Description | Default |
| ----- | ----- | ----- | ----- |
| `--index_suffix` | boolean | 결과 파일을 저장할 때, 파일명 뒤에 시작 인덱스 값과 끝 인덱스 값을 붙입니다. (yelp_review_**from_0_to_100**.csv) | 1 |

## Keys for Scraping
Yelp HTML의 class 이름은 직관적이지 않고, 때때로 바뀌는 경우가 있습니다. 만약 모든 식당의 리뷰가 정상적으로 수집되지 않는다면, class 이름이 변경되었는지 확인하여야합니다. 리뷰 수집에 필요한 class 이름들은 `keys_for_scraping.ini`에 모두 기록되어 있습니다. 모든 값들은 작은 따옴표(')로 둘러싸야 합니다.
