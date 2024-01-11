from transformers import pipeline, PegasusForConditionalGeneration, PegasusTokenizer
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import quote
from bs4 import BeautifulSoup
import time
import re
import torch

# Global progress variable
progress = 0

# Chatbot class
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

    # Get content of article
    def __get_article_content(self, url):
        global progress

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
            progress += 10

            groups = soup.find_all("div", class_="group")
            for group in groups:
                paragraphs = group.find_all("p")
                article_content += ' '.join([paragraph.text for paragraph in paragraphs])

            return article_content
        
        except Exception as e:
            print(f"Error: {e}")
        return ""
    
    # Get valid urls (free articles, not membership articles)
    def __extract_valid_urls(self, results):
        valid_urls = []
        for result in results:
            card = result.find("div", class_="SearchResult-searchResultCard SearchResult-standardVariant")
            content = result.find("div", class_="SearchResult-searchResultContent")
            
            not_a_video = False
            if card:
                classes = card.find(recursive=False).get('class', [])
                if "resultlink" in classes:
                    not_a_video = True
            else:
                not_a_video = True

            if not_a_video:
                eyebrow = content\
                    .find("div", class_="SearchResult-searchResultEyebrow")\
                    .find("a").text.lower()
                if ("pro: " not in eyebrow) and ("club" not in eyebrow):
                    url = content\
                        .find("div", class_="SearchResult-searchResultTitle")\
                        .find("a", href=True).get('href').replace(" ", "%20")
                    valid_urls.append(url)

        return valid_urls

    # Scroll page
    def __scroll_page(self, driver):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        print("Scrolled page")

    def __convert_to_bs4_object(self, result):
        return BeautifulSoup(result.get_attribute('outerHTML'), 'html.parser')
    
    # Get search results
    def __get_search_urls(self, soup, pages, driver):
        global progress

        search_container = soup.find("div", id="searchcontainer")
        urls = []

        initial_results = search_container.find_all("div", class_="SearchResult-searchResult SearchResult-standardVariant")
        initial_urls = self.__extract_valid_urls(initial_results)
        urls.extend(initial_urls)

        while len(urls) < pages:
            self.__scroll_page(driver)
            try:
                new_results = WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "SearchResult-searchResult")))
            except Exception as e:
                print("No records")
                return []
            new_results_converted = [self.__convert_to_bs4_object(result) for result in new_results]
            new_urls = self.__extract_valid_urls(new_results_converted)
            urls.extend(new_urls)
            progress += 10

            if not new_urls:
                break
        return urls[:pages]
    
    # Generate summary based on combined article content
    def __generate_summary(self, content):
        global progress

        max_chunk_size = 1024
        generated_summaries = []
        progress += 10

        print("ARTICLE CONTENT")
        print(content)

        chunks = [content[i:i+max_chunk_size] for i in range(0, len(content), max_chunk_size)]
        summarizer = self.__load_model()
        progress += 10

        for chunk in chunks:
            summary = summarizer(
                chunk,
                max_length=40,
                min_length=10,
                length_penalty=1.0,     # Increase for longer sentences
                num_beams=1,            # Increase for more diversity and complexity, but increases computational power
                do_sample=False,        # Setting this to True allows for more randomness, and allows temperature hyperparameter to be changed
                # temperature=1.2,      # Increase for more randomness (only valid if do_sample is True)
                early_stopping=False    # Don't set this to True, it truncates some sentences
            )
            generated_summaries.append(summary[0]['summary_text'])

        final_summary = " ".join(generated_summaries)
        progress += 5
        return final_summary

    # Primary method to generate output - searches CNBC
    def generate_output(self, query, pages=3):
        global progress
        progress = 0

        # CNBC
        base_url = "https://www.cnbc.com/search/"
        formatted_query = quote(query)
        url = f"{base_url}?query={formatted_query}&qsearchterm={formatted_query}"
        progress += 5

        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        time.sleep(5)
        progress += 5

        try:
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            progress += 5

            search_urls = self.__get_search_urls(soup, pages, driver)
            if len(search_urls) > 0:
                print(f"{len(search_urls)} URLs found")
            else:
                print("No URLs found")

            content = ""
            for url in search_urls:
                content += self.__get_article_content(url)
            
            driver.quit()

            processed_content = content.replace("\n", " ").replace("  ", " ")
            processed_content = re.sub(r'\s+', ' ', processed_content).strip()

            final_summary = self.__generate_summary(content)
            return final_summary
        
        except Exception as e:
            print(f"Error: {e}")
        return []
    
# Progress getter variable
def get_progress():
    return progress