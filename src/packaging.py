import os
import pandas as pd
import re
from csv import DictWriter
import random
from kiwipiepy import Kiwi
import time

now_loc = os.getcwd() + "/../"

def main():
    list = []
    for i in range(10):
        a = input(str(i)+", ")
        list.append(a)
    return list

def t():
    product_name = input("프로덕트 이름: ")
    list = main()
    print("_______________________")
    for idx, i in enumerate(list):
        print(idx, ",", i)

    summary = input("요약해주세요: ")

    dict_to_save = {"product_name":product_name, "review_summary":summary, "review_text": list}

    fieldnames = ["product_name", "review_text", "review_summary"]
    file_exist = os.path.exists(now_loc + "packaging_summary.csv")


    with open('{}packaging_summary.csv'.format(now_loc), 'a', newline='', encoding="utf-8-sig") as f_object:
        dictwriter_object = DictWriter(f_object, fieldnames=fieldnames)
        if file_exist:

            dictwriter_object.writerow(dict_to_save)            
        else:
            dictwriter_object.writeheader()
            dictwriter_object.writerow(dict_to_save)
if __name__ == "__main__":
    while 1:
        t()