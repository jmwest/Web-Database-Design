import json
import operator

results = open("results.json")
results_str = results.read()
results_json = json.loads(results_str)

grade = 0
for test in results_json['autograder_test_case_results']:
	if test['points_awarded'] != test['points_possible']:
		print str(test['points_awarded']), '/', str(test['points_possible']), '  ', str(test['test_case_name'])
	grade += test['points_awarded']
print "Grade:", grade, '/', 100