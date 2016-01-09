import io, json, numpy as np, sys
from random import shuffle
from statistics import mean, pstdev


with io.open("nfl.json",'r',encoding='utf8') as dataFile:
  fdata = json.load(dataFile, object_hook=dict, parse_float=float, parse_int=int)

print("Loaded data from nfl.json")
teams = fdata["teams"]
exact_data = fdata["exact_data"]
score_mean = fdata['exact_metadata']['mean']
score_stdev = fdata['exact_metadata']['stdev']
data = fdata['data']
dim = fdata['data_dims'] if 'data_dims' in fdata else 708
print("Parsed data from nfl.json")


def word_feats(words_vals):
  return dict([(word, val) for word,val in words_vals]) #word, val is feature, level


def getTeamFeats(team, season, pref = ''):
  return [ ((pref+'_'+cat.replace("StatisticCategory","")+'_'+subcat+"_"+stat).replace(' ','_'),stats[i]) 
    for cat, cats in data[season].items() 
    for subcat, subcats in cats.items() 
    if "Team" in subcats
    for i in range(len(subcats["Team"])) 
    if team == subcats["Team"][i] 
    for stat,stats in subcats.items()
    if stat != 'Team']

def neuralNet():
  import tensorflow as tf
  def tensor_feats(words_vals):
    return np.array([val for word,val in words_vals]) #word, val is feature, level

  def init_weights(shape):
    return tf.Variable(tf.random_normal(shape, stddev=0.01))

  config = tf.ConfigProto()
  config.gpu_options.allocator_type = 'BFC'
  
  feats = [(tensor_feats(
       getTeamFeats(game[0], season, "home") + getTeamFeats(game[1], season, "away") 
      ), game[2]) 
    for season, games in exact_data.items() 
    for game in games if season in data]

  shuffle(feats)

  trX, trY, teX, teY = ([x for x,y in feats[:int(len(feats)*0.95)]],
  [y for x,y in feats[:int(len(feats)*0.95)]], 
  [x for x,y in feats[int(len(feats)*0.95):]], 
  [y for x,y in feats[int(len(feats)*0.95):]])

  x = tf.placeholder(tf.float32, [None, dim])
  W = tf.Variable(tf.zeros([dim,1]))

  y = (1 / (1 + tf.log(-(tf.matmul(x, W)))))


  y_ = tf.placeholder(tf.float32, [None, 1])

  sigmoid_error = -tf.reduce_sum((y_ - y) * x * y * (1-y))

  train_step = tf.train.GradientDescentOptimizer(0.01).minimize(sigmoid_error)

  init = tf.initialize_all_variables()

  sess = tf.Session()
  sess.run(init)
  # tf.train.start_queue_runners(sess=sess)
  for i in range(1000):
      sess.run(train_step, feed_dict={x: trX, y_: trY})
      print(i, np.mean(np.argmax(teY, axis=1) ==
                     sess.run(predict_op, feed_dict={x: teX, y_: teY})))


  correct_prediction = tf.equal(tf.argmax(y,1), tf.argmax(y_,1))
  accuracy = tf.reduce_mean(tf.cast(correct_prediction, "float"))

  a = sess.run(accuracy, feed_dict={x: trX, y:trY})
  print("accuracy:",a)


def naiveBayes():
  from sklearn.naive_bayes import MultinomialNB
  from sklearn.pipeline import Pipeline
  from nltk.classify import SklearnClassifier
  from sklearn.feature_extraction.text import TfidfTransformer
  from sklearn.feature_selection import SelectKBest, chi2

  feats = [(word_feats(
     getTeamFeats(game[0], season, "home") + getTeamFeats(game[1], season, "away") 
    ), game[2]) 
  for season, games in exact_data.items() 
  if int(season) >= 2005
  for game in games if season in data]
  shuffle(feats)

  training, testing = feats[:int(len(feats)*0.75)], feats[int(len(feats)*0.75):]

  pipeline = Pipeline([('tfidf', TfidfTransformer()),
    #('chi2', SelectKBest(chi2, k=250)),  
    ('nb', MultinomialNB())])

  classifier = SklearnClassifier(pipeline).train(training)
  
  accuracy = 0
  for t in testing:
    classification = classifier.classify(t[0])
    accuracy += int((t[1] > 0) == (classification > 0)) / float(len(testing))

  print("Training on 75% and testing on 25% of the data at random, the algorithm is "+str(round(accuracy*100,4))+"% accurate")

  accuracy = 0.0
  i=0
  print("Performing leave-one-out cross-validation")
  for game in feats:
    training = [x for x in feats if x!=game]

    pipeline = Pipeline([('tfidf', TfidfTransformer()),
      #('chi2', SelectKBest(chi2, k=250)),  
      ('nb', MultinomialNB())])

    classifier = SklearnClassifier(pipeline).train(training)

    rw = []
    classification = classifier.classify(game[0])
    accuracy += int((game[1] > 0) == (classification > 0)) / float(len(feats))
    i+=1
    if i%5==0:
      print("After "+str(i)+" games, accuracy is at "+str(round(accuracy*float(len(feats))*100 / i,4))+'%')
  print("With leave-one-out cross-validation, the algorithm is "+str(round(accuracy*100,4))+"% accurate")

print("Starting machine learning")
if '--ann' in sys.argv:
  print("Doing an Artificial Neural Network")
  neuralNet()

if '--mnb' in sys.argv:
  print("Doing a Multinomial Naive Bayes Classifier")
  naiveBayes()

print("Done")