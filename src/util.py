from mxnet import gluon
import gluonnlp as nlp
import time
import multiprocessing as mp
import itertools

class mp_tokenizer:
    '''
    length_clip takes as input a list and outputs a list with maximum length
    '''
    def __init__(self, tokenizer, clip_length1, clip_length2):
        self.tokenizer = tokenizer
        self.clipper1 = nlp.data.ClipSequence(clip_length1)
        self.clipper2 = nlp.data.ClipSequence(clip_length2)
    
    def preprocess(self, data):
        # now the first element in tuple is review, second plot and third label
        left, right, label = data[0], data[1], int(data[2])
        # clip the length of review words
        left, right = self.clipper1(self.tokenizer(left.lower())), self.clipper2(self.tokenizer(right.lower()))
        return left, right, label

    def get_length(self, data):
        return float(len(data[0]))

    def process_dataset(self, data):
        start = time.time()
        with mp.Pool() as pool:
            # Each sample is processed in an asynchronous manner.
            data = gluon.data.ArrayDataset(pool.map(self.preprocess, data))
            lengths = gluon.data.ArrayDataset(pool.map(self.get_length, data))
        end = time.time()
        print('Done! Sequence clipping and get length Time={:.2f}s, #Sentences={}'.format(end - start, len(data)))
        return data, lengths

class mp_indexer:
    '''
    A token index or a list of token indices is returned according to the vocabulary.
    '''
    def __init__(self, dataset_token, embedding):
        self.dataset_token = dataset_token
        self.seqs = [ sample[0] + sample[1] for sample in dataset_token]
        self.counter = nlp.data.count_tokens(list(itertools.chain.from_iterable(self.seqs)))
        self.vocab = nlp.Vocab(self.counter, max_size=40000)
        self.vocab.set_embedding(nlp.embedding.GloVe(source=embedding))

    def token_to_idx(self, data):
        return self.vocab[data[0]], self.vocab[data[1]], data[2]

    def process_dataset(self, data):
        # A token index or a list of token indices is returned according to the vocabulary.
        with mp.Pool() as pool:
            data_new = pool.map(self.token_to_idx, data)
        return data_new