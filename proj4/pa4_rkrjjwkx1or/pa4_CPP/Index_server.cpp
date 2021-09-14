#include "Index_server.h"

#include <cassert>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iostream>
#include <sstream>

// DO NOT MODIFY vvvvvv
#ifndef UNIT_TEST
#include <pthread.h>
#include "mongoose.h"
#endif
// DO NOT MODIFY ^^^^^^

using std::cerr;
using std::cout;
using std::endl;
using std::ifstream;
using std::ostream;
using std::ostringstream;
using std::string;
using std::vector;

namespace {
    // DO NOT MODIFY vvvvvv
    #ifndef UNIT_TEST
    int handle_request(mg_connection *);
    int get_param(const mg_request_info *, const char *, string&);
    string get_param(const mg_request_info *, const char *);
    #endif
    // DO NOT MODIFY ^^^^^^
    string to_json(const vector<Query_hit>&);

    ostream& operator<< (ostream&, const Query_hit&);
}

// DO NOT MODIFY vvvvvv
#ifndef UNIT_TEST
pthread_mutex_t mutex;

// Runs the index server on the supplied port number.
void Index_server::run(int port)
{
    // List of options. Last element must be NULL
    ostringstream port_os;
    port_os << port;
    string ps = port_os.str();
    const char *options[] = {"listening_ports",ps.c_str(),0};

    // Prepare callback structure. We have only one callback, the rest are NULL.
    mg_callbacks callbacks;
    memset(&callbacks, 0, sizeof(callbacks));
    callbacks.begin_request = handle_request;

    // Initialize the global mutex lock that effectively makes this server
    // single-threaded.
    pthread_mutex_init(&mutex, 0);

    // Start the web server
    mg_context *ctx = mg_start(&callbacks, this, options);
    if (!ctx) {
        cerr << "Error starting server." << endl;
        return;
    }

    pthread_exit(0);
}
#endif
// DO NOT MODIFY ^^^^^^



















// STAHP SCROLL BACK DOWN ///////////////////////////////////////////////////////////////////////////
// DON'T TOUCH ANYTHING ABOVE THIS //////////////////////////////////////////////////////////////////




















#include <cmath>
#include <algorithm>
#include <unordered_map>
#include <string>
#include <vector>
#include <list>

//THINGS COPIED FROM TFIDF_CALC.h
struct InvertedIndexCaption {
    unsigned docId;                  // Doc_id
    int occurrencesInDoc;       // number of occurrences in Doc_id
    double normalizationFactor; // Doc_id's normalization factor (before sqrt)
};

struct InvertedIndexRow {
    string word;
    double idf;                 // log(N / n_k)
    int occurrences;            // total #occurrences
    vector<InvertedIndexCaption> captions;
};

// number of docs (max doc id)
unsigned int numDocs = 0;

// Hash table of Inverted Index File
// key = word
// value = row
std::unordered_map<string, InvertedIndexRow> invertedIndexFile;

void transformToLowerCase_server(string& input) {
    transform(input.begin(), input.end(), input.begin(), ::tolower);
}

void removeNonAlphaNumeric_server(string& input) {
    for (unsigned int i = 0; i < input.length(); i++) {
        if (!isalnum(input[i]) && input[i] != ' ') {
            input.erase(i, 1);
            i--;
        }
    }
}

void removeStopWords_server(vector<string>& input_words) {

    cout << endl << "Removing stopwords from query..." << endl;
    bool foundAnyStopWords = false; // This is just for output

    // Open stopwords.txt
    ifstream stopwords("stopwords.txt");
    if (stopwords.is_open()) {

        // For each word in stopwords.txt,
        // if input_words is one of those words, remove that word
        string word;
        while(getline(stopwords, word)) {

            removeNonAlphaNumeric_server(word);
            bool removedWord = true;

            while (removedWord) {
                for (auto it = input_words.begin(); it != input_words.end(); it++) {
                    if (word == *it) {
                        input_words.erase(it);
                        foundAnyStopWords = true;
                        cout << "  Found a stopword: " << word << endl;
                        break;
                    }
                    removedWord = false;
                }

                if (input_words.size() == 0)
                    input_words.push_back("entarotassadar");
            }
        }
    }

    if (foundAnyStopWords)
        cout << "Successfully removed stopwords." << endl;
    else
        cout << "Did not find any stopwords." << endl;
}

