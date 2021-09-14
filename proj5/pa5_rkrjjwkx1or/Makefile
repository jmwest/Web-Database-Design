CC = g++

CFLAGS = -c -g --std=c++11 -pedantic -Wall -O3
LFLAGS = -g -O3 --std=c++11

HITS_OBJS = hits_code/hits.o
HITS_PROG = hits

PAGERANK_OBJS = pagerank_code/pagerank.o
PAGERANK_PROG = pagerank

default: $(HITS_PROG) $(PAGERANK_PROG)

$(HITS_PROG): $(HITS_OBJS)
	$(CC) $(LFLAGS) $(HITS_OBJS) -o $(HITS_PROG)

hits_code/hits.o: hits_code/hits.cpp
	$(CC) $(CFLAGS) hits_code/hits.cpp -o hits_code/hits.o

$(PAGERANK_PROG): $(PAGERANK_OBJS)
	$(CC) $(LFLAGS) $(PAGERANK_OBJS) -o $(PAGERANK_PROG)

pagerank_code/pagerank.o: pagerank_code/pagerank.cpp
	$(CC) $(CFLAGS) pagerank_code/pagerank.cpp -o pagerank_code/pagerank.o

clean:
	rm -f hits_code/*.o pagerank_code/*.o hits pagerank test/*_out*.txt

# ^^^^ DO NOT MODIFY MAKEFILE ABOVE
# Custom commands for convenience

build:
	@echo "\nCleaning Solution..."
	make clean
	@echo "\nBuilding Solution..."
	make

run_hits:
	make build
	@echo "\nRunning hits..."
	./hits config.hits

run_pagerank:
	make build
	@echo "\nRunning pagerank..."
	./pagerank config.pagerank

test_pagerank:
	make build
	@echo "\nRunning pagerank on test cases..."
	./pagerank test/pagerank/test1_config.pagerank
	./pagerank test/pagerank/test2_config.pagerank

test_hits:
	make build
	@echo "\nRunning hits on test cases..."
	./hits test/config_test1.hits
	./hits test/config_test2.hits
	./hits test/config_test3.hits

submit:
	cp pagerank_code/pagerank.cpp _submit/pagerank.cpp
	cp hits_code/hits.cpp _submit/hits.cpp

hit:
	make
	./hits test/config_test2.hits
	wc -l test/test2_out.txt
