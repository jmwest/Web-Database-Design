#include <iostream>
#include <iomanip>
#include <string>
#include <fstream>
#include <vector>
#include <sstream>
#include <algorithm>
#include <iterator>
#include <unordered_map>
#include <map>
#include <cmath>

using namespace std;

//////////////////////////////////////////////////////////////////////////////////////////
// Enums
//////////////////////////////////////////////////////////////////////////////////////////

enum END_CONDITION_HITS { iterations, convergence };

//////////////////////////////////////////////////////////////////////////////////////////
// Structs
//////////////////////////////////////////////////////////////////////////////////////////

// This is the format for one configuration (4th line and onwards).
// See page 7 of spec
struct CONFIG_HITS {
	CONFIG_HITS() : numIterations(0), convergenceValue(0) {}

	int hValue;

	END_CONDITION_HITS condition;
	int numIterations;
	double convergenceValue;

	string outputFilename;

	vector<string> query;
};

// This is the file format for entire config.hits file.
// See page 7 of spec
struct CONFIG_HITS_FILE {
	string inputFilename;
	string invertedIndexFilename;
	int numConfigurations;
	vector<CONFIG_HITS> configurations;
};

// Struct to represent a node in a graph.
struct Node_Hits {
	Node_Hits()
	: numOutgoingLinks(0), numIncomingLinks(0) { }
	
	Node_Hits(int id_input, string label_input)
	: id(id_input), label(label_input),
	authorityScore_previous(0.0), authorityScore_current(0.0),
	hubScore_previous(0.0), hubScore_current(0.0),
	numOutgoingLinks(0), numIncomingLinks(0) { }
	
	int id;
	string label;
	
	// Two authority and hub scores
	// for current and previous rounds
	double authorityScore_previous;
	double authorityScore_current;
	double hubScore_previous;
	double hubScore_current;
	
	int numOutgoingLinks;
	vector<int> outgoingLinks;
	
	int numIncomingLinks;
	vector<int> incomingLinks;
};

struct Hits_Output {
	int id;
	double hubScore;
	double authorityScore;
};

//////////////////////////////////////////////////////////////////////////////////////////
// Function Declarations
//////////////////////////////////////////////////////////////////////////////////////////

void load_inverted_index_hits(unordered_map<string, vector<int> > & inverted_index,
							  const string & index_file);

void build_seed_set(vector<int> & seed_set, unordered_map<string, vector<int> > & inverted_index,
						   const vector<string> & query_words, int h);

void grow_base_set(vector<int> & base_set, map<int, Node_Hits>& graph, vector<int> & seed_set);

void initialize_base_set_nodes(map<int, Node_Hits>& graph, vector<int> & base_set);

void reset_nodes(map<int, Node_Hits>& graph);

void update_auth_score(map<int, Node_Hits>& graph, Node_Hits & node);

void update_hub_score(map<int, Node_Hits>& graph, Node_Hits & node);

void update_base_set_scores(map<int, Node_Hits>& graph, vector<int> & base_set);

void normalize_scores_iterations(map<int, Node_Hits>& graph, vector<int> & base_set);

bool normalize_scores_difference(map<int, Node_Hits>& graph, vector<int> & base_set, double diff_val);

void prepare_hits_output(vector<Hits_Output>& output_vec, map<int, Node_Hits>& graph, vector<int> & base_set);

// function passed into sort
bool hits_output_sort(const Hits_Output& first, const Hits_Output& second);

// Splits a string into a vector.
vector<string> splitString_Hits(string sentence);

// REQUIRES: line is a "configuration" (4th line and onwards)
// Parses a line in the config file and returns a
// CONFIG_HITS struct according to that "configuration"
CONFIG_HITS parseConfigLine_Hits(string line);

void setUpConfigStruct_Hits(char* configInput, CONFIG_HITS_FILE& configFileHits);

void addLink_Hits(Node_Hits& source, Node_Hits& target);

void loadInputFile_Hits(map<int, Node_Hits>& graph, string inputFilename, int& numV, int& numA);

//////////////////////////////////////////////////////////////////////////////////////////
//											MAIN										//
//////////////////////////////////////////////////////////////////////////////////////////

