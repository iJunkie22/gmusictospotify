from __future__ import unicode_literals

__author__ = 'ethan'

from spotify.client import Spotify

import logging
import curses.ascii
from credentials import CREDENTIALS as __CRED


log = logging.getLogger(__name__)

__UNAME = __CRED['Spotify']['username']
__PWORD = __CRED['Spotify']['password']

searching = False


def uri_to_url(uri_str):
    uri_list = str(uri_str).split(':')
    assert uri_list[1] == 'track'
    sp_url_frmt = "https://open.spotify.com/{}/{}"
    return sp_url_frmt.format(uri_list[1], uri_list[2])


class App(object):
    def __init__(self):
        self.sp = Spotify()
        self.logged_in = False
        self.return_only = ["tracks"]

    def run(self, uname, pword):
        # @self.sp.login(os.environ['USERNAME'], os.environ['PASSWORD'])
        @self.sp.login(uname, pword)
        def on_login():
            self.sp.search('daft punk', count=7, callback=self.on_search)
            self.logged_in = True

    def do_search(self, sterm):
        global searching
        searching = True
        try:
            str_sterm = str(sterm)
        except UnicodeEncodeError as _uee:
            str_sterm = "".join([c for c in sterm if curses.ascii.isascii(c)])

        str_sterm = str(str_sterm)

        assert isinstance(str_sterm, str)

        self.sp.search(str_sterm, count=1, callback=self.on_search)

    def on_search(self, result):
        global searching
        # Artists
        if not self.return_only or "artists" in self.return_only:
            print 'artists (%s)' % result.artists_total

            for artist in result.artists:
                print '\t[%s] "%s"' % (artist.uri, artist.name)

                if not artist.portraits:
                    continue

                for portrait in artist.portraits:
                    print '\t\t', portrait.file_url

        # Albums
        if not self.return_only or "albums" in self.return_only:
            print 'albums (%s)' % result.albums_total

            for album in result.albums:
                print '\t[%s] "%s" - %s' % (album.uri, album.name, ', '.join([ar.name for ar in album.artists]))

                if not album.covers:
                    continue

                for cover in album.covers:
                    print '\t\t', cover.file_url

        # Tracks
        if not self.return_only or "tracks" in self.return_only:
            #print 'tracks (%s)' % result.tracks_total

            for track in result.tracks:
                print '\t%s [%s] "%s" - %s' % (uri_to_url(track.uri), track.uri, track.name,
                                                ', '.join([ar.name for ar in track.artists if ar.name]))

        # Playlists
        if not self.return_only or "playlists" in self.return_only:
            print 'playlists (%s)' % result.playlists_total

            for playlist in result.playlists:
                print '\t[%s] "%s"' % (playlist.uri, playlist.name)
        searching = False


if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG)
    logging.basicConfig(level=logging.CRITICAL)

    app = App()
    app.run(__UNAME, __PWORD)

    import gpmusicAPI

    while not app.logged_in:
        pass

    current_pl = None
    for trac in gpmusicAPI.found_tracks:

        t1, t2, t3 = trac.rpartition("::")
        if t1 != current_pl:
            print "=" * 50, "\n", t1
        app.do_search(t3)
        #print "\nsearching for", t3
        while searching:
            pass
        current_pl = t1

    #while True:
    #    raw_input()

