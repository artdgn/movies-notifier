FROM python:3.6

COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

ENV APP_DIR=/movies_notifier

ADD . ${APP_DIR}

WORKDIR ${APP_DIR}

ENTRYPOINT ["python", "check_new_movies.py"]

CMD ["--help"]

# docker build --pull -t artdgn/movies_notifier .
# docker push artdgn/movies_notifier