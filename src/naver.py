import os
import pandas as pd
import re
from csv import DictWriter
import random
from kiwipiepy import Kiwi
import time

kiwi = Kiwi()
data_loc = os.getcwd() + "/../naver/"
now_loc = os.getcwd() + "/../"
BAD_NUM = 2
GOOD_NUM = 8
MIN_LEN = 10
PRICE = ["가격", "음식량", "용량", "사이즈"]
PACKAGE = ["포장", "제품구성"]
FLAVOR = ["맛", "식감", "향기"]
ASPECT = PACKAGE

def include_more_than_one(text):

    try:
        for aspect in ASPECT:
            if "({})".format(aspect) in text:
                return True
        return False
    except TypeError:
        return False

def is_over_min_len(text):

    if len(text >= 10):
        return True
    else:
        return False

def seperate_review(grade, is_good):

    if is_good == True:
        try:
            if grade >= 4:
                return True
            else:
                return False
        except TypeError:
            return False
    else:
        try:
            if grade >= 4:
                return False
            else:
                return True
        except TypeError:
            return False


def is_aspect_there(text):
    for i in ASPECT:
        if "({})".format(i) in text:
            return True
    return False

def replace_aspects_to_blank(text):
    for aspect in ASPECT:
        text = text.replace("({})".format(aspect), "")
    return text

def extract_taste_area_in_review(row):
    text = row['cleanContent']  # 실제 문장
    area_text = row['topicSpans'] # 특정 문장이 있는 곳 ex: (맛) 두부 맛있는 두부 (사이즈)뭐시기
    text = text.replace("\n", " ")
    split_text = kiwi.split_into_sents(text)
    split_text = [i.text for i in split_text]
    
    split_area_text = area_text.split("\n")
    split_area_text = [i for i in split_area_text if is_aspect_there(i)==True]
    split_area_text = [replace_aspects_to_blank(i) for i in split_area_text]
    split_area_text = [i for i in split_area_text if i != ""]
    #print(split_text)
    #print(split_area_text)

    aalist = []
    ret_str = ""
    for idx, i in enumerate(split_text):
        for j in split_area_text:
            if j in i:
                aalist.append(idx)
    aalist = set(aalist)
    for i in aalist:
        ret_str += split_text[i]
        ret_str += " "
    row['cleanContent'] = ret_str

    return row

def extract_amount_of_reviews_for_save(df, num, matchNvMid):
    
    reviews_dict_list = []
    order = 0
    left_num = num
    #print("Selected Product: {}".format(matchNvMid, "||", df.loc[0]['nvMid']))
    print("Selected Product: {}".format(matchNvMid))
    while left_num != 0:
        df_sample = df.loc[order: order+left_num-1]
        df_sample = df_sample.apply(extract_taste_area_in_review, axis=1)
        flag_good_input = False
        while flag_good_input == False:
            try:
                print("________Select to waste in this reviews________, left: {}".format(left_num))
                for idx, row in df_sample.iterrows():
                    print(idx, row.cleanContent)
                
                a = input()
                if a == "!!!":
                    with open(now_loc + "/trash.txt", "a") as f:
                        f.write(matchNvMid + '\n')
                        print("This number has been trashed")
                        raise ImportError
                elif "다" in a:
                    num_to_waste = df_sample.index.tolist()
                elif a != "":
                    num_to_waste = a.strip().split(" ")
                    num_to_waste = list(set([int(i) for i in num_to_waste]))
                else:
                    num_to_waste = []
                
                dropped_df_sample = df_sample.drop(num_to_waste)
                for _, row in dropped_df_sample.iterrows():
                    reviews_dict_list.append({'matchNvMid': df.loc[0]['matchNvMid'], "nvMid": df.loc[0]['nvMid'], "qualityScore":row.qualityScore, "cleanContent":row.cleanContent})
                order += left_num
                left_num -= left_num - len(num_to_waste)
                flag_good_input = True
            except KeyboardInterrupt:
                print("KeyboardInterrupted")
                exit(0)
            except ImportError:
                exit(0)
            except:
                print("-----------------------------------------------------")
                print("I think you put wrong num. Check format one more time")
                print("-----------------------------------------------------")
                time.sleep(0.3)

    return reviews_dict_list


