# Makefile

CC = g++
LD = g++

CFLAGS = -pedantic -Wall -c -std=c++11
SERVER_LFLAGS = -ldl -pthread -lpthread
INDEXER_LFLAGS =
TFIDF_LFLAGS =
STEST_LFLAGS = -ldl -lpthread

SERVER_OBJS = server_main.o Index_server.o mongoose.o
INDEXER_OBJS = indexer_main.o Indexer.o
TFIDF_OBJS = tfidf_test.o
SERVER_TEST_OBJS = Index_server.o mongoose.o Index_server_test.o

SERVER_TEST_FILES = Index_server.h Index_server.cpp Index_server_test.cpp mongoose.h mongoose.c TFIDF_CALC.h

SERVER = indexServer
INDEXER = indexer
TFIDF_TEST = tfidf_test
SERVER_TEST = server_test

CAPTIONS_PATH = ../resources/captions.txt
INDEX_PATH = ../index/inverted_index.txt

PORT_NUMBER = 3002

default: $(SERVER) $(INDEXER)
test: $(TFIDF_TEST) $(SERVER_TEST)

debug: CFLAGS += -g
debug: SERVER_LFLAGS += -g
debug: INDEXER_LFLAGS += -g
debug: $(SERVER) $(INDEXER)

$(SERVER): $(SERVER_OBJS)
	$(LD) $(SERVER_OBJS) -o $(SERVER) $(SERVER_LFLAGS)

server_main.o: server_main.cpp Index_server.h
	$(CC) $(CFLAGS) server_main.cpp

Index_server.o: Index_server.cpp Index_server.h
	$(CC) $(CFLAGS) Index_server.cpp

mongoose.o: mongoose.c mongoose.h
	gcc -c mongoose.c 

$(INDEXER): $(INDEXER_OBJS)
	$(LD) $(INDEXER_LFLAGS) $(INDEXER_OBJS) -o $(INDEXER)

indexer_main.o: indexer_main.cpp Indexer.h
	$(CC) $(CFLAGS) indexer_main.cpp

Indexer.o: Indexer.cpp Indexer.h
	$(CC) $(CFLAGS) Indexer.cpp

$(TFIDF_TEST): $(TFIDF_OBJS)
	$(LD) $(TFIDF_LFLAGS) $(TFIDF_OBJS) -o $(TFIDF_TEST)

tfidf_test.o: TFIDF_test.cpp
	$(CC) $(CFLAGS) TFIDF_test.cpp

$(SERVER_TEST): $(SERVER_OBJS) Indexer.o Index_server_test.o
	$(LD) $(STEST_LFLAGS) $(SERVER_TEST_OBJS) -o $(SERVER_TEST)

Index_server_test.o:
	$(CC) $(CFLAGS) Index_server_test.cpp

clean:
	rm -rf *.o $(SERVER) $(INDEXER) $(TFIDF_TEST) $(SERVER_TEST)

captions:
	./indexer captions.txt captions_output.txt

run:
	./$(INDEXER) $(CAPTIONS_PATH) $(INDEX_PATH)
	./$(SERVER)  $(PORT_NUMBER)   $(INDEX_PATH)

rebuild:
	make clean
	make
	make run

background:
	make clean
	make
	./$(INDEXER) $(CAPTIONS_PATH) $(INDEX_PATH)
	./$(SERVER)  $(PORT_NUMBER)   $(INDEX_PATH) &

diego:
	./indexer diego.txt diego_output.txt

john: TFIDF_test.cpp TFIDF_CALC.cpp
	./tfidf_test

stest: $(SERVER_TEST_FILES)
	./indexer diego.txt diego_output.txt
	./server_test diego.txt diego_output.txt
