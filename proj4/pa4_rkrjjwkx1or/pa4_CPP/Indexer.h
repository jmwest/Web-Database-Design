#ifndef INDEXER_H
#define INDEXER_H

#include <iosfwd>

class Indexer {
public:
    void index(std::istream& content, std::ostream& outfile);
};

#endif
