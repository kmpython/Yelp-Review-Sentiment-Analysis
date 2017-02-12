from bs4 import BeautifulSoup
from googleapiclient import discovery
from oauth2client.client import GoogleCredentials
import urllib.request as ur
import sys


def get_service():
    credentials = GoogleCredentials.get_application_default()
    return discovery.build('language', 'v1',
                           credentials=credentials)


def get_native_encoding_type():
    """Returns the encoding type that matches Python's native strings."""
    if sys.maxunicode == 65535:
        return 'UTF16'
    else:
        return 'UTF32'


def analyze_sentiment(text, encoding='UTF32'):
    body = {
        'document': {
            'type': 'PLAIN_TEXT',
            'content': text,
        },
        'encoding_type': encoding
    }

    service = get_service()

    request = service.documents().analyzeSentiment(body=body)
    response = request.execute()

    return response


def scrape_page(pg_url):

    url = pg_url
    page = ur.urlopen(url)
    html = page.read()
    soup = BeautifulSoup(html, "html.parser")

    review_lst = []

    for reviews in soup.find_all("p", attrs={"lang": "en"}):
        review_lst.append(reviews.text)

    return review_lst

if __name__ == '__main__':

    page_url = str(input("please enter the url :"))
    customer_reviews = scrape_page(page_url)

    total_score = 0.00
    total_mag = 0.00
    count = 0

    for review in customer_reviews:
        count += 1
        sentiment = analyze_sentiment(review, get_native_encoding_type())
        total_score = total_score + sentiment['documentSentiment']['score']
        total_mag = total_mag + sentiment['documentSentiment']['magnitude']

    overall_sentiment = float("{0:.2f}".format(total_score/count))
    overall_magnitude = float("{0:.2f}".format(total_mag/count))

    if overall_sentiment > 0.20:
        if overall_magnitude >= 4.00:
            descrpt_var = "strongly positive"
        elif overall_magnitude >= 2.00 and overall_magnitude <= 3.99:
            descrpt_var = "clearly positive"
        elif overall_magnitude >= 0.00 and overall_magnitude <= 1.99:
            descrpt_var = "mildly positive"
    elif overall_sentiment >= -0.19 and overall_sentiment <= 0.19:
        if overall_magnitude >= 4.00:
            descrpt_var = "confused review"
        elif overall_magnitude >= 2.00 and overall_magnitude <= 3.99:
            descrpt_var = "mixed review"
        elif overall_magnitude >= 0.00 and overall_magnitude <= 1.99:
            descrpt_var = "Neutral"
    elif overall_sentiment <= -.20:
        if overall_magnitude >= 4.00:
            descrpt_var = "strongly positive"
        elif overall_magnitude >= 2.00 and overall_magnitude <= 3.99:
            descrpt_var = "clearly positive"
        elif overall_magnitude >= 0.00 and overall_magnitude <= 1.99:
            descrpt_var = "mildly positive"

    print("the overall sentiment of the document is " + str(overall_sentiment))
    print("the overall magnitude of the document is " + str(overall_magnitude))
    print("the overall emotion of the document is " + descrpt_var)
