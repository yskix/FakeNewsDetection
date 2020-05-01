# FakeAlert
This is Submission for Lumiata COVID 19 Hackathon

Before you forward those whatsapp messages or share tweets or facebook posts. Make sure you run a check through our
system to ensure that the news is authentic and real

Prerequisites:
1. Ubuntu OS
2. Anaconda installed with Python > 3.6

How to RUN:
1. Create a conda environment using the following commands
  $ conda create -n FakeAlert python=3.6
  $ cd FakeNewsDetection
  $ pip install -r requirements.txt
  
2. some required commands
  $ bert-serving-start -model_dir wwm_uncased_L-24_H-1024_A-16/ -num_worker=1

3. Test with following commands
  $ python final.py "COVID 19 has a new vaccine"  
  $ python final.py "COVID-19 is an unprecedented pandemic"
