from os import access
from datetime import datetime, timedelta

import bcrypt
import jwt
import functools

from flask import Flask, jsonify, request, current_app, request, Response, g
from flask_cors import CORS
from flask.json import JSONEncoder
from sqlalchemy import create_engine, text


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return JSONEncoder.default(self, obj)


def get_user(user_id):
    user = current_app.database.execute(
        text(
            """
                                            SELECT id, name, email, profile 
                                            FROM users
                                            WHERE id =:user_id
                                            """
        ),
        {"user_id": user_id},
    ).fetchone()
    return (
        {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "profile": user["profile"],
        }
        if user
        else None
    )


def insert_user(user):
    return current_app.database.execute(
        text(
            """
                                             INSERT INTO users (name, email, profile, hashed_password) 
                                             VALUES (:name, :email, :profile, :password)
                                             """
        ),
        user,
    ).lastrowid


def insert_tweet(user_tweet):
    return current_app.database.execute(
        text(
            """
                                            INSERT INTO tweets (user_id, tweet)
                                            VALUES (:id, :tweet)
                                            """
        ),
        user_tweet,
    ).rowcount


def insert_follow(user_follow):
    return current_app.database.execute(
        text(
            """
                                            INSERT INTO users_follow_list (user_id, follow_user_id)
                                            VALUES (:id, :follow)
                                            """
        ),
        user_follow,
    ).rowcount


def insert_unfollow(user_unfollow):
    return current_app.database.execute(
        text(
            """
                                            DELETE FROM users_follow_list
                                            WHERE user_id =:id
                                            AND follow_user_id =:unfollow
                                            """
        ),
        user_unfollow,
    ).rowcount


def get_timeline(user_id):
    timeline = current_app.database.execute(
        text(
            """
                                                SELECT t.user_id, t.tweet
                                                FROM tweets AS t
                                                LEFT JOIN users_follow_list AS ufl
                                                ON ufl.user_id =:user_id
                                                WHERE t.user_id =:user_id OR t.user_id = ufl.follow_user_id
                                                """
        ),
        {"user_id": user_id},
    ).fetchall()
    return [
        {"user_id": tweet["user_id"], "tweet": tweet["tweet"]} for tweet in timeline
    ]


def get_user_id_and_password(email):
    row = current_app.database.execute(
        text(
            """
                                           SELECT id, hashed_password
                                           FROM users
                                           WHERE email=:email
                                           """
        ),
        {"email": email},
    ).fetchone()
    return {"id": row["id"], "hashed_password": row["hashed_password"]} if row else None


def login_required(f):
    @functools.wraps(f)
    def decorated_function(*args, **kwargs):
        access_token = request.headers.get("Authorization")
        if access_token is not None:
            try:
                payload = jwt.decode(
                    access_token, current_app.config["JWT_SECRET_KEY"], "HS256"
                )
            except jwt.InvalidTokenError:
                payload = None

            if payload is None:
                return Response(status=401)

            user_id = payload["user_id"]
            g.user_id = user_id
            g.user = get_user(user_id) if user_id else None

        else:
            return Response(status=401)
        return f(*args, **kwargs)

    return decorated_function


def create_app(test_config=None):
    app = Flask(__name__)

    CORS(app)

    if test_config is None:
        app.config.from_pyfile("config.py")
    else:
        app.config.update(test_config)

    database = create_engine(app.config["DB_URL"], encoding="UTF-8", max_overflow=0)
    app.database = database
    app.config["JWT_SECRET_KEY"] = "yyeon"

    @app.route("/ping", methods=["GET"])
    def ping():
        return "pong"

    @app.route("/sign-up", methods=["POST"])
    def sign_up():
        new_user = request.json
        new_user["password"] = bcrypt.hashpw(
            new_user["password"].encode("UTF-8"), bcrypt.gensalt()
        )
        new_user_id = insert_user(new_user)
        new_user = get_user(new_user_id)
        return jsonify(new_user)

    @app.route("/login", methods=["POST"])
    def login():
        credential = request.json
        email = credential["email"]
        password = credential["password"]
        user_credential = get_user_id_and_password(email)

        if user_credential and bcrypt.checkpw(
            password.encode("UTF-8"), user_credential["hashed_password"].encode("UTF-8")
        ):
            user_id = user_credential["id"]
            payload = {
                "user_id": user_id,
                "exp": datetime.utcnow() + timedelta(seconds=60 * 60 * 24),
            }
            token = jwt.encode(
                payload=payload, key=app.config["JWT_SECRET_KEY"], algorithm="HS256"
            )
            return jsonify(
                {
                    "access_token": token  # jwt version에 따라서 encode의 출력 결과가 다르게 됨.(20version 이후부터는 string을 출력하기 때문에 decode과정 필요없음)
                }
            )
        else:
            return "", 421

    @app.route("/tweet", methods=["POST"])
    @login_required
    def tweet():
        user_tweet = request.json
        user_tweet["id"] = g.user_id
        tweet = user_tweet["tweet"]

        if len(tweet) > 300:
            return "300자를 초과하였습니다.", 400

        insert_tweet(user_tweet)
        return "", 200

    @app.route("/follow", methods=["POST"])
    @login_required
    def follow():
        payload = request.json
        insert_follow(payload)

        return "", 200

    @app.route("/unfollow", methods=["POST"])
    @login_required
    def unfollow():
        payload = request.json
        insert_unfollow(payload)

        return "", 200

    @app.route("/timeline/<int:user_id>", methods=["GET"])
    def timeline(user_id):
        return jsonify({"user_id": user_id, "timeline": get_timeline(user_id)})

    @app.route("/timeline", methods=["GET"])
    @login_required
    def user_timeline():
        user_id = g.user_id

        return jsonify({"user_id": user_id, "timeline": get_timeline(user_id)})

    return app
