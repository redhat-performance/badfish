FROM python:3-alpine

RUN apk add git && apk update

RUN git clone https://github.com/redhat-performance/badfish

WORKDIR badfish

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "badfish.py"]
CMD ["-v"]