int main(int argc, char* argv[]) {

	CONFIG_HITS_FILE configFileHits;
	setUpConfigStruct_Hits(argv[1], configFileHits);
	
	// Load inverted index
	unordered_map<string, vector<int> > inverted_index;
	load_inverted_index_hits(inverted_index, configFileHits.invertedIndexFilename);
	
	// Load graph
	map<int, Node_Hits> graph;
	int numVertices = 0;
	int numArcs = 0;
	loadInputFile_Hits(graph, configFileHits.inputFilename, numVertices, numArcs);
	
	// Iterate through all config commands
	for (int i = 0; i < configFileHits.numConfigurations; ++i) {
		
		CONFIG_HITS current_config = configFileHits.configurations.at(i);

		vector<int> seed;
		build_seed_set(seed, inverted_index, current_config.query, current_config.hValue);

		vector<int> base;
		grow_base_set(base, graph, seed);
		
		initialize_base_set_nodes(graph, base);
		
		if (current_config.condition == iterations) {

			for (int k = 0; k < current_config.numIterations; ++k) {
				update_base_set_scores(graph, base);
				normalize_scores_iterations(graph, base);
			}
		}
		else {

			bool threshold_met = false;
			
			while (!threshold_met) {
				
				update_base_set_scores(graph, base);
				threshold_met = normalize_scores_difference(graph, base, current_config.convergenceValue);
			}
		}
		
		ofstream outfile(current_config.outputFilename);
		if (!outfile.is_open()) {
			cerr << "Error opening output file: " << current_config.outputFilename << endl;
			exit(EXIT_FAILURE);
		}
		
		ostringstream ss;
		
		vector<Hits_Output> hits_output_vector;
		prepare_hits_output(hits_output_vector, graph, base);
		
		for (int a = 0; a < hits_output_vector.size(); ++a) {
			ss << fixed << setprecision(6) << hits_output_vector.at(a).id << "," << hits_output_vector.at(a).hubScore << "," << hits_output_vector.at(a).authorityScore << "\n";
		}
		
		outfile << ss.str();
		
		outfile.close();
		
		reset_nodes(graph);
	}
	
	return 0;
}

//////////////////////////////////////////////////////////////////////////////////////////
// Function Definitions
//////////////////////////////////////////////////////////////////////////////////////////

void load_inverted_index_hits(unordered_map<string, vector<int> > & inverted_index,
							  const string & index_file) {
	
	ifstream infile(index_file);
	if (!infile.is_open()) {
		cerr << "Error opening inverted index file: " << index_file << endl;
		exit(EXIT_FAILURE);
	}
	
	string file_input;
	
	while(getline(infile, file_input)) {
		
		string word;
		int id;
		
		transform(file_input.begin(), file_input.end(), file_input.begin(), ::tolower);
		
		istringstream iss(file_input);
		
		// Get word
		iss >> word;
		
		// Get doc id
		iss >> id;
		
		// Put info into map
		inverted_index[word].push_back(id);
	}
	
	unordered_map<string, vector<int> >::iterator start;
	unordered_map<string, vector<int> >::iterator end = inverted_index.end();
	
	for (start = inverted_index.begin(); start != end; ++start) {
		sort(start->second.begin(), start->second.end());
	}
	
	infile.close();
	
	return;
}

void build_seed_set(vector<int> & seed_set, unordered_map<string, vector<int> > & inverted_index,
						   const vector<string> & query_words, int h) {
	
	if (query_words.size() < 1) {
		return;
	}
	
	int num_words = query_words.size();
	
	vector<int>& current = inverted_index[query_words.at(0)];
	
	if (num_words == 1) {
		seed_set = current;
	}
	
	for (int i = 1; i < num_words; ++i) {
		seed_set.clear();
		vector<int>& next = inverted_index[query_words.at(i)];
		set_intersection(current.begin(), current.end(),
						 next.begin(), next.end(),
						 back_inserter(seed_set));
		
		if (seed_set.empty()) {
			return;
		}
		
		current = seed_set;
	}
	
	if (h < seed_set.size()) {
		seed_set.erase(seed_set.begin() + h, seed_set.end());
	}
	
	return;
}

