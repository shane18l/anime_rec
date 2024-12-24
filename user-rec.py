import pandas as pd
from pathlib import Path
from sklearn.metrics.pairwise import cosine_similarity

path = "files/user-filtered.csv"
df = pd.read_csv(path)

titles_path = "files/anime-filtered.csv"
titles_df = pd.read_csv(titles_path)
titles_dict = titles_df.set_index('anime_id')['Name'].to_dict()
print(titles_dict)

# Create matrix (users are rows, anime are columns)
user_matrix = df.pivot(index='user_id', columns='anime_id', values='rating').fillna(0)

# Calculate cosine similarity
user_similarity = cosine_similarity(user_matrix)

user_similarity_df = pd.DataFrame(user_similarity, index=user_matrix.index, columns= user_matrix.index)
print(user_similarity_df)

def get_anime_name(anime_id):
    return titles_dict[anime_id]

def recommend_anime(user_id, user_matrix, user_similarity_df, num_rec =5):
    user_id = int(user_id)
    similar_users = user_similarity_df[user_id]
    similar_users = similar_users.drop(user_id).sort_values(ascending=False)
    similar_users = similar_users.head(num_rec)

    recommendations = {}

    for similar_user in similar_users.index:
        user_ratings = user_matrix.loc[similar_user]

        for anime_id, rating in user_ratings.items():
            if rating >= 7 and user_matrix.loc[user_id, anime_id] == 0:
                if anime_id not in recommendations:
                    recommendations[anime_id] = 0
                recommendations[anime_id] += rating * similar_users[similar_user]

    sorted_recs = sorted(recommendations.items(), key= lambda x: x[1], reverse=True)
    top_sorted = sorted_recs[:num_rec]
    return top_sorted

user_id = input(f"Enter your userid, and we'll recommend you animes: ")
final_recs = recommend_anime(user_id, user_matrix, user_similarity_df)

for rec, score in final_recs:
    title = get_anime_name(rec)
    print(f"We recommend: {title}")



    