// Format query appropriately and split up words.
// Return a vector of each word in doc.
vector<string> splitUpWords_server(string doc) {
    transformToLowerCase_server(doc);
    removeNonAlphaNumeric_server(doc);
    // Split string by spaces, push into vector

    vector<string> words;
    string crazy = "this query should not return anything. yolo! battlecruiser operational. en taro tassadar.";

    if (doc.length() == 0) {
        words.push_back(crazy);
        return words;
    }

    string word;
    std::istringstream iss(doc);
    while (iss >> word) {
        words.push_back(word);
    }
    removeStopWords_server(words);

    return words;
}

// Add InvertedIndexRow to invertedIndexFile
void addInvertedIndexRowToFile_server(InvertedIndexRow row, string key) {
    //cerr << "We in insert row to file" << endl;
    std::pair<string, InvertedIndexRow> obj (key, row);
    invertedIndexFile.insert(obj);
    return;
}

vector<unsigned int> buildDocList_server(const vector<string> & word_list) {

    unsigned int numDocs = invertedIndexFile.size();

    vector<unsigned int> word_appearances_in_doc(numDocs);
    unsigned num_words = word_list.size();

    cout << endl << "Starting for loop in buildDocList_server. There are " << num_words << " words in word_list." << endl;
    for (unsigned i = 0; i < num_words; ++i) {
        cout << "  i = " << i << endl;
        cout << "  Current word: " << word_list.at(i) << endl;
        std::unordered_map<string, InvertedIndexRow>::const_iterator result = invertedIndexFile.find(word_list.at(i));
        
        // If the current word does not match any key in the table
        // return an empty vector cuz boolean AND
        if (result == invertedIndexFile.end()) {
            cout << "  Current word does not match any key in table." << endl;
            cout << "  Returning an empty vector..." << endl;
            return vector<unsigned int>();
        } // if
        else {
            
            const vector<InvertedIndexCaption>* captions_ptr = &result->second.captions;
            
            int captions_size = captions_ptr->size();

            for (int k = 0; k < captions_size; ++k) {
                unsigned docId;

                docId = captions_ptr->at(k).docId;
                cout << "  Found in docId: " << docId << endl;
                cout << "  captions.txt, Line " << docId + 1 << endl;
                
                ++word_appearances_in_doc.at(docId);
                cout << "  Incremented appearances for docId " << docId << " to " << word_appearances_in_doc.at(docId);
                cout << endl << endl;
            } // for
        } // else
    } // for

    vector<unsigned int> doc_list;
    
    for (unsigned j = 0; j < numDocs; ++j) {
        if (word_appearances_in_doc.at(j) == num_words) {
            cout << "Found a hit for docID " << j << "." << endl;
            cout << "  captions.txt, Line " << j + 1 << endl;
            doc_list.push_back(j);
        } // if
    } // for
    
    return doc_list;
} // buildDocList_server

//                   FUNCTIONS FOR USING THE INVERTED INDEX FILE
double getIDF_server(const string& word) {
    return invertedIndexFile[word].idf;
}

//INPUT: a word and a doc id
//OUTPUT: the tf of that word within that doc
double getTF_server(const string& word, unsigned int docID) {
    for (InvertedIndexCaption indexDocID: invertedIndexFile[word].captions) {
        if (indexDocID.docId == docID) {
            return indexDocID.occurrencesInDoc;
        }
    }
    cout << "this should never ever happen" << endl;
    return -1;
}

//INPUT: a word, and vector of words
//OUTPUT: the tf of that word within the vector
double getTF_server(const string& word, vector<string> vectorOfWords) {
    unsigned int count = 0;
    for (string wordd: vectorOfWords) {
        if (wordd.compare(word) == 0) {
            count++;
        }
    }
    return count;
}