void grow_base_set(vector<int> & base_set, map<int, Node_Hits>& graph, vector<int> & seed_set) {
	
	base_set = seed_set;

	for (int i = 0; i < seed_set.size(); ++i) {
		
		vector<int> temp1, temp2, temp3;

		Node_Hits& node = graph[seed_set.at(i)];
		
//		vector<int>& in_ref = node.incomingLinks;
//		vector<int>& out_ref = node.outgoingLinks;
		
		// compile all connected nodes together
		set_union(node.incomingLinks.begin(), node.incomingLinks.end(),
				  node.outgoingLinks.begin(), node.outgoingLinks.end(),
				  back_inserter(temp1));
		
		// remove the seed set from compiled list
		set_difference(temp1.begin(), temp1.end(),
					   seed_set.begin(), seed_set.end(),
					   back_inserter(temp2));
		
		// Make the final iterator either .end()
		// or .begin() + 50, depending on size
		auto temp2_end_it = temp2.end();
		 
		if ((temp2.end() - temp2.begin()) > 50) {
			temp2_end_it = temp2.begin() + 50;
		}

		// add first 50 nodes in compiled list to base set
		set_union(temp2.begin(), temp2_end_it,
				  base_set.begin(), base_set.end(),
				  back_inserter(temp3));

		base_set = temp3;
		
//		int counted_links = 0;
//		for (int in_c = 0, out_c = 0; (counted_links < 50) && ((in_c < in_ref.size()) || (out_c < out_ref.size()));) {
//			
//			int temp_int = 0;
//			
//			// Determine which next incoming or outgoing link is smaller
//			// and use that one for currrent round
//			if (in_c < in_ref.size()) {
//				
//				if (out_c < out_ref.size()) {
//					
//					if (in_ref.at(in_c) < out_ref.at(out_c)) {
//						temp_int = in_ref.at(in_c);
//						++in_c;
//					}
//					else {
//						temp_int = out_ref.at(out_c);
//						++out_c;
//					}
//				}
//				else {
//					temp_int = in_ref.at(in_c);
//					++in_c;
//				}
//			}
//			else {
//				temp_int = out_ref.at(out_c);
//				++out_c;
//			}
//			
////			cout << temp_int << endl;
//
//			// Check if current link is already in seed_set.
//			// If so, ignore and go to next iteration.
//			if (!binary_search(seed_set.begin(), seed_set.end(), temp_int)) {
//				++counted_links;
//				
//				if (find(base_set.begin(), base_set.end(), temp_int) == base_set.end()) {
//					
//					base_set.push_back(temp_int);
//				}
//			}
//		}
	}
//
//	sort(base_set.begin(), base_set.end());
	
	return;
}

void initialize_base_set_nodes(map<int, Node_Hits>& graph, vector<int> & base_set) {

	int base_size = base_set.size();
	
	for (int i = 0; i < base_size; ++i) {
		
		graph[base_set.at(i)].authorityScore_previous = 1.0;
		graph[base_set.at(i)].hubScore_previous = 1.0;
	}
	
	return;
}

void reset_nodes(map<int, Node_Hits>& graph) {

	for (auto it = graph.begin(); it != graph.end(); ++it) {
		
		Node_Hits& node = it->second;
		
		node.authorityScore_previous = 0.0;
		node.authorityScore_current = 0.0;
		node.hubScore_previous = 0.0;
		node.hubScore_current = 0.0;
	}
	
	return;
}

void update_auth_score(map<int, Node_Hits>& graph, Node_Hits & node) {

	// set current authority score to 0
	node.authorityScore_current = 0.0;
	
	int num_incoming = node.incomingLinks.size();
	vector<int>& incoming_links_ref = node.incomingLinks;
	
	for (int i = 0; i < num_incoming; ++i) {
		node.authorityScore_current += graph[incoming_links_ref.at(i)].hubScore_previous;
	}
	
	return;
}

void update_hub_score(map<int, Node_Hits>& graph, Node_Hits & node) {

	// set current hub score to 0
	node.hubScore_current = 0;

	int num_outgoing = node.outgoingLinks.size();
	vector<int>& outgoing_links_ref = node.outgoingLinks;

	for (int i = 0; i < num_outgoing; ++i) {
		node.hubScore_current += graph[outgoing_links_ref.at(i)].authorityScore_previous;
	}

	return;
}

