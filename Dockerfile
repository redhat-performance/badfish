FROM quay.io/quads/python39:latest

RUN apk add git && apk update

RUN git clone https://github.com/redhat-performance/badfish

WORKDIR badfish

RUN apk add build-base
RUN pip install --no-cache-dir -r requirements.txt
RUN python setup.py build
RUN python setup.py install

ENTRYPOINT ["badfish"]
CMD ["-v"]
