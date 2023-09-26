FROM ubuntu

RUN apt update

RUN apt install python3 python3-pip -y

COPY . *

CMD pip install -r req.txt

CMD python3 ./app/main.py