void update_base_set_scores(map<int, Node_Hits>& graph, vector<int> & base_set) {

	int base_size = base_set.size();
	
	for (int i = 0; i < base_size; ++i) {
		update_auth_score(graph, graph[base_set.at(i)]);
		update_hub_score(graph, graph[base_set.at(i)]);
	}
	
	return;
}

void normalize_scores_iterations(map<int, Node_Hits>& graph, vector<int> & base_set) {

	double total_auth_score = 0.0;
	double total_hub_score = 0.0;
	
	int base_size = base_set.size();

	for (int i = 0; i < base_size; ++i) {
		
		Node_Hits& node = graph[base_set.at(i)];
		
		total_auth_score += pow(node.authorityScore_current, 2);
		total_hub_score += pow(node.hubScore_current, 2);
	}
	
	total_auth_score = sqrt(total_auth_score);
	total_hub_score = sqrt(total_hub_score);
	
	for (int j = 0; j < base_size; ++j) {
		
		Node_Hits& node = graph[base_set.at(j)];
		
		node.authorityScore_previous = (node.authorityScore_current/total_auth_score);
		node.hubScore_previous = (node.hubScore_current/total_hub_score);
	}
	
	return;
}

bool normalize_scores_difference(map<int, Node_Hits>& graph, vector<int> & base_set, double diff_val) {

	double total_auth_score = 0.0;
	double total_hub_score = 0.0;
	
	int base_size = base_set.size();

	for (int i = 0; i < base_size; ++i) {
		
		Node_Hits& node = graph[base_set.at(i)];
		
		total_auth_score += pow(node.authorityScore_current, 2);
		total_hub_score += pow(node.hubScore_current, 2);
	}
	
	total_auth_score = sqrt(total_auth_score);
	total_hub_score = sqrt(total_hub_score);
	
	bool all_below_threshold = true;
	for (int j = 0; j < base_size; ++j) {
		
		Node_Hits& node = graph[base_set.at(j)];
		
		node.authorityScore_current = (node.authorityScore_current/total_auth_score);
		node.hubScore_current = (node.hubScore_current/total_hub_score);
		
		if (node.authorityScore_current != 0) {
			
			if ( (abs(node.authorityScore_current - node.authorityScore_previous)/node.authorityScore_previous) > diff_val) {
				all_below_threshold = false;
			}
		}
		
		if (node.hubScore_current != 0) {
			
			if ( (abs(node.hubScore_current - node.hubScore_previous)/node.hubScore_previous) > diff_val) {
				all_below_threshold = false;
			}
		}
		
		node.authorityScore_previous = node.authorityScore_current;
		node.hubScore_previous = node.hubScore_current;
	}
	
	return all_below_threshold;
}

void prepare_hits_output(vector<Hits_Output>& output_vec, map<int, Node_Hits>& graph, vector<int> & base_set) {
	
	for (int i = 0; i < base_set.size(); ++i) {
		
		Hits_Output out;
		Node_Hits& node = graph[base_set.at(i)];
		
		out.id = node.id;
		out.hubScore = node.hubScore_previous;
		out.authorityScore = node.authorityScore_previous;
		
		output_vec.push_back(out);
	}

	
	sort(output_vec.begin(), output_vec.end(), hits_output_sort);
	
	return;
}

// function for sorting Hits_Output by hubscore (descending)
bool hits_output_sort(const Hits_Output& first, const Hits_Output& second) {
	
	if (first.hubScore == second.hubScore) {
		return (first.id < second.id);
	}
	else {
		return (first.hubScore > second.hubScore);
	}
}


// Splits a string into a vector.
vector<string> splitString_Hits(string sentence) {
	// Copy pasted from:
	// http://stackoverflow.com/questions/236129/split-a-string-in-c
	istringstream iss(sentence);
	vector<string> tokens;
	copy(istream_iterator<string>(iss),
		 istream_iterator<string>(),
		 back_inserter(tokens));
	
	return tokens;
}

