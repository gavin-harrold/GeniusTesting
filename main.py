import tensorflow as tf
from tokens import client_id, client_secret, token 
from lyricsgenius import Genius
import numpy as np



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


def main():
    """
        Main :)
    """
    genius = Genius(token)
    #this fucking chugs for no reason (very dumb)
    artist = genius.search_artist("Yung Gravy", max_songs=20)
    artist.save_lyrics('Gravy20.json')

    #writing lyric to file
    text = write_lyrics(artist)
    file = open("GravyLyrics200.txt", "w")
    file.write(text)
    file.close()

    #prep data for Tensor
    with open('GravyLyrics200.txt') as f:
        text = f.read()
    
    vocab = sorted(set(text))
    char_to_ind = {u:i for i, u in enumerate(vocab)}
    ind_to_char = np.array(vocab)
    encoded_text = np.array([char_to_ind[c] for c in text])
    averageLineLength = calculate_line_average('GravyLyrics200.txt')
    print(int(averageLineLength))
    





if __name__ == "__main__":
    main()