import requests
from bs4 import BeautifulSoup
import os
import pandas as pd
from dotenv import load_dotenv, dotenv_values
from google import genai

# Load environment variables for API keys
config = dotenv_values("env")

# Configure Gemini API
client = genai.Client(api_key=config["gemini_token"])
model_name = "gemini-2.0-flash"

def scrape_website(url):
    """Scrape content from a news website."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract title
        title = soup.title.text if soup.title else "No title found"
        
        # Extract main text
        paragraphs = soup.find_all('p')
        main_text = ' '.join([p.text for p in paragraphs])
        
        return {
            'title': title,
            'content': main_text[:5000],  # Truncate to avoid hitting token limits
            'url': url
        }
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None

def summarize_website(website_data):
    """Use Gemini to summarize the website content and identify key topics."""
    prompt = f"""
    Analyze this news article and provide the following information:
    1. Main topic/category (e.g., politics, technology, sports)
    2. Geographic focus (e.g., US, global, specific region)
    3. 3-5 key themes or subtopics
    4. A brief summary (2-3 sentences)
    
    Article title: {website_data['title']}
    Article content: {website_data['content']}
    
    Format your response as JSON with keys: topic, geography, themes, summary
    """
    
    response = client.models.generate_content(
        model=model_name,
        contents=prompt
    )
    
    try:
        summary_info = eval(response.text)  # Convert the JSON-like string to a dictionary
        return summary_info
    except:
        # Fallback if the response isn't valid JSON
        print("Error parsing model response, using simplified extraction")
        return {
            'topic': website_data['title'],
            'geography': 'unknown',
            'themes': [website_data['title']],
            'summary': website_data['content'][:200]
        }

def find_similar_websites(summary_info):
    """Use Gemini to find similar news websites based on the summary."""
    prompt = f"""
    I need to find 10 news websites that cover similar stories to these characteristics:
    - General topic: {summary_info['topic']}
    - Geographic focus: {summary_info['geography']}
    - Key themes: {', '.join(summary_info['themes']) if isinstance(summary_info['themes'], list) else summary_info['themes']}
    
    Please provide direct URLs to 10 different news websites (not search engine links).
    These can be from any reputable news sources, including smaller publications, blogs, or niche sites.
    Focus on variety rather than exact matches - I'm looking for a diverse range of perspectives on similar topics.
    
    Return only the URLs, one per line, with no additional text.
    """
    print(summary_info)
    
    response = client.models.generate_content(
        model=model_name,
        contents=prompt
    )
    
    # Extract URLs from the response
    urls = [line.strip() for line in response.text.split('\n') if line.strip().startswith('http')]
    
    # Return up to 10 unique URLs
    return list(set(urls))[:10]

def analyze_sentiment(website_data):
    """Use Gemini to analyze the sentiment of a news article."""
    prompt = f"""
    Analyze the sentiment of this news article. Rate it on a scale from -10 (extremely negative) to 10 (extremely positive).
    Consider the overall tone, language use, and framing of events.
    
    Article title: {website_data['title']}
    Article content: {website_data['content']}
    
    Return only a number between -10 and 10 representing the sentiment score.
    """
    
    response = client.models.generate_content(
        model=model_name,
        contents=prompt
    )
    
    try:
        sentiment_score = float(response.text.strip())
        return sentiment_score
    except:
        print(f"Error parsing sentiment for {website_data['url']}, defaulting to neutral")
        return 0.0

def main():
    print("News Website Sentiment Analyzer")
    print("-" * 40)
    
    # Get user input
    url = input("Enter the URL of a news article: ")
    
    print("\nStep 1: Scraping the input website...")
    website_data = scrape_website(url)
    if not website_data:
        print("Failed to scrape the website. Please check the URL and try again.")
        return
    
    print("\nStep 2: Analyzing website content...")
    summary_info = summarize_website(website_data)
    print(f"Topic: {summary_info['topic']}")
    print(f"Geographic focus: {summary_info['geography']}")
    print(f"Summary: {summary_info['summary']}")
    
    print("\nStep 3: Finding similar news websites...")
    similar_urls = find_similar_websites(summary_info)
    print(f"Found {len(similar_urls)} similar websites:")
    for i, url in enumerate(similar_urls):
        print(f"  {i+1}. {url}")
    
    print("\nStep 4: Analyzing sentiment across all websites...")
    # Analyze sentiment of original website
    original_sentiment = analyze_sentiment(website_data)
    print(f"Original website sentiment score: {original_sentiment:.2f}")
    
    # Analyze sentiment of similar websites
    similar_sentiments = []
    
    for i, similar_url in enumerate(similar_urls):
        print(f"  Analyzing website {i+1}/{len(similar_urls)}: {similar_url}")
        similar_data = scrape_website(similar_url)
        if similar_data:
            sentiment = analyze_sentiment(similar_data)
            similar_sentiments.append(sentiment)
            print(f"    Sentiment score: {sentiment:.2f}")
    
    # Calculate average sentiment
    if similar_sentiments:
        avg_sentiment = sum(similar_sentiments) / len(similar_sentiments)
        print(f"\nAverage sentiment of similar websites: {avg_sentiment:.2f}")
        
        if original_sentiment > avg_sentiment:
            print(f"The original website is more POSITIVE than average by {original_sentiment - avg_sentiment:.2f} points")
        elif original_sentiment < avg_sentiment:
            print(f"The original website is more NEGATIVE than average by {avg_sentiment - original_sentiment:.2f} points")
        else:
            print("The original website has the same sentiment as the average")
    else:
        print("\nWarning: No sentiment data from similar websites.")

if __name__ == "__main__":
    main()