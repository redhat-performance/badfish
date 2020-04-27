FROM python:3-alpine

RUN apk add git && apk update

RUN git clone https://github.com/redhat-performance/badfish

WORKDIR badfish

RUN pip install -r requirements.txt
RUN python setup.py build
RUN python setup.py develop

ENTRYPOINT ["badfish"]
CMD ["-v"]
