#include <iostream>
#include <string>
#include <fstream>
#include <vector>
#include <sstream>
#include <algorithm>
#include <iterator>
#include <map>
#include <ctime>
#include <iomanip>

#define NDEBUG // Uncomment this line before the autograder runs.
#include <cassert>

using namespace std;

//////////////////////////////////////////////////////////////////////////////////////////
// Structs
//////////////////////////////////////////////////////////////////////////////////////////

enum END_CONDITION_PAGERANK { iterations, convergence };

// This is the format for one configuration (3rd line and onwards).
// See page 4 of spec
struct CONFIG_PAGERANK {
	CONFIG_PAGERANK() : numIterations(0), convergenceValue(0) {}

	double dValue;

	END_CONDITION_PAGERANK condition;
	int numIterations;
	double convergenceValue;

	string outputFilename;
};

struct CONFIG_PAGERANK_FILE {
	string inputFilename;
	int numConfigurations;
	vector<CONFIG_PAGERANK> configurations;
};


// Struct to represent a node in a graph.
struct Node_Pagerank {
	Node_Pagerank() {}

	Node_Pagerank(int id_input, string label_input)
		: id(id_input), label(label_input), isSinkNode(false),
		  numOutgoingLinks(0) { }

	int id;
	string label;
	bool isSinkNode;

	// We need two pageranks in order to make sure all pages are
	// pulling from the same iteration of calculated pageranks
	double previousPagerank;
	double currentPagerank;

	double numOutgoingLinks;
	vector<int> outgoingLinks;
};

struct Pagerank_Output {
	int id;
	double pagerank;
};

//////////////////////////////////////////////////////////////////////////////////////////
// Functions
//////////////////////////////////////////////////////////////////////////////////////////

// Splits a string into a vector.
vector<string> splitString_Pagerank(string sentence) {
	// Copy pasted from:
	// http://stackoverflow.com/questions/236129/split-a-string-in-c
	istringstream iss(sentence);
	vector<string> tokens;
	copy(istream_iterator<string>(iss),
		istream_iterator<string>(),
		back_inserter(tokens));

	return tokens;
}

// REQUIRES: line is a "configuration" (3rd line and onwards)
// Parses a line in the config file and returns a
// CONFIG_PAGERANK struct according to that "configuration"
CONFIG_PAGERANK parseConfigLine_Pagerank(string line) {

	CONFIG_PAGERANK configPagerank;

	vector<string> tokens = splitString_Pagerank(line);
	for (int i = 0; i < tokens.size(); ++i) {
		string val = tokens[i];

		switch(i) {

		case 0: // d-value
			configPagerank.dValue = stod(val);
			break;

		case 1: // Iterations or convergence
			if (val == "k")
				configPagerank.condition = iterations;
			else if (val == "c")
				configPagerank.condition = convergence;
			else {
				cerr << "ERROR: Incorrect condition variable." << endl;
				cerr << "  " << line << endl;
				exit(EXIT_FAILURE);
			}
			break;

		case 2: // Number of iterations or threshold of convergence
			if (configPagerank.condition == iterations)
				configPagerank.numIterations = stoi(val);
			else
				configPagerank.convergenceValue = stod(val);
			break;

		default: // Output file
			configPagerank.outputFilename = val;
			break;

		}
	}

	return configPagerank;
}

