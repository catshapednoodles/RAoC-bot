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

COPY . .

RUN chmod a+x run.sh

# USER user

CMD ["./run.sh"]
