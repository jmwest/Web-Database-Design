#include "Index_server.h"

#include <fstream>
#include <iostream>

using std::cerr;
using std::endl;
using std::ifstream;
using std::ofstream;

extern void printInvertedIndexFile();

int main(int argc, char *argv[]) {
	
	Index_server server;
	const char *index_fname = argv[2];
	ifstream index_file(index_fname);
	if (!index_file.is_open()) {
		cerr << "Error opening file: " << index_fname << endl;
		return -1;
	}
	
	server.init(index_file);
	
	printInvertedIndexFile();
	
	return 0;
}