void setUpConfigStruct_Pagerank(char* configInput, CONFIG_PAGERANK_FILE& configFilePagerank) {
	
	fstream configFile;
	configFile.open(configInput);

	if (configFile.good()) {
		string line;
		int lineNum = 0;
		while(getline(configFile, line)) {
			switch (lineNum) {

			case 0: // inputFilename
				configFilePagerank.inputFilename = line;
				break;

			case 1: // numConfigurations
				configFilePagerank.numConfigurations = stoi(line);
				break;

			default: // Fill in configurations vector
				configFilePagerank.configurations.push_back(parseConfigLine_Pagerank(line));
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
}

// Makes a link from the source to the target.
// Increments the number of links correctly.
void addLink(Node_Pagerank& source, Node_Pagerank& target) {
	source.outgoingLinks.push_back(target.id);
	source.numOutgoingLinks++;
}

// Load input file into memory.
void loadInputFile_Pagerank(map<int, Node_Pagerank>& graph, string inputFilename, int& numV) {

	fstream inputFile;
	inputFile.open(inputFilename);
	if (!inputFile.good()) {
		cerr << "ERROR: Could not open input file \"";
		cerr << inputFilename << "\"" << endl;
		exit(EXIT_FAILURE);
	}

	string line;
	bool inVertices = true;
	while(getline(inputFile, line)) {
		if (line[0] == '*') {
			if (line[1] == 'V' || line[1] == 'v') {
				vector<string> verticesLine = splitString_Pagerank(line);
				numV = stoi(verticesLine[1]);
			}
			else {
				inVertices = false;
				vector<string> arcsLine = splitString_Pagerank(line);
			}
		}
		else {
			if (inVertices) {
				// Split up lines and add them as vertices
				vector<string> tokens = splitString_Pagerank(line);
				int currentNodeId = stoi(tokens[0]);
				graph[currentNodeId] = Node_Pagerank(currentNodeId, tokens[1]);
			}
			else {
				// Split up lines and add them as arcs
				vector<string> tokens = splitString_Pagerank(line);

				bool validLine = true;

				// Break if:
				// 1. Line is not correct size or is a newline (will segfault regardless)
				// 2. Remove/ignore self edges (see spec page 3)
				if (tokens.size() < 2 || tokens[0] == tokens[1])
					validLine = false;

				if (validLine) {
					int sourceId = stoi(tokens[0]);
					int targetId = stoi(tokens[1]);
					addLink(graph[sourceId], graph[targetId]);
				}
			}
		}
	}

	// Sink Nodes
	// Create "virtual" outgoing links to every other node in graph
	// if a node does not have any outgoing links
	for (auto it = graph.begin(); it != graph.end(); ++it) {
		if (it->second.numOutgoingLinks > 0)
			continue;

		it->second.isSinkNode = true;
	}
}

// Calculate the pagerank of a single node.
void distributePageranks(map<int, Node_Pagerank>& graph, Node_Pagerank& currentNode) {

	// Calculate pagerank to distribute
	double distributedPagerank = currentNode.previousPagerank;

	// If it's a sink node, distribute to all nodes
	if (currentNode.isSinkNode) {
		distributedPagerank /= graph.size() - 1;

		// Distribute to all nodes
		for (auto it = graph.begin(); it != graph.end(); ++it) {
			if (it->first == currentNode.id)
				continue;

			it->second.currentPagerank += distributedPagerank;
		}
	}
	else {
		distributedPagerank /= currentNode.numOutgoingLinks;

		// Distribute to outgoing nodes
		for (int outgoingId : currentNode.outgoingLinks)
			graph[outgoingId].currentPagerank += distributedPagerank;
	}
}

// Resets the pageranks to the initial pageranks.
void resetGraph(map<int, Node_Pagerank>& graph, int numV) {
	for (auto it = graph.begin(); it != graph.end(); ++it) {
		double initialPagerank = 1.0 / numV;
		it->second.previousPagerank = initialPagerank;
		it->second.currentPagerank = initialPagerank;
	}
}

// Makes all current pageranks the previous pageranks.
void advancePagerank(map<int, Node_Pagerank>& graph, double dValue) {
	for (auto it = graph.begin(); it != graph.end(); ++it) {
		it->second.previousPagerank = it->second.currentPagerank;
		it->second.currentPagerank = 0.0;
	}
}

// Checks if there are remaining iterations left to perform in the algorithm.
// ALWAYS Returns false if end condition is not iterations.
// Else,
//   Returns true if there are remaining iterations.
//   Returns false if no more remaining iterations.
bool remainingIterations(int iterationsLeft, const CONFIG_PAGERANK& config) {
	if (config.condition != iterations)
		return false;

	return iterationsLeft > 0;
}

// Checks if every node changed no more than the convergenceValue.
// ALWAYS Returns false if end condition is not convergence.
// Else,
//   Returns true if above threshold. (not converged enough => keep iterating)
//   Returns false if within threshold.
bool aboveConvergenceThreshold(map<int, Node_Pagerank>& graph, const CONFIG_PAGERANK& config) {
	if (config.condition != convergence)
		return false;

	bool allNodesWithinThreshold = true;
	for (auto it = graph.begin(); it != graph.end(); ++it) {
		double difference = it->second.currentPagerank - it->second.previousPagerank;
		if (difference < 0)
			difference = it->second.previousPagerank - it->second.currentPagerank;

		double currentConvergence = difference / it->second.previousPagerank;
		allNodesWithinThreshold = currentConvergence <= config.convergenceValue;
	}

	return !allNodesWithinThreshold;
}

// Comparator function for sorting the pageranks
bool comparePageranks(const Pagerank_Output& first, const Pagerank_Output& second) {
    return first.pagerank > second.pagerank;
}

// Writes all pageranks to output filename.
void writeToOutput(map<int, Node_Pagerank>& graph, const CONFIG_PAGERANK& config) {
	fstream outputFile;
	outputFile.open(config.outputFilename, fstream::out);
	if (!outputFile.good()) {
		cerr << "ERROR: Could not open output file \"";
		cerr << config.outputFilename << "\"" << endl;
		exit(EXIT_FAILURE);
	}

	vector<Pagerank_Output> pageranks;

	// Add all pageranks to a vector
	for (auto it = graph.begin(); it != graph.end(); ++it) {
		Pagerank_Output currentDoc;

		currentDoc.id = it->second.id;
		currentDoc.pagerank = it->second.currentPagerank;

		pageranks.push_back(currentDoc);
	}

	// Sort the vector by pagerank (decreasing order)
	sort(pageranks.begin(), pageranks.end(), comparePageranks);

	// Output all pageranks as:
	// id,pagerank
	for (auto it = pageranks.begin(); it != pageranks.end(); ++it)
		outputFile << it->id << ',' << fixed << setprecision(6) <<  it->pagerank << endl;

	outputFile.close();
}

void processClockedTime(clock_t startTime, string process) {
	clock_t endTime = clock();
	if (startTime > endTime)
		swap(startTime, endTime);
	double secondsPassed = (endTime - startTime) / CLOCKS_PER_SEC;

	cout << endl << "Process: " << process << endl;
	cout         << "   Time: " << fixed << setprecision(2) << secondsPassed << " s" << endl;
}


//////////////////////////////////////////////////////////////////////////////////////////
// Main Function
//////////////////////////////////////////////////////////////////////////////////////////

int main(int argc, char* argv[]) {

	CONFIG_PAGERANK_FILE configPagerankFile;
	setUpConfigStruct_Pagerank(argv[1], configPagerankFile);

	// TODO: Setup for loop to go through each configuration

	// The main data structure that holds the graph is a hashmap of Nodes.
	// key = id
	// value = Node_Pagerank struct
	map<int, Node_Pagerank> graph;
	int numVertices = 0;

	clock_t startTime = clock();

	// Load input file into memory
	loadInputFile_Pagerank(graph, configPagerankFile.inputFilename, numVertices);

	processClockedTime(startTime, "Loading into memory");

	for (int i = 0; i < configPagerankFile.configurations.size(); ++i) {
		CONFIG_PAGERANK currentConfig = configPagerankFile.configurations[i];

		// Initialize all nodes to 1 / N
		resetGraph(graph, numVertices);

		clock_t configurationStartTime = clock();

		// Start iterating
		int numIterations = currentConfig.numIterations;
		do {
			// 1st Pass
			// Previous pagerank = current pagerank
			advancePagerank(graph, currentConfig.dValue);

			// 2nd Pass
			// For all nodes, distribute the pagerank
			for (auto it = graph.begin(); it != graph.end(); ++it)
				distributePageranks(graph, it->second);

			// 3rd Pass
			// Multiply all nodes' pageranks by dValue and add the random surfer's contributions
			for (auto it = graph.begin(); it != graph.end(); ++it) {
				it->second.currentPagerank *= currentConfig.dValue;
				it->second.currentPagerank += (1.0 - currentConfig.dValue) / graph.size();
			}

			// Decrease numIterations (doesn't matter how low it gets)
			numIterations--;
		} while (remainingIterations(numIterations, currentConfig) || aboveConvergenceThreshold(graph, currentConfig));

		processClockedTime(configurationStartTime, "Configuration " + to_string(i));

		// After the iteration step, output all pageranks to the output file
		writeToOutput(graph, currentConfig);
	}

	processClockedTime(startTime, "Total");



	// Assert statements (these work with pagerank_code/pagerank.net)
	// assert(numVertices == 362);
	// assert(numArcs == 3433);
	// assert(graph[19908980].id == 19908980);
	// assert(graph[19908980].label == "\"List_of_Presidents_of_the_United_States\"");
	// assert(graph[19908980].outgoingLinks[0] == 307);
	// assert(graph[19908980].outgoingLinks[1] == 3356);
	// assert(graph[19908980].outgoingLinks[20] == 20082093);
	// assert(graph[20082093].incomingLinks[7] == 19908980);
	// assert(graph[18110].incomingLinks[0] == 534366);
}