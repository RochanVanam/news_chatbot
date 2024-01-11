from flask import Flask, render_template, request
from transformers import pipeline
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from urllib.parse import quote
import torch
import requests
import tkinter as tk
import time
import re

class FinancialChatbot:
    def __init__(self):
        self.summarizer = pipeline('summarization', model="google/pegasus-xsum")

    def __get_article_content(self, url):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        time.sleep(2)

        try:
            html = driver.page_source
            driver.quit()
            soup = BeautifulSoup(html, 'html.parser')
            article_content = ""

            print("Searching for article content")

            paragraphs = soup\
                .find("div", class_="article__content")\
                .find_all("p", recursive=False)
            
            article_content += ' '.join([paragraph.text for paragraph in paragraphs])
            print("Content found")

            return article_content
        
        except Exception as e:
            print(f"Error: {e}")
        return ""
    
    def __get_search_urls(self, soup, pages):
        results = soup\
            .find("div", class_="container__field-links container_list-images-with-description__field-links")\
            .find_all("div", recursive=False)
        
        if results:
            print("Results found")
        else:
            print("Results not found")
        
        urls = [result.find("a", href=True).get('href') for result in results]
        return urls[:pages]
    
        # urls = []

        # for result in results:
        #     url = result.find("a", href=True).get('href')

        #     if url:
        #         print(f"URL found: {url}")
        #     else:
        #         print("URL not found")

        #     urls.append(url)
        #     if len(urls) >= pages:
        #         break
        # return urls
    
    def __generate_summary(self, content):
        max_chunk_size = 1024
        generated_summaries = []

        chunks = [content[i:i+max_chunk_size] for i in range(0, len(content), max_chunk_size)]

        for chunk in chunks:
            summary = self.summarizer(
                chunk,
                max_length=50,
                min_length=15,
                length_penalty=1.0,
                num_beams=5,
                do_sample=False,
                # temperature=0.8,
                early_stopping=False
            )
            generated_summaries.append(summary[0]['summary_text'])

        final_summary = " ".join(generated_summaries)
        return final_summary
    
    def search_cnn(self, query, pages=3):
        base_url = "https://www.cnn.com/search?q="
        formatted_query = quote(query)
        url = f"{base_url}{formatted_query}&from=0&size=10&page=1&sort=newest&types=article&section=business"

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        time.sleep(5)

        try:
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            driver.quit()

            search_urls = self.__get_search_urls(soup, pages)

            if len(search_urls) > 0:
                print(f"{len(search_urls)} URLs found")
            else:
                print("No URLs found")

            with ThreadPoolExecutor() as executor:
                content_list = list(executor.map(self.__get_article_content, search_urls))
            content = ' '.join(content_list)

            processed_content = content.replace("\n", " ").replace("  ", " ")
            processed_content = re.sub(r'\s+', ' ', processed_content).strip()

            print("ARTICLE CONTENT")
            print(processed_content)

            final_summary = self.__generate_summary(processed_content)
            return final_summary
        
        except Exception as e:
            print(f"Error: {e}")
        return []

def main():
    chatbot = FinancialChatbot()
    query = "Roth 401k"
    # query = "Real estate news"
    # query = "What is the equities market outlook for 2024?"

    output = chatbot.search_cnn(query)
    print()
    print("CHATBOT RESPONSE")
    print(output)

if __name__ == "__main__":
    chatbot = FinancialChatbot()
    main()