def make_summary_in_single_review(location, big_cat, small_cat, matchNvMid):
    print("This is in {}/{}/{}".format(big_cat, small_cat, matchNvMid))
    df = pd.read_csv(location)

    df= df.sort_values('qualityScore', ascending=False)

    df = df.drop_duplicates("cleanContent")

    a = []

    #print(df['topicSpans'])
    print("____________________")
    df = df[df['topicSpans'].apply(lambda text: include_more_than_one(text))]
    #print(df['topicSpans'])
    if len(df) == 0:
        print("no pozang @@@@@@@@@@")
        return
    df_good = df[df['starScore'].apply(lambda grade: seperate_review(grade, True))].reset_index()
    df_bad = df[df['starScore'].apply(lambda grade: seperate_review(grade, False))].reset_index()
    df = df.reset_index()
    #a += extract_amount_of_reviews_for_save(df_good, GOOD_NUM, matchNvMid)
    #a += extract_amount_of_reviews_for_save(df_bad, BAD_NUM, matchNvMid)
    if len(df) < 10:
        print("not enough: {}".format(len(df)))
        return
    a += extract_amount_of_reviews_for_save(df, 10, matchNvMid)
    

    reviews = []

    print("______당신이 선택한 리뷰 10개입니다______")
    for idx, i in enumerate(a):
        print(idx, ",", i['cleanContent'])
        reviews.append(i['cleanContent'])
    summary = input("요약해주세요: ")
    print("")
    dict_to_save = {"big_cat": big_cat, "small_cat": small_cat, "matchNvMid": matchNvMid, "nvMid": a[0]['nvMid'], "cleanContent": reviews, "review_summary": summary}

    file_exist = os.path.exists(now_loc + "naver_new_summary.csv")
    fieldnames = ["big_cat", "small_cat", "matchNvMid", "nvMid", "cleanContent", "review_summary"]

    with open('{}naver_new_summary.csv'.format(now_loc), 'a', newline='', encoding="utf-8-sig") as f_object:
        dictwriter_object = DictWriter(f_object, fieldnames=fieldnames)
        if file_exist:
            exist_reviews = pd.read_csv(now_loc + "naver_new_summary.csv")
            exist_reviews_id = exist_reviews.matchNvMid.tolist()
            if dict_to_save['matchNvMid'] in exist_reviews_id:
                print("Warning: There is an existing review summary")
            else:
                dictwriter_object.writerow(dict_to_save)            
        else:
            dictwriter_object.writeheader()
            dictwriter_object.writerow(dict_to_save)

    print("save done\n______________________________________________________________\n")
        
def main():
    filenames = os.listdir(data_loc)
    #cat_choice = random.choice(filenames)
    cat_choice = "gjsnew"
    fileloc = data_loc + cat_choice + "/"
    big_cat = cat_choice

    smallcatnames = os.listdir(fileloc)
    #cat_choice = random.choice(smallcatnames)
    cat_choice = "total"
    fileloc += cat_choice + '/'
    small_cat = cat_choice

    productnames = os.listdir(fileloc)
    cat_choice = random.choice(productnames)
    fileloc += cat_choice
    matchNvMid = cat_choice

    exist = pd.read_csv(now_loc + "naver_new_summary.csv")
    exist = exist['matchNvMid'].tolist()

    try:
        with open(now_loc + "trash.txt") as f:
            trashed = f.readlines()
        trashed = [line.rstrip('\n') for line in trashed]
    except FileNotFoundError:
        trashed = []
    
    if matchNvMid in exist:
        print("exist")
        return
    elif matchNvMid in trashed:
        print("trashed")
        return
    else:
        make_summary_in_single_review(fileloc, big_cat, small_cat, matchNvMid)


if __name__ == "__main__":
    while 1:
        main()