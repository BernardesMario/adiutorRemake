FROM python:3.12-buster
ENV PYTHONUNBUFFERED 1

RUN mkdir /src
WORKDIR /src

COPY requirements.txt /src
RUN pip install -r requirements.txt

COPY . .

RUN pip freeze > /installed-requirements.txt

EXPOSE 8000

RUN python manage.py create_groups
RUN python manage.py migrate

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
