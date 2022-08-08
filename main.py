import tensorflow as tf
from tokens import client_id, client_secret, token 
from lyricsgenius import Genius
import numpy as np




def write_lyrics(artist):
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

def main():
    """Main :)"""
    genius = Genius(token)
    #this fucking chugs for no reason
    artist = genius.search_artist("Yung Gravy", max_songs=20)
    artist.save_lyrics('Gravy20.json')

    #writing lyric to file
    text = write_lyrics(artist)
    file = open("GravyLyrics200.txt", "w")
    file.write(text)
    file.close()






if __name__ == "__main__":
    main()