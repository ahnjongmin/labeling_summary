import os
import pandas as pd
import re
from csv import DictWriter
import random

data_loc = os.getcwd() + "/../coupang/"
now_loc = os.getcwd() + "/../"


def select_n_reviews(file_loc, rev_num=10):
    file_exist = os.path.exists(file_loc)
    if not file_exist:
        print("Error: There is no file in {}".format(file_loc))
    raw_reviews = pd.read_csv(file_loc)
    sampled_reviews = raw_reviews.sample(rev_num)

    product_id = str(sampled_reviews.product_id.tolist()[0])
    product_name = sampled_reviews.product_name.tolist()[0]

    review_list = []
    for _, row in sampled_reviews.iterrows():
        try:
            single_review = row.review_title + " " + row.review_text
        except TypeError:
            single_review = row.review_text
        single_review = single_review.replace("\n", " ")
        single_review = re.sub(r"\s+", " ", single_review)
        review_list.append(single_review)

    return {"product_id":product_id, "product_name":product_name, "review":review_list}


def save_review_with_summary(field_dict):
    file_exist = os.path.exists(now_loc + "summary.csv")
    fieldnames = ['product_id', 'product_name', 'review', 'summary']

    with open('{}summary.csv'.format(now_loc), 'a', newline='', encoding="utf-8-sig") as f_object:
        dictwriter_object = DictWriter(f_object, fieldnames=fieldnames)
        if file_exist:
            exist_reviews = pd.read_csv(now_loc + "summary.csv")
            exist_reviews_id = exist_reviews.product_id.tolist()
            if field_dict['product_id'] in exist_reviews_id:
                print("Warning: There is an existing review summary")
                return
            else:
                dictwriter_object.writerow(field_dict)
                return                
        else:
            dictwriter_object.writeheader()
            dictwriter_object.writerow(field_dict)
            return
            

def save_single_review_totally(loc):
    dict = select_n_reviews(loc)
    print(dict['product_name'])
    for i in dict['review']:
        print(i)
    
    summary = input("Summary :: ")
    dict['summary'] = summary

    save_review_with_summary(dict)


def main1():
    target_category = [225491,225504,432568,432669,432672,432740,432765,446032,446035,446038,486687]
    cat_choice = random.choice(target_category)
    cat_loc = data_loc + str(cat_choice) + "/"

    tt = pd.read_csv(cat_loc + str(cat_choice) + ".csv")
    tt = tt.product_id.tolist()
    
    product_choice = random.choice(tt)
    product_loc = cat_loc + "reviews/" + str(product_choice) + ".csv"

    print(product_loc)
    save_single_review_totally(product_loc)


def main():
    target_category = [225491,225504,432568,432669,432672,432740,432765,446032,446035,446038,486687]
    cat_choice = random.choice(target_category)
    cat_loc = data_loc + str(cat_choice) + "/"

    tt = pd.read_csv(cat_loc + str(cat_choice) + ".csv")
    tt = tt.product_id.tolist()
    
    product_choice = random.choice(tt)
    product_loc = cat_loc + "reviews/" + str(product_choice) + ".csv"

    print(product_loc)
    save_single_review_totally(product_loc)


if __name__ == "__main__":
    while 1:
        main()