// REQUIRES: line is a "configuration" (4th line and onwards)
// Parses a line in the config file and returns a
// CONFIG_HITS struct according to that "configuration"
CONFIG_HITS parseConfigLine_Hits(string line) {
	
	CONFIG_HITS configHits;
	
	vector<string> tokens = splitString_Hits(line);
	for (int i = 0; i < tokens.size(); ++i) {
		string val = tokens[i];
		
		switch(i) {
				
			case 0: // h-value
				configHits.hValue = stoi(val);
				break;
				
			case 1: // Iterations or convergence
				if (val == "k")
					configHits.condition = iterations;
				else if (val == "c")
					configHits.condition = convergence;
				else {
					cerr << "ERROR: Incorrect condition variable." << endl;
					cerr << "  " << line << endl;
					exit(EXIT_FAILURE);
				}
				break;
				
			case 2: // Number of iterations or threshold of convergence
				if (configHits.condition == iterations)
					configHits.numIterations = stoi(val);
				else
					configHits.convergenceValue = stod(val);
				break;
				
			case 3: // Output file
				configHits.outputFilename = val;
				break;
				
			default: // Rest of the line is the query to process
				configHits.query.push_back(val);
				break;
				
		}
	}
	
	return configHits;
}

void setUpConfigStruct_Hits(char* configInput, CONFIG_HITS_FILE& configFileHits) {
	
	fstream configFile;
	configFile.open(configInput);
	
	if (configFile.good()) {
		string line;
		int lineNum = 0;
		while(getline(configFile, line)) {
			
			transform(line.begin(), line.end(), line.begin(), ::tolower);
			
			switch (lineNum) {
					
				case 0: // inputFilename
					configFileHits.inputFilename = line;
					break;
					
				case 1: // invertedIndexFilename
					configFileHits.invertedIndexFilename = line;
					break;
					
				case 2: // numConfigurations
					configFileHits.numConfigurations = stoi(line);
					break;
					
				default: // Fill in configurations vector
					configFileHits.configurations.push_back(parseConfigLine_Hits(line));
					break;
					
			}
			lineNum++;
		}
		
	}
	else {
		cerr << "ERROR: Could not open config file \"";
		cerr << configInput << "\"" << endl;
		exit(EXIT_FAILURE);
	}
	
	return;
}

// Makes a link from the source to the target.
// Increments the number of links correctly.
void addLink_Hits(Node_Hits& source, Node_Hits& target) {
	
	source.outgoingLinks.push_back(target.id);
	source.numOutgoingLinks++;
	
	target.incomingLinks.push_back(source.id);
	target.numIncomingLinks++;
	
	return;
}

// Load input file into memory.
void loadInputFile_Hits(map<int, Node_Hits>& graph, string inputFilename, int& numV, int& numA) {
	
	ifstream inputFile(inputFilename);
	if (!inputFile.is_open()) {
		cerr << "ERROR: Could not open input file \"";
		cerr << inputFilename << "\"" << endl;
		exit(EXIT_FAILURE);
	}
	
	string line;
	bool inVertices = true;
	while(getline(inputFile, line)) {
		if (line[0] == '*') {
			if (line[1] == 'V' || line[1] == 'v') {
				vector<string> verticesLine = splitString_Hits(line);
				numV = stoi(verticesLine[1]);
			}
			else {
				inVertices = false;
				vector<string> arcsLine = splitString_Hits(line);
				numA = stoi(arcsLine[1]);
			}
		}
		else {
			if (inVertices) {
				// Split up lines and add them as vertices
				vector<string> tokens = splitString_Hits(line);
				int currentNodeId = stoi(tokens[0]);
				graph[currentNodeId] = Node_Hits(currentNodeId, tokens[1]);
			}
			else {
				// Split up lines and add them as arcs
				vector<string> tokens = splitString_Hits(line);
				
				bool validLine = true;
				
				// Break if:
				// 1. Line is not correct size or is a newline (will segfault regardless)
				// 2. Remove/ignore self edges (see spec page 6)
				if (tokens.size() < 2 || tokens[0] == tokens[1])
					validLine = false;
				
				if (validLine) {
					int sourceId = stoi(tokens[0]);
					int targetId = stoi(tokens[1]);
					addLink_Hits(graph[sourceId], graph[targetId]);
				}
			}
		}
	}
	
	// Sort all outgoing and incoming links for later use
	for (auto it3 = graph.begin(); it3 != graph.end(); ++it3) {
		sort(it3->second.outgoingLinks.begin(), it3->second.outgoingLinks.end());
		sort(it3->second.incomingLinks.begin(), it3->second.incomingLinks.end());
	}
	
	return;
}