double getNormalizationFactor_server(const string&word, unsigned int docID) {
    for (InvertedIndexCaption indexDocID: invertedIndexFile[word].captions) {
        if (indexDocID.docId == docID) {
            return indexDocID.normalizationFactor;
        }
    }
    cout << "this should never happen" << endl;
    return -1;
}

bool compareDocsBySimScore_server(const Query_hit& first, const Query_hit& second) {
    return (first.score > second.score);
}
//END TFIDF_CALC.h

// Load index data from the file of the given name.
void Index_server::init(ifstream& infile)
{
    // Fill in this method to load the inverted index from disk.
	// Check filestream open
	if (!infile.is_open()) {
		cerr << "Error. Filestream not open" << endl;
		return;
	}
	
	string file_input;
	
	while(getline(infile, file_input)) {
		InvertedIndexRow row;
		
		std::istringstream iss(file_input);
		
		// Get word
		iss >> row.word;
		
		// Get idf
		iss >> row.idf;
		
		// Get total # occurrences
		iss >> row.occurrences;
		
		int counter = 0;
		while (counter < row.occurrences) {
			InvertedIndexCaption cap;
			
			// Get docId
			iss >> cap.docId;
			
			// Get occurrencesInDoc
			iss >> cap.occurrencesInDoc;
			
			// Get normalizationFactor
			iss >> cap.normalizationFactor;
			
			row.captions.push_back(cap);
			
			counter += cap.occurrencesInDoc;
		}
		
		// Put InvertedIndexRow into TFIDF_CALC map
		addInvertedIndexRowToFile_server(row, row.word);
	}
    // cout << "TEST PURPOSES ONLY" << endl << "about to call process_query" << endl;
    // std::vector<Query_hit> v;
    // process_query("roll sushi", v);
}

// Search the index for documents matching the query. The results are to be
// placed in the supplied "hits" vector, which is guaranteed to be empty when
// this method is called.
void Index_server::process_query(const string& query, vector<Query_hit>& hits)
{
    cout << "| ========== PROCESSING QUERY: " << query << " ========== |" << endl;
    //put query into a vector of words
    vector<string> vectorOfWords = splitUpWords_server(query);

    cout << endl << "Successfully split up words:" << endl;
    cout << "  ";
    for (unsigned i = 0; i < vectorOfWords.size(); ++i) {
        cout << vectorOfWords[i] << " ";
    }
    cout << endl;
    //get all docs that contain ALL words from query
    vector<unsigned int> docVector = buildDocList_server(vectorOfWords);
    cout << endl << "Finished building docList. Printing docVector values:" << endl;
    cout << "  ";
    for (unsigned i = 0; i < docVector.size(); ++i) {
        cout << docVector[i] << " ";
    }
    cout << endl;

    // a list of tuples. Each tuple is <docID, simScore>
    //list<tuple<unsigned int, double>> listOfDocSimScores;

    //for each doc, calculate sim(doc, query)
    for (unsigned int doc : docVector ) {
        cout << endl << "Calculating sim(doc, query) for docId " << doc << "." << endl;
        double numerator = 0;
        double leftDenominator = 0;
        double rightDenominator = 0;
        //go through each word in query
        for (string word: vectorOfWords) {
            double idf = getIDF_server(word);
            double weightOfWordInQuery = getTF_server(word, vectorOfWords) * idf;
            double weightOfWordInCaption = getTF_server(word, doc) * idf;
            numerator += (weightOfWordInQuery * weightOfWordInCaption);

            leftDenominator += (weightOfWordInCaption * weightOfWordInCaption);
            rightDenominator += getNormalizationFactor_server(word, doc);
        } 
        double sqrtLeftDenominator = sqrt(leftDenominator);
        double sqrtRightDenominator = sqrt(rightDenominator);
        double finalDenominator = sqrtLeftDenominator + sqrtRightDenominator;

        double simScore = numerator / finalDenominator;

        //push into vector
        string docID_as_string = std::to_string(doc);
        char * docID_as_cstr = new char[docID_as_string.length() + 1];
        strcpy(docID_as_cstr, docID_as_string.c_str());

        Query_hit queryHit(docID_as_cstr, simScore);
        cout << "  Finished calculating query hit for docId " << doc << "." << endl;
        cout << "  Query_hit id:    " << queryHit.id << endl;
        cout << "  Query_hit score: " << queryHit.score << endl;
        cout << endl;
        hits.push_back(queryHit);
    }

    //sort docs by sim (use vector sort, make my own comparator, comparing sim score)
    std::sort(hits.begin(), hits.end(), compareDocsBySimScore_server);
    cout << "Sorted vector. Printing new doc order:" << endl;
    cout << "  ";
    for (unsigned i = 0; i < hits.size(); ++i) {
        cout << hits[i].id << " ";
    }
    cout << endl;
    
}

















