FROM gcc:latest

WORKDIR /usr/src/myapp

COPY test.c /usr/src/myapp

RUN gcc -o test test.c

CMD ["./test"]
