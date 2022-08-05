from tokens import client_id, client_secret, token 
from lyricsgenius import Genius

def main():
    """Main :)"""
    genius = Genius(token)
    #this fucking chugs sometimes for no reason
    artist = genius.search_artist("Yung Gravy", max_songs=20)
    artist.save_lyrics('Gravy20.json')

    

if __name__ == "__main__":
    main()