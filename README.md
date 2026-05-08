📰 News Topic Classifier (NLP & BERT)

A multi-class classifier designed to categorize news articles into topics. Built with RuBERT-tiny2 and optimized for processing Russian language news content from RIA and Lenta.ru.



🌟 Key Features


High Performance: Achieved 90%+ validation accuracy by leveraging pre-trained transformer embeddings.
Dynamic Scraping: Built-in scraper with Selenium support for infinite scroll handling and ThreadPoolExecutor for fast content retrieval.
Production Ready: The trained model is exported via joblib, making it ready for integration into web apps or Telegram bots.

🛠 Tech Stack


Framework: Scikit-learn / PyTorch
Base Model: RuBERT-tiny2 (by cointegrated)
Data Collection: Selenium, BeautifulSoup4, Requests
Techniques: Transfer Learning (Embeddings), Logistic Regression, Class Weight Balancing.


📊 Model Architecture


The model leverages the pre-trained feature extractor of RuBERT-tiny2 to convert raw text into 312-dimensional semantic vectors, followed by a custom Logistic Regression head for multi-class topic classification.

⚙️ Installation

To set up the environment and install all dependencies, run the following commands:

```# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

#  Install dependencies from requirements.txt
pip install -r requirements.txt
```


📈 Results


The model demonstrates high precision and recall across various news categories:
Accuracy: 0.906
Macro F1-Score: 0.90
Top Performing Category: Sport (F1: 0.97)
