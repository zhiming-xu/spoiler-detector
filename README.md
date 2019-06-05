---
title: Motivation and Introduction
date: 2019-06-04 15:00:00
---
## Introduction
### Motivation
I believe that many people dislike spoilers just like me, especially for the upcoming movies, TV series, and animes. Although
I think I am quite tolerant to them, the moment I saw a key plot shown in Weibo's frontpage before I went to see the Avengers: Endgame,
I felt really frustrated. At that time, I am developing a classifier to detect toxic online forum contents. So I came up with the idea of developing a neural network model to detect spoilers. I even thought of add this feature to the toxic content detector, since spoilers themselves are indeed toxic, too. But I do not find proper dataset at that time. Fortunately, just one month later, I found [IMDB movie information and user review dataset with spoiler label](https://www.kaggle.com/rmisra/imdb-spoiler-dataset). It contains ~1300 different movies' information, and ~570k user reviews on them.
### Data preprocessing
The original dataset has actually two files, one contains movie information: movie ID, genre, duration, plot summary etc, 25 columns in total, and the other contains user review: user ID, movie ID, review summary, review detail, label etc, 7 columns in total. For this task, the most directly related features should be movie's plot summary, user's review summary (or title), review detail and the label. I would guess that rating might also have something to do with spoiling, since if people either very satisfied or unsatisfied with a movie might be more likely to give out key plot in review due to their strong emotion related to it. (Suppose your favorite character in GoT suddenly died, would you give a low score, write the death in your review and kindly greet the scriptwriter) But now I only feed the three field aforementioned to the network. Extracting these three features is relatively easy, just load the two json files as data frame and do a natural join on movie ID. The code can be found in [data_loader](./data_loader.ipynb).
## Model
### Manhattan LSTM
Firstly I tried manhattan LSTM (malstm), this model was introduced in a [paper](https://www.aaai.org/ocs/index.php/AAAI/AAAI16/paper/download/12195/12023) published on AAAI'16. It intends to measure the similarity between twn sentences, so I think it might be able to connect summary with spoiler. The model works as follows.
- Use single direction LSTM to embed two input sentences into vectors $$\vec{v_1}$$, $$\vec{v_2}$$. 
- Calculate the manhattan distance between these two vectors $$vec{d}=\vec{v_1}-\vec{v_2}$$.
- Compute $$\exp(-\vec{d})$$, intuitively, this value is closer to 1 if $$\vec{d}$$ is small, i.e., two vector representions are alike. Thus we can use it to detect similarity in two sentences. However, when using this model on IMDB dataset, I found that it can only output the most common label although it worked on Quora duplicate question pair dataset. I think there are several reasons:
- In Quora dataset, the lengths of questions are usually small, in fact, fewer of them exceed 50 words. But for IMDB dataset, the average length of review is 300 words, and that of plot summary is 100 words. This will result in LSTM memorizing a lot of information, which has long been a problem of its structure.
- The spoiler in review might be very short, and takes a fairly small portion. So the review and plot summary can be quite different while the former still contains a spoiler. On this occasion, measure the element-wise is not reasonable and can produce inaccurate prediction.
In fact, when tested on this model, I found that for short plot and one sentence review (also a spoiler) made up by myself, it could predicts the right label. But for IMDB dataset, it failed to produce useful result.
### Self-attention sentence embedding
This is the second model I used. The difference from malstm is that the sentence embedding changed from a vanilla LSTM to four layers of LSTM followed by a self attention layer. This model was introduced in a [paper](https://arxiv.org/pdf/1703.03130.pdf) published on ICLR'17.
