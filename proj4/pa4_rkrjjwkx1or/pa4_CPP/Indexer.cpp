#include "Indexer.h"

#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>
#include <map>
#include <tuple>
#include <iomanip>
#include <cmath>
#include <algorithm>



using namespace std;
using std::ifstream;
using std::ostream;

//COPIED FROM TFIDF_CALC.h
void transformToLowerCase(string& input) {
	transform(input.begin(), input.end(), input.begin(), ::tolower);
}

void removeNonAlphaNumeric(string& input) {
	for (unsigned int i = 0; i < input.length(); i++) {
		if (!isalnum(input[i]) && input[i] != ' ') {
			input.erase(i, 1);
			i--;
		}
	}
}

void removeStopWords(vector<string>& input_words) {
	// Open stopwords.txt
	ifstream stopwords("stopwords.txt");

	// bool strands = false;
	// if (input_words[0] == "1950s") // DEBUG (checking for strands caption)
	// 	strands = true;

	if (stopwords.is_open()) {

		// For each word in stopwords.txt,
		// if input_words is one of those words, remove that word
		string word;
		while(getline(stopwords, word)) {
			removeNonAlphaNumeric(word);
			bool needToCheckForStopWord = true;
			while (needToCheckForStopWord) {
				for (auto it = input_words.begin(); it != input_words.end(); it++) {

					// if (strands) { // DEBUG
					// 	cout << "Comparing word: " << *it << endl;
					// 	cout << "  word: " << word << endl;
					// }

					if (word == *it) {

						// if (strands) { // DEBUG
						// 	cout << "  Removing word: " << *it << endl;
						// 	cout << "  Restarting loop." << endl;
						// }

						input_words.erase(it);
						it = input_words.begin(); // Check input_words again in case of doubles
					}
				}
				needToCheckForStopWord = false;
			}
		}
	}
	// if (strands) { // DEBUG
	// 	cout << "Removed stopwords from caption. Caption is now: " << endl;
	// 	cout << " ";
	// 	for (unsigned i = 0; i < input_words.size(); ++i) {
	// 		cout << " " << input_words[i];
	// 	}
	// 	cout << endl << endl;
	// }
}

// Format query appropriately and split up words.
// Return a vector of each word in doc.
vector<string> splitUpWords(string doc) {
	transformToLowerCase(doc);
	removeNonAlphaNumeric(doc);
	// Split string by spaces, push into vector
	vector<string> words;
	string word;
	istringstream iss(doc);
	while (iss >> word) {
		words.push_back(word);
	}
	removeStopWords(words);
	return words;
}



//END TFIDF_CALC.h



