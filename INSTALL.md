For debian/ubuntu:
  * You can install python3 with:

          sudo apt-get install python3 python3-pip
  * and install required libraries with the following:

          sudo pip3 install numpy
          sudo apt-get install python3-scipy
          sudo pip3 install requests
          sudo pip3 install Levenshtein

  * For the Multinomial Naive Bayes classifier, do:

          sudo pip3 install nltk
          sudo pip3 install sklearn
  * For the Artificial Neural Net, follow Google's instructions on their website for Tensorflow, or try the following:
  
          sudo pip install --upgrade https://storage.googleapis.com/tensorflow/linux/gpu/tensorflow-0.6.0-cp27-none-linux_x86_64.whl