import pandas as pd
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import csv
import re
from difflib import SequenceMatcher
from rapidfuzz import process

path = Path('files/anime-filtered.csv')
lines = path.read_text(encoding="utf-8").splitlines()
content = csv.reader(lines)

header = next(content)




# Function to process descriptions
def preprocess_text(text):
    text = text.lower()  # Convert to lowercase
    text = re.sub(r'[^a-z0-9\s]', '', text)  # Remove special characters
    return text

# Function returns true if titles are too similar
def is_similar(title1, title2, threshold=0.3):
    #Check if two titles are similar based on a similarity threshold.
    ratio = SequenceMatcher(None, title1.lower(), title2.lower()).ratio()
    return ratio >= threshold

# Function to remove similar titles
def filter_titles(titles):
    filtered = [match]
    for title in titles:
        if not any(is_similar(title, seen_title) for seen_title in filtered):
            filtered.append(title)
    return filtered

# Function that generates recommendations by finding animes w similar descriptions
def generate_recs():


    cleaned_desc = [anime['desc'] for anime in descs]
    tfidf = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform(cleaned_desc)
    similarity_matrix = cosine_similarity(tfidf_matrix)

    # Index of the user's anime
    user_index = anime_names.index(match)
    similarity_scores = list(enumerate(similarity_matrix[user_index]))

    sorted_scores = sorted(similarity_scores, key = lambda x:x[1], reverse=True)

    # Sort the titles by increasing similarity score
    sorted_titles = []
    for idx, score in sorted_scores[:30]:
        if idx != user_index:
            if anime_names[idx] == 'unknown':
                sorted_titles.append(descs[idx]['jap_name'])
            else:
                sorted_titles.append(anime_names[idx])

    # Filter similar titles
    filtered_titles = filter_titles(sorted_titles)
    for title in filtered_titles[1:6]:
        print(f"We recommend: {title}")
    print("\n")


    


descs = []
for row in content:
    dict = {'name': row[header.index('English name')].lower(),
            'jap_name' : row[header.index('Name')].lower(),
            'rating': row[header.index('Score')],
            'desc': preprocess_text(row[header.index('sypnopsis')]),}
    descs.append(dict)

while True:
    # Prompt user for anime title
    user_input = input("Enter an anime you've enjoyed and we'll recommend you" +
                       "more (enter 'n' to quit): ")
    user_input = user_input.strip().lower()
    if user_input == 'n':
        break
    else:
        anime_names = [anime['name'] for anime in descs]
        # Match the user input to the closest anime title
        result = process.extractOne(user_input, anime_names)

        # Unpack only the match and score
        match, score = result[:2]

        if score >= 80:
            print(f"Did you mean {match}? \n")
            found_anime = next((anime['name'] for anime in descs if anime['name'] == match), None)
            if found_anime:
                generate_recs()
        else:
            print(f"We don't recognize this anime: {user_input}?")




