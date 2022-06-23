import os
import time
import datetime
import pandas as pd

from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def set_driver():
    '''
    Chromeを自動操作するためのChromeDriverを起動してobjectを取得する
    '''
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
    options = ChromeOptions()

    # 起動オプションの設定
    options.add_argument(f'--user-agent={USER_AGENT}') # ブラウザの種類を特定するための文字列
    options.add_argument('log-level=3') # 不要なログを非表示にする
    options.add_argument('--ignore-certificate-errors') # 不要なログを非表示にする
    options.add_argument('--ignore-ssl-errors') # 不要なログを非表示にする
    options.add_experimental_option('excludeSwitches', ['enable-logging']) # 不要なログを非表示にする
    options.add_argument('--incognito') # シークレットモードの設定を付与
    
    # ChromeのWebDriverオブジェクトを作成する。
    service=Service(ChromeDriverManager().install())
    return Chrome(service=service, options=options)

url = "https://www.amazon.co.jp/dp/{asin}"

def item_search(asin):
    driver = set_driver()
    try:
        driver.get(url.format(asin=asin))
        name = driver.find_element(by=By.CSS_SELECTOR, value=".product-title-word-break").text
        try:
            image_url = driver.find_element(by=By.ID, value="landingImage").get_attribute("src")
        except:
            iamge_block = driver.find_element(by=By.CSS_SELECTOR, value=".itemNo0")
            image_url = iamge_block.find_element(by=By.CSS_SELECTOR, value=".a-dynamic-image").get_attribute("src")
        price = ""
        prime = ""
        try:
            review_count = driver.find_element(by=By.CSS_SELECTOR, value="#reviewsMedley > div > div.a-fixed-left-grid-col.a-col-left > div.a-section.a-spacing-none.a-spacing-top-mini.cr-widget-ACR > div.a-row.a-spacing-medium.averageStarRatingNumerical > span").text.rstrip("件のグローバル評価")
            review = driver.find_element(by=By.XPATH, value='//span[@data-hook="rating-out-of-text"]').text.replace("星5つ中の","")   
        except:
            review_count = 0
            review = ""
        try:
            new_item_box = driver.find_element(by=By.ID, value="newAccordionRow")
        except:
            new_item_box = ""
        small_ctgry = []
        try:
            detail_tbl = driver.find_element(by=By.ID, value="productDetails_detailBullets_sections1")
            for tr in detail_tbl.find_elements(by=By.TAG_NAME, value="tr"):
                if "売れ筋ランキング" in tr.find_element(by=By.TAG_NAME, value="th").text:
                    td = tr.find_element(by=By.TAG_NAME, value="td")
                    td_elems = td.find_elements(by=By.TAG_NAME, value="a")
                    for td_elem in td_elems:
                        small_ctgry.append(td_elem.text)
                else:
                    pass
        except:
            pass
        
        # 公式でない場合    
        if new_item_box == "":
            a_box = driver.find_element(by=By.ID, value="addToCart")
            rows = a_box.find_elements(by=By.CSS_SELECTOR, value=".tabular-buybox-text")
            for row in rows:
                # ボックス内でプライム対象商品があった場合
                if row.get_attribute("tabular-attribute-name") == "出荷元" and (row.text == "Amazon" or row.text == "Amazon.co.jp"):
                    prime = "prime"
                    # 黒字の値段
                    try:
                        price = a_box.find_element(by=By.CSS_SELECTOR, value=".a-price-whole").text
                    # 赤字の値段
                    except:
                        price = driver.find_element(by=By.CSS_SELECTOR, value="#corePrice_feature_div > div > span.a-price.a-text-price.a-size-medium > span:nth-child(2)").text.lstrip("￥")
            # なかった場合は、新品＆中古品のリストまで見る。
            if prime == "":
                try:
                    driver.find_element(by=By.CSS_SELECTOR, value="#olpLinkWidget_feature_div > div.a-section.olp-link-widget > span > a > div > div").click()
                    time.sleep(3)
                    driver.find_element(by=By.ID, value="aod-filter-string").click()
                    aod_parent_filter = driver.find_elements(by=By.CSS_SELECTOR, value=".aod-filter-parent-filter")
                    for aod_filter in aod_parent_filter:
                        try:
                            label = aod_filter.find_element(by=By.CSS_SELECTOR, value=".a-icon-prime-jp")
                            aod_filter.find_element(by=By.CSS_SELECTOR, value=".a-icon-checkbox").click()                
                        except:
                            label = aod_filter.find_element(by=By.CSS_SELECTOR, value=".a-size-base")
                            if label.text=="新品":
                                aod_filter.find_element(by=By.CSS_SELECTOR, value=".a-icon-checkbox").click()
                    time.sleep(2)
                    # 絞り込んだ条件でプライム商品があれば値段を取得
                    prime = "prime"
                    information_block = driver.find_elements(by=By.CSS_SELECTOR, value=".aod-information-block")
                    price = information_block[1].find_element(by=By.CSS_SELECTOR, value=".a-price-whole").text                       
                except:
                    pass                   
        # 公式販売ページの場合
        else:
            rows = new_item_box.find_elements(by=By.TAG_NAME, value="span")
            for row in rows:
                if row.text == "Amazon" or row.text == "Amazon.co.jp":
                    price = new_item_box.find_elements(by=By.TAG_NAME, value="span")[1].text.lstrip("￥")
                    prime = "prime"
            if prime == "":
                try:
                    driver.find_element(by=By.CSS_SELECTOR, value="#olpLinkWidget_feature_div > div.a-section.olp-link-widget > span > a > div > div").click()
                    time.sleep(3)
                    driver.find_element(by=By.ID, value="aod-filter-string").click()
                    aod_parent_filter = driver.find_elements(by=By.CSS_SELECTOR, value=".aod-filter-parent-filter")
                    for aod_filter in aod_parent_filter:
                        try:
                            label = aod_filter.find_element(by=By.CSS_SELECTOR, value=".a-icon-prime-jp")
                            aod_filter.find_element(by=By.CSS_SELECTOR, value=".a-icon-checkbox").click()                
                        except:
                            label = aod_filter.find_element(by=By.CSS_SELECTOR, value=".a-size-base")
                            if label.text=="新品":
                                aod_filter.find_element(by=By.CSS_SELECTOR, value=".a-icon-checkbox").click()
                    time.sleep(2)
                    # 絞り込んだ条件でプライム商品があれば値段を取得
                    information_block = driver.find_elements(by=By.CSS_SELECTOR, value=".aod-information-block")
                    price = information_block[1].find_element(by=By.CSS_SELECTOR, value=".a-price-whole").text   
                    prime = "prime"                    
                except:
                    pass             
    
    except:
        name = ""
        price = ""
        prime = ""
        review_count = ""
        review = ""
        image_url = ""
        small_ctgry = ""
                        
    dict = {
        "ASIN": asin,
        "商品名": name,
        "URL": url.format(asin=asin),
        "最低価格": price,
        "prime": prime,
        "評価件数": review_count,
        "評価": review,
        "画像URL": image_url,
        "カテゴリー＆ランキング":small_ctgry
    }
    
    return dict

def ctgry_search(ctgry_url, price_range):
    driver = set_driver()
    driver.get(ctgry_url)
    time.sleep(3)
    driver.find_element(by=By.CSS_SELECTOR, value=".a-icon-checkbox").click()
    time.sleep(3)
    driver.find_element(by=By.CSS_SELECTOR, value=".a-star-medium-4").click()
    time.sleep(3)
    cur_url = driver.current_url
    driver.get(cur_url+price_range)
    time.sleep(5)
    
    try:
        main_area = driver.find_element(by=By.CSS_SELECTOR, value=".s-main-slot")
        item_list = main_area.find_elements(by=By.CSS_SELECTOR, value=".s-result-item")
        for item in item_list[1:]:
            data_asin = item.get_attribute("data-asin")
            return data_asin
    except:
        data_asin = ""
        return data_asin
