import json
import tensorflow as tf
from tokens import client_id, client_secret, token 
from lyricsgenius import Genius
import numpy as np
from os import path

from keras.models import Sequential, load_model
from keras.layers import LSTM,Dense,Embedding,Dropout,GRU
from keras.losses import sparse_categorical_crossentropy

ARTIST = input("Enter an artist to emulate: ")
SONG_COUNT = input("Enter the amount of songs to attempt to track: ")
FILE = ARTIST + "Lyrics" + SONG_COUNT + ".txt"
#"GravyLyrics100.txt"

def write_lyrics(artist):
    """
        writes lyrics with a nice break between songs to a String variable
        @param artist: results from Genius library
        @returns text to insert into file
    """
    txt = ''

    special_chars = set([ 'ँ', 'आ', 'ए', 'क', 'ग', 'ज', 'त',
       'द', 'ध', 'न', 'प', 'ब', 'म', 'य', 'र', 'व', 'श', 'ह', 'ा', 'ि',
       'ी', 'ू', 'े', 'ै', 'ो', '्', '\u2005', '\u200c', '—', 
       '\u205f', '느', '사', '어', '이', '제', '죠', '품', '회','\u0435','\xa0','\u200b'])


    for song in artist.songs:
        chars = set(song.lyrics)
        separator = '\n======================================================================\n\n'
        if len(chars.intersection(special_chars)) == 0:
            txt += song.lyrics + "\n" + separator
        else:
            pass
    return txt

def calculate_line_average(file):
    """
        calculate the average line length of a given file
        @param String file: file name to calculate average line length
        @returns float: calculated average line length in float form
    """
    sum = 0
    lineCount = 0
    with open(file) as f:
        for line in f:
            lineCount+=1
            sum += len(line)
    return sum/lineCount


def create_seq_targets(seq):
    """
    shift text and group as tuple
    @param seq: input text sequence
    @returns tuple of input_txt and target_txt
    """
    input_txt = seq[:-1]
    target_txt = seq[1:]
    return input_txt, target_txt

def sparse_cat_loss(y_true,y_pred):
    """
    loss function using Keras' loss function
    @param y_true: ground truth values
    @param y_pred: predicted values
    @returns sparse categorical crossentropy loss value
    """
    return sparse_categorical_crossentropy(y_true, y_pred, from_logits=True)


def create_model(vocab_size, embed_dim, rnn_neurons, batch_size):
    """
    creates model for tf
    @param vocab_size: length of vocab
    @param embed_dim: embed dimension
    @param rnn_neurons: neuron count
    @param batch_size: batch size
    @returns newly created model
    """
    model = Sequential()
    model.add(Embedding(vocab_size, embed_dim, batch_input_shape=[batch_size, None]))
    model.add(GRU(rnn_neurons, return_sequences=True, stateful=True, recurrent_initializer='glorot_uniform'))
    model.add(Dense(vocab_size))
    model.compile(optimizer='adam', loss=sparse_cat_loss)
    return model

def generate_text(model, start_seed, char_to_ind, ind_to_char, gen_size=100, temp=1.0):
    num_generate = gen_size
    input_eval = [char_to_ind[s] for s in start_seed]
    input_eval = tf.expand_dims(input_eval, 0)
    text_generated = []

    model.reset_states()
    for i in range(num_generate):
        predictions = model(input_eval)
        predictions = tf.squeeze(predictions, 0)
        predictions = predictions / temp
        predicted_id = tf.random.categorical(predictions, num_samples=1)[-1, 0].numpy()
        input_eval = tf.expand_dims([predicted_id], 0)
        text_generated.append(ind_to_char[predicted_id])
    return (start_seed + ''.join(text_generated))

def main():
    """
        Main :)
    """
    genius = Genius(token)
    #check if file already exists so it doesn't have to always chug
    if not path.exists(FILE):
        #this fucking chugs for no reason (very dumb)
        artist = genius.search_artist(ARTIST, max_songs=int(SONG_COUNT))
        json_file = ARTIST + SONG_COUNT + ".json"
        artist.save_lyrics(json_file)

        #writing lyric to file
        text = write_lyrics(artist)
        file = open(FILE, "w")
        file.write(text)
        file.close()

    #prep data for Tensor
    with open(FILE) as f:
        text = f.read()
    
    vocab = sorted(set(text))
    char_to_ind = {u:i for i, u in enumerate(vocab)}
    ind_to_char = np.array(vocab)
    encoded_text = np.array([char_to_ind[c] for c in text])
    averageLineLength = calculate_line_average(FILE)
    print(int(averageLineLength))
    
    #training sequences
    seq_length = 120
    total_seq_len = len(text)//(seq_length+1)
    
    char_dataset = tf.data.Dataset.from_tensor_slices(encoded_text)
    sequences = char_dataset.batch(seq_length+1, drop_remainder=True)

    dataset = sequences.map(create_seq_targets)

    #printing stuff
    """
    for input_txt, target_txt in dataset.take(1):
        print(input_txt.numpy())
        print(''.join(ind_to_char[input_txt.numpy()]))
        print('\n')
        print(target_txt.numpy())
        print(''.join(ind_to_char[target_txt.numpy()]))
    """
    #creating batches!
    batch_size = 128
    buffer_size = 10000
    dataset = dataset.shuffle(buffer_size).batch(batch_size, drop_remainder=True)

    #model creation (LSTM)
    vocab_size = len(vocab)
    embed_dim = 64
    rnn_neurons = 1026
    #actually create da model
    model = create_model(
        vocab_size=vocab_size,
        embed_dim=embed_dim,
        rnn_neurons=rnn_neurons,
        batch_size=batch_size
    )
    #debug, prints model summary
    print(model.summary())

    #model training!!!!!
    for input_example_batch, target_example_batch in dataset.take(1):
        example_batch_predictions = model(input_example_batch)
        print(example_batch_predictions.shape, " <=== (batch_size, seq_length, vocab_size)")

    sampled_indices = tf.random.categorical(example_batch_predictions[0], num_samples=1)
    #format to singular list rather than list of list
    sampled_indices = tf.squeeze(sampled_indices,axis=-1).numpy()

    #print stuff
    print("Given the input sequence: \n")
    print("".join((ind_to_char[input_example_batch[0]])))
    print("\n")
    print("".join(ind_to_char[sampled_indices]))

    epochs = 100
    model.fit(dataset, epochs=epochs)
    model.save(ARTIST + '_gen.h5')
    model = create_model(vocab_size, embed_dim, rnn_neurons, batch_size=1)
    model.load_weights(ARTIST + '_gen.h5')
    model.build(tf.TensorShape([1, None]))

    print(generate_text(model, 'Hey', char_to_ind, ind_to_char, gen_size=1000))






if __name__ == "__main__":
    main()
