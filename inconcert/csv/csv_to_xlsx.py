import time, openpyxl, datetime, urllib
from selenium import webdriver
import selenium.webdriver.support.ui as ui
try: 
    from openpyxl.cell import get_column_letter
except ImportError:
    from openpyxl.utils import get_column_letter

import pyexcel
from pyexcel.cookbook import merge_all_to_a_book
# import pyexcel.ext.xlsx # no longer required if you use pyexcel >= 0.2.2 
import glob


merge_all_to_a_book(glob.glob("events.csv"), "events.xlsx")