// STAHP SCROLL BACK UP /////////////////////////////////////////////////////////////////////////////
// DON'T TOUCH ANYTHING BELOW THIS //////////////////////////////////////////////////////////////////
















namespace {
    // DO NOT MODIFY vvvvvv
    #ifndef UNIT_TEST
    int handle_request(mg_connection *conn)
    {
        const mg_request_info *request_info = mg_get_request_info(conn);

        if (!strcmp(request_info->request_method, "GET") && request_info->query_string) {
            // Make the processing of each server request mutually exclusive with
            // processing of other requests.

            // Retrieve the request form data here and use it to call search(). Then
            // pass the result of search() to to_json()... then pass the resulting string
            // to mg_printf.
            string query;
            if (get_param(request_info, "q", query) == -1) {
                // If the request doesn't have the "q" field, this is not an index
                // query, so ignore it.
                return 1;
            }

            vector<Query_hit> hits;
            Index_server *server = static_cast<Index_server *>(request_info->user_data);

            pthread_mutex_lock(&mutex);
            server->process_query(query, hits);
            pthread_mutex_unlock(&mutex);

            string response_data = to_json(hits);
            int response_size = response_data.length();

            // Send HTTP reply to the client.
            mg_printf(conn,
                      "HTTP/1.1 200 OK\r\n"
                      "Content-Type: application/json\r\n"
                      "Content-Length: %d\r\n"
                      "\r\n"
                      "%s", response_size, response_data.c_str());
        }

        // Returning non-zero tells mongoose that our function has replied to
        // the client, and mongoose should not send client any more data.
        return 1;
    }

    int get_param(const mg_request_info *request_info, const char *name, string& param)
    {
        const char *get_params = request_info->query_string;
        size_t params_size = strlen(get_params);

        // On the off chance that operator new isn't thread-safe.
        pthread_mutex_lock(&mutex);
        char *param_buf = new char[params_size + 1];
        pthread_mutex_unlock(&mutex);

        param_buf[params_size] = '\0';
        int param_length = mg_get_var(get_params, params_size, name, param_buf, params_size);
        if (param_length < 0) {
            return param_length;
        }

        // Probably not necessary, just a precaution.
        param = param_buf;
        delete[] param_buf;

        return 0;
    }
    #endif
    // DO NOT MODIFY ^^^^^^

    // Converts the supplied query hit list into a JSON string.
    string to_json(const vector<Query_hit>& hits)
    {
        ostringstream os;
        os << "{\"hits\":[";
        vector<Query_hit>::const_iterator viter;
        for (viter = hits.begin(); viter != hits.end(); ++viter) {
            if (viter != hits.begin()) {
                os << ",";
            }

            os << *viter;
        }
        os << "]}";

        return os.str();
    }

    // Outputs the computed information for a query hit in a JSON format.
    ostream& operator<< (ostream& os, const Query_hit& hit)
    {
        os << "{" << "\"id\":\"";
        int id_size = strlen(hit.id);
        for (int i = 0; i < id_size; i++) {
            if (hit.id[i] == '"') {
                os << "\\";
            }
            os << hit.id[i];
        }
        return os << "\"," << "\"score\":" << hit.score << "}";
    }
}