// Reads content from the supplied input file stream, and transforms the
// content into the actual on-disk inverted index file.
void Indexer::index(istream& content, ostream& outfile)
{
    // Fill in this method to parse the content and build your
    // inverted index file.

    // map from word to (map from docID to occurencesInThatDoc)
    // Each word in allWords has its own map.
    // Those maps denote which docIDs that word appears in and how often.
    std::map<string,map<unsigned int, unsigned int>> allWords;

    // map from docID to words in that doc
    map<unsigned int, vector<string>> allDocs;


	//STEP 1 LOOP through each caption from captions.txt
	std::string line;
	unsigned int currentDocID = 0;
	while (std::getline(content, line)) {
		currentDocID++;
		// cout << "virgin line is " << line << endl;

	  	//STEP 2 make that string into a vector of workable words
		vector<string> words = splitUpWords(line);
		allDocs[currentDocID] = splitUpWords(line);

		// Print out list of words to verify
		// cout << "   new line is ";
		
	 	//STEP 3 for each word in the caption:
		for (string word : words ) {	  		
	  		//if word is not already in the map, create map for that word
			if (allWords.find(word) == allWords.end()) {
				//allWords[word] = map<unsigned int, unsigned int> docIDsAndOccurences;
				allWords[word][currentDocID] = 1;
				//cout << "adding word \"" << word << "\" to map, in doc " <<
				 //currentDocID << ", with count " << allWords[word][currentDocID] << "\n\n";
			} 
			//if word is already in the map
			else {
				//if word is not already in this document, set count to 1
				if (allWords[word].find(currentDocID) == allWords[word].end()) {
					allWords[word][currentDocID] = 1;
				}
				//if word was already found in this document, increase it's count
				else {
					allWords[word][currentDocID]++;
				}
				
			}
			//cout << "word "<<word<< " in doc "<< currentDocID<< " is now at count " << allWords[word][currentDocID] << endl;
		}
	}
	//END LOOP

	//STEP 4 go through all words in our map
	map<string,map<unsigned int, unsigned int>>::iterator it;
	map<unsigned int, unsigned int>::iterator it2;
	double numberOfCaptions = currentDocID;

	for ( it = allWords.begin(); it != allWords.end(); it++ ) {

		// bool strands = false;
		// if (it->first == "strands") // DEBUG (checking for strands caption)
		// 	strands = true;

		// if (strands) // DEBUG
		// 	cout << it->first << endl;

	    //STEP 5 do math on them
	    //5.a. get idf
	    double numberOfCaptionsThatContainTheWord = allWords[it->first].size();
	   	double idf = log10(numberOfCaptions / numberOfCaptionsThatContainTheWord);
	   	// if (it->first.compare("jet") == 0) {
	    // 	cout << "number of captions: " << numberOfCaptions << endl;
	    // 	cout << "appearances: " << numberOfCaptionsThatContainTheWord << endl;
	    // }

	   	//5.b. get total number of occurences for this word
	   	unsigned int numberOfOccurencesForThisWord = 0;
	   	for (it2 = allWords[it->first].begin(); it2 != allWords[it->first].end(); it2++) {
	   		numberOfOccurencesForThisWord += allWords[it->first][it2->first];
	   	}
	   	//cout << "numberOfOccurencesForThisWord "<<it->first<< " is " << numberOfOccurencesForThisWord << endl;

	   	//5.c. make a vector of 3-tuples, representing packs of (Doc_id, number of occurrences in Doc_id, Doc_id's normalization factor (before sqrt))
		vector<tuple<unsigned int, unsigned int, double>>docInfo;
		
		//loop through each doc containing current word
		for (it2 = allWords[it->first].begin(); it2 != allWords[it->first].end(); it2++) {

			double preSquareRootNormalization = 0;

			//loop through each word in that caption
			for (unsigned i = 0; i < allDocs[it2->first].size(); ++i) {
				string word = allDocs[it2->first][i];

				// If this word appeared earlier, skip it.
				bool foundDuplicate = false;
				for (unsigned j = 0; j < i; ++j)
					if (allDocs[it2->first][j] == word)
						foundDuplicate = true;

				if (foundDuplicate)
					continue;


				// if (strands) { // DEBUG
				// 	cout << "Calculating tf2idf2 for word: " << word << endl;
				// }

				//cout << "looking at word " << word << " in doc " << it2->first << endl;
				//calculate tf^2 * idf^2 of this term
				double normal_tf = allWords[word][it2->first];
				double normal_idf = log10(numberOfCaptions / allWords[word].size());
				double tf2Idf2 = normal_tf * normal_tf * normal_idf * normal_idf;

				//add it to our sum of all tf2idf2s
				preSquareRootNormalization += tf2Idf2;

				// if (strands) { // DEBUG
				// 	cout << "  normal_tf:  " << normal_tf << endl;
				// 	cout << "  normal_idf:  " << normal_idf << endl;
				// 	cout << "  tf2Idf2:      " << tf2Idf2 << endl;
				// 	cout << "  norm so far:   " << preSquareRootNormalization << endl;
				// }
			}
			// tuple
			docInfo.push_back(make_tuple(it2->first, allWords[it->first][it2->first], preSquareRootNormalization));
		}

		//STEP 6 write that math to outputfile
		outfile << it->first << " " << idf << setprecision(16) << " " << numberOfOccurencesForThisWord;
		outfile.flush();
		for (tuple<unsigned int, unsigned int, double> t: docInfo) {
			outfile << " " << get<0>(t) << " " << get<1>(t) << " " << get<2>(t) << setprecision(16);
			outfile.flush();
		}
		outfile << endl;
		//(docInfo);
	}
}



