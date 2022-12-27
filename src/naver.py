import os
import pandas as pd
import re
from csv import DictWriter
import random
from kiwipiepy import Kiwi

kiwi = Kiwi()
data_loc = os.getcwd() + "/../naver/"
now_loc = os.getcwd() + "/../"
BAD_NUM = 2
GOOD_NUM = 8
MIN_LEN = 10

def include_all_tag(text):

    try:
        if "(맛)" in text:
            return True
        else:
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

# def extract_taste_area_in_review(text, area_text):
#     split_text = kiwi.split_into_sents(text)
#     split_text = [i.text for i in split_text]
    
#     split_area_text = area_text.split("\n")
#     split_area_text = [i for i in split_area_text if "(맛)" in i]
#     split_area_text = [i.replace("(맛)", "") for i in split_area_text]
#     print(split_text)
#     print(split_area_text)
#     aalist = []
#     ret_str = ""
#     for idx, i in enumerate(split_text):
#         for j in split_area_text:
#             if j in i:
#                 aalist.append(idx)
#     aalist = set(aalist)
#     for i in aalist:
#         ret_str += split_text[i]
    
#     return ret_str


def extract_taste_area_in_review(row):
    text = row['review_text']
    area_text = row['review_topics']
    text = text.replace("\n", " ")
    split_text = kiwi.split_into_sents(text)
    split_text = [i.text for i in split_text]
    
    split_area_text = area_text.split("\n")
    split_area_text = [i for i in split_area_text if "(맛)" in i]
    split_area_text = [i.replace("(맛)", "") for i in split_area_text]
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
    row['review_text'] = ret_str

    return row

def extract_amount_of_reviews_for_save(df, num):
    
    reviews_dict_list = []
    order = 0
    left_num = num
    print("Selected Product: {}".format(df.loc[0]['product_name']))
    while left_num != 0:
        df_sample = df.loc[order: order+left_num-1]
        df_sample = df_sample.apply(extract_taste_area_in_review, axis=1)
        print("________Select to waste in this reviews________, left: {}".format(left_num))
        for idx, row in df_sample.iterrows():
            print(idx, row.review_text)
        
        a = input()
        if a != "":
            num_to_waste = a.strip().split(" ")
            num_to_waste = [int(i) for i in num_to_waste]
        else:
            num_to_waste = []
        
        dropped_df_sample = df_sample.drop(num_to_waste)
        for _, row in dropped_df_sample.iterrows():
            reviews_dict_list.append({'product_id': df.loc[0]['product_id'], "product_name": df.loc[0]['product_name'], "review_help_cnt":row.review_help_cnt, "review_text":row.review_text})
        order += left_num
        left_num -= left_num - len(num_to_waste)

    return reviews_dict_list


def make_summary_in_single_review(location, big_cat, small_cat, product_id):
    print("This is in {}/{}/{}".format(big_cat, small_cat, product_id))
    df = pd.read_csv(location)

    df= df.sort_values('review_help_cnt', ascending=False)


    a = []
    df = df[df['review_topics'].apply(lambda text: include_all_tag(text))]
    df_good = df[df['review_user_grade'].apply(lambda grade: seperate_review(grade, True))].reset_index()
    df_bad = df[df['review_user_grade'].apply(lambda grade: seperate_review(grade, False))].reset_index()
    
    a += extract_amount_of_reviews_for_save(df_good, GOOD_NUM)
    a += extract_amount_of_reviews_for_save(df_bad, BAD_NUM)

    reviews = []
    print("______당신이 선택한 리뷰 10개입니다______")
    for idx, i in enumerate(a):
        print(idx, ",", i['review_text'])
        reviews.append(i['review_text'])
    summary = input("요약해주세요: ")
    print("")
    dict_to_save = {"big_cat": big_cat, "small_cat": small_cat, "product_id": product_id, "product_name": a[0]['product_name'], "review_text": reviews, "review_summary": summary}

    file_exist = os.path.exists(now_loc + "naver_summary.csv")
    fieldnames = ["big_cat", "small_cat", "product_id", "product_name", "review_text", "review_summary"]

    with open('{}naver_summary.csv'.format(now_loc), 'a', newline='', encoding="utf-8-sig") as f_object:
        dictwriter_object = DictWriter(f_object, fieldnames=fieldnames)
        if file_exist:
            exist_reviews = pd.read_csv(now_loc + "naver_summary.csv")
            exist_reviews_id = exist_reviews.product_id.tolist()
            if dict_to_save['product_id'] in exist_reviews_id:
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
    cat_choice = "bakery"
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
    product_name = cat_choice

    exist = pd.read_csv(now_loc + "/naver_summary.csv")
    exist = exist['product_id'].tolist()
    if product_name in exist:
        print("exist")
        return
    else:
        make_summary_in_single_review(fileloc, big_cat, small_cat, product_name)


if __name__ == "__main__":
    while 1:
        main()
#     extract_taste_area_in_review("두개 먹어봤는데요 진짜 맛있어요",  """(맛)두개 먹어봤는데요
# (만족도)맛은 그저 그냥 그래요
# (만족도)가격대비 좋은지 모르겠구요
# (가격)가격대비 좋은지 모르겠구요
# """)