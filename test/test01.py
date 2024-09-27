import json
import urllib.parse
from datetime import datetime
from sys import executable

import pandas as pd
import requests
from bs4 import BeautifulSoup
import re

from selenium import webdriver
from selenium.webdriver.common.by import By
import subprocess
import undetected_chromedriver as uc

if __name__ == '__main__':
    browser = uc.Chrome(headless=False, use_subprocess=False)

    # url = "https://chatgpt.com/g/g-23B7QDQzF-ai-coupon-code-finder-smart-shopping-companion"
    url = "https://chatgpt.com/g/g-GbLbctpPz-universal-primer"
    
    browser.get(url)

    # class (btn relative btn-primary btn-giant) click
    browser.find_element(By.CLASS_NAME, "btn.relative.btn-primary.btn-giant").click()
    browser.find_element(By.CLASS_NAME, "social-btn").click()
    print("test")