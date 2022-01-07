import requests
import re

from bs4 import BeautifulSoup
from requests import Response
from typing import Tuple
from review import Review


def download_all_reviews_of(product_id: int) -> Tuple[str, list]:
    reviews: list[Review] = []
    page: int = 1

    response: Response = requests.get(f"https://www.ceneo.pl/{product_id}")

    if response.status_code == 200:
        page_source = BeautifulSoup(response.text, 'html.parser')
        product_name = page_source.select_one("h1.product-top__product-info__name").get_text()
    else:
        return "", []

    while True:
        response: Response = requests.get(f"https://www.ceneo.pl/{product_id}/opinie-{page}", allow_redirects=False)

        if not response.status_code == 200:
            break

        page_source: BeautifulSoup = BeautifulSoup(response.text, 'html.parser')
        reviews_source: BeautifulSoup.Tag = page_source.select("div.js_product-review")
        product_name: str = page_source.select_one("h1.product-top__product-info__name").get_text()

        for review_source in reviews_source:
            r_id: int = int(review_source["data-entry-id"])
            r_author: str = review_source.select_one("span.user-post__author-name").get_text("", True)
            r_recommended: str = review_source.select_one("span.user-post__author-recomendation > em").get_text()
            r_score: str = review_source.select_one("span.user-post__score-count").get_text()
            published_dates: BeautifulSoup.Tag = review_source.select_one("span.user-post__published").select("time")
            r_published_date: str = published_dates[0]["datetime"]
            r_purchased_date: str = published_dates[0]["datetime"] if published_dates[0:] else ""
            r_content: str = review_source.select_one("div.user-post__text").get_text()
            r_positive_votes: int = int(review_source.select_one("button.vote-yes > span").get_text())
            r_negative_votes: int = int(review_source.select_one("button.vote-no > span").get_text())
            r_verified: bool = bool(review_source.select_one("div.review-pz > em"))
            review: Review = Review(r_id, r_author, r_recommended, r_score, r_published_date, r_purchased_date,
                                    r_content, r_positive_votes, r_negative_votes, r_verified)
            reviews.append(review)

        page += 1

    return product_name, reviews


def run():
    product_id: int = int(input("Podaj numer id produktu: "))

    product_name, reviews = download_all_reviews_of(product_id)
    if product_name == "":
        print("Wrong product id")

    product_name = re.sub(r"[^\w\-_.\s]", "_", product_name)

    file_name = f"{product_name}-{product_id}.json"

    with open(file_name, "w", encoding="utf-8") as file:
        file.write("[")

        for i in range(len(reviews) - 1):
            file.write(reviews[i].to_json() + ",")
            file.write("\n")

        file.write(reviews[-1].to_json())
        file.write("\n")

        file.write("]")
