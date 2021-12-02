from sqlalchemy import text


class TweetDao:
    def __init__(self, database):
        self.db = database

    def insert_tweet(self, user_id, tweet):
        return self.db.execute(
            text(
                """
                INSERT INTO users (user_id, tweet)
                VALUES (:user_id, :tweet)
                """
            ),
            {"id": user_id, "tweet": tweet},
        ).rowcount

    def get_timeline(self, user_id):
        timeline = self.db.execute(
            text(
                """
                SELECT t.user_id, t.twwet
                FROM tweets AS t
                LEFT JOIN user_follow_list AS ufl 
                ON ufl.user_id = :user_id
                WHERE t.user_id = :user_id OR t.user_id = ufl.follow_user_id
                """
            ),
            {"id": user_id},
        ).fetchall()

        return [
            {"user_id": tweet["user_id"], "tweet": tweet["tweet"]} for tweet in timeline
        ]
