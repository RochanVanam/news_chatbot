from transformers import pipeline, PegasusForConditionalGeneration, PegasusTokenizer
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from urllib.parse import quote
import torch
import requests
import time
import re

progress = 0

class Chatbot:
    def __init__(self):
        # self.summarizer = pipeline('summarization', model="google/pegasus-xsum") # This program dynamically loads model, so this line is not needed
        pass

    def __load_model(self):
        # Load Google Pegasus LLM
        model_name = "google/pegasus-xsum"
        model = PegasusForConditionalGeneration.from_pretrained(model_name)
        tokenizer = PegasusTokenizer.from_pretrained(model_name)
        return pipeline('summarization', model=model, tokenizer=tokenizer)

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
    
    def __generate_summary(self, content):
        global progress

        max_chunk_size = 1024
        generated_summaries = []

        chunks = [content[i:i+max_chunk_size] for i in range(0, len(content), max_chunk_size)]

        summarizer = self.__load_model()
        progress += 10

        for chunk in chunks:
            summary = summarizer(
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

        progress += 30

        final_summary = " ".join(generated_summaries)
        return final_summary
    
    def generate_output(self, query, pages=3):
        global progress
        progress = 0

        base_url = "https://www.cnn.com/search?q="
        formatted_query = quote(query)
        url = f"{base_url}{formatted_query}&from=0&size=10&page=1&sort=newest&types=article&section=business"

        progress += 10

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

            progress += 10

            if len(search_urls) > 0:
                print(f"{len(search_urls)} URLs found")
            else:
                print("No URLs found")

            with ThreadPoolExecutor() as executor:
                content_list = list(executor.map(self.__get_article_content, search_urls))
            content = ' '.join(content_list)

            progress += 30

            processed_content = content.replace("\n", " ").replace("  ", " ")
            processed_content = re.sub(r'\s+', ' ', processed_content).strip()

            progress += 10

            print("ARTICLE CONTENT")
            print(processed_content)

            final_summary = self.__generate_summary(processed_content)
            return final_summary
        
        except Exception as e:
            print(f"Error: {e}")
        return []
    
def get_progress():
    return progress
