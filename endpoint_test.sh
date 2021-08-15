# sign-up
http -v POST "http://localhost:5000/sign-up" \
name=yyeon2 \
email=pushpyy@gmail.com \
password=test1234 \
profile="Machine Learning Engineer"


# login
http -v POST "http://localhost:5000/login" \
email=pushpyy@gmail.com \
password=test1234


# tweet
http -v POST localhost:5000/tweet tweet="hello world" "Authorization:eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE2MjkxMjQxNzB9._eCDnJrGfRr34kX8zTaL-6Qpo1IcIjzgFw7PGLvq3_w"
