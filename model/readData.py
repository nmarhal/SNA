"""
reads data from the csv files and puts it in required data structures
"""
import pandas as pd

def get_all_data()-> pd.DataFrame:
    book1 = pd.read_csv('Dataset/book1.csv')
    book2 = pd.read_csv('Dataset/book2.csv')
    book3 = pd.read_csv('Dataset/book3.csv')
    book4 = pd.read_csv('Dataset/book4.csv')
    book5 = pd.read_csv('Dataset/book5.csv')
    result = [book1, book2, book3, book4, book5]
    result = pd.concat(result, ignore_index=True)
    return result

def get_book_1()->pd.DataFrame:
    return pd.read_csv('Dataset/book1.csv')

def get_book_2()->pd.DataFrame:
    return pd.read_csv('Dataset/book2.csv')

def get_book_3()->pd.DataFrame:
    return pd.read_csv('Dataset/book3.csv')

def get_book_4()->pd.DataFrame:
    return pd.read_csv('Dataset/book4.csv')

def get_book_5()->pd.DataFrame:
    return pd.read_csv('Dataset/book5.csv')