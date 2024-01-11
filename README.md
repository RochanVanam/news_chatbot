# News Chatbot
## Overview
This app is a news chatbot that presents relevant news to the query.

## Requirements
- Python 3.10
- All required libraries and frameworks can be found in ```requirements.txt```.

## Installation
Clone the repository to your local machine using ```git clone https://github.com/RochanVanam/news_chatbot.git```.

## Usage
1. Open terminal/command prompt/CLI, navigate to directory of choice
2. Clone repository
3. Create and activate virtual environment in Python 3.10 (optional but recommended)
4. Install libraries using ```pip install -r requirements.txt```
5. Run app.py using ```python app.py```
6. Open browser and go to the web address printed in CLI
7. Enter query. It might take a minute to get a response.

# CNN
In ```other_versions/```, there is a program called ```cnn.py``` that scrapes CNN instead of CNBC.
1. To scrape CNN, move ```cnn.py``` into the main project directory.
2. Go to app.py and edit the import statement at the top from ```from main import Chatbot, get_progress``` to ```from cnn import Chatbot, get_progress```.
3. Do steps 5-7 from above.

## Data and Model
This program scrapes CNBC for news data, and uses Google's Pegasus model off HuggingFace to synthesize an output. Additionally, in ```other_versions/```, there is a program that scrapes CNN instead of CNBC.

- [CNBC](https://www.cnbc.com/)
- [Google Pegasus](https://huggingface.co/google/pegasus-xsum)
- [CNN](https://www.cnn.com/)

Thank you!

**Rochan V:**
- [GitHub](https://github.com/RochanVanam)
- [LinkedIn](https://www.linkedin.com/in/rochanvanam/)
