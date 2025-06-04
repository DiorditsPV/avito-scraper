#!/usr/bin/env python3

import sys
sys.path.append('.')

from avito_subscriber.client.selenium.selenium import SeleniumParser
from selenium.webdriver.common.by import By

def test_selenium():
    """Простой тест SeleniumParser"""
    
    # Тест удаленного Selenium
    with SeleniumParser(remote_selenium_url="http://localhost:4444") as parser:
        parser.go_to_page("https://httpbin.org/html")
        element = parser.wait_for_element(By.TAG_NAME, "h1")
        assert element.text == "Herman Melville - Moby-Dick"
        print("Удаленный Selenium работает")
    
    # Тест локального Selenium
    try:
        with SeleniumParser() as parser:
            parser.go_to_page("https://httpbin.org/status/200")
            print("Локальный Selenium работает")
    except Exception as e:
        print(f"Локальный Selenium недоступен: {e}")

if __name__ == "__main__":
    test_selenium()
    print("Тесты завершены") 