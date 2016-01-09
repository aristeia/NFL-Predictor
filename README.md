# NFL-Predictor

## By Jon Sims and Ray Hermosillo-Torres

This app uses NFL game data (from [devstopfix's](/devstopfix/) [nfl_results repo](/devstopfix/nfl_results)) and NFL team statistics (scraped from [the nfl's official website](www.nfl.com)) as input data for machine learning algorithms. The two algorithms we include code for are the Multinomial Naive Bayes classifier and an Artificial Neural Net (not fully working).

scrapeNFL.py is the file performing scraping from the NFL's website, requiring the python libraries scipy, Levenshtein, and requests. Works with python3. Saves its results to nfl.json (we've included our nfl.json file for data back to 1995 as an example).

nfl.json contains the output from scrapeNFL.py in json format. It contains the following types of data:
* teams: a dictionary mapping team name abbreviations and alternate spellings to the true team name (including city). Examples: {"KC": "Kansas", "GB": "Green Bay", "Chargers": "San Diego Chargers", "Patriots": "New England Patriots", "Lions": "Detroit Lions", "49ers": "San Francisco 49ers",...}
* data: team data per year per the statistics available on nfl.com
* data_dims: number of statistics available per team (for use in an ANN)
* exact_data: game results parsed from from [devstopfix's](/devstopfix/) [nfl_results repo](/devstopfix/nfl_results), with score differences being normally-distributed and replaced by their [CDF on that normal distribution](https://en.wikipedia.org/wiki/Normal_distribution#/media/File:Normal_Distribution_CDF.svg) times two, subtracted from one. This way, the result is a [-1,1] value representing a loss/win by parity and by how much they won/loss using the CDF. This type of result works especially well with Multinomial Naive Bayes classifiers as a classification. The point difference is done as the difference between the first (home) and the second (away) team in the list. Examples: {2009: ["Pittsburgh Steelers", "Tennessee Titans", 0.021146882854667925], ["Cincinnati Bengals", "Denver Broncos", -0.37996400161768973], ["Cleveland Browns", "Minnesota Vikings", -0.7213662952824762],...}
* exact_metadata:
  * mean: mean point difference in games. Example: 2.594 (home teams win by that much in our data, on average, from 1995)
  * stdev: standard deviation of point difference in games. Example: 15.316 (home teams win with a stdev of that much in our data, on average, from 1995)

tester.py tests the data from nfl.json on the machine learning algorithms, requiring numpy and running on python3. It takes two optional command line arguments:
* --ann: Test on the artificial neural network (requires Tensorflow)
* --mnb: Test on the Multinomial Naive Bayes classifier (requires sklearn and nltk)
See result.out for the outfile from a run on our test data with the --mnb parameter