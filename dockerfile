FROM python:alpine3.7
COPY . /app
WORKDIR /app
RUN pip3 install pipenv
RUN pipenv install --system
EXPOSE 5000
CMD python ./app/dice.py