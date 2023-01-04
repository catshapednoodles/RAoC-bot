# Base image
FROM python:3.9-slim-buster

ENV RUNNING_IN_DOCKER Yes

WORKDIR /app

# here we create a new user
# note how the commands are using &&
# this helps with caching
# RUN useradd -m -r user && \
#   chown user /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY run.sh ./
RUN chmod a+x run.sh

COPY templates ./templates
COPY posts.py ./
COPY app.py ./
COPY raoc.py ./

# USER user

CMD ["./run.sh"]
