from __future__ import print_function, unicode_literals

__author__ = 'ethan'

from gmusicapi import Mobileclient
from credentials import CREDENTIALS as __CRED


def pretty_print_dict(in_dict):
    print('{')
    for k, v in in_dict.items():
        print('\t', k, ':', v)
    print('}')


def get_to_tuple(in_dict, *keys):
    return tuple([in_dict.get(_k) for _k in keys])


class GPlaylist(object):
    def __init__(self, playlist_dict):
        assert isinstance(playlist_dict, dict)
        self.__root_dict = playlist_dict
        assert isinstance(self.__root_dict['tracks'], list)


class GPlaylistCollection(object):
    __pkeys__ = {'tracks', 'id', 'name', 'deleted'}

    def __init__(self):
        self._playlists = {}
        self._detailed_playlists = {}
        self._all_track_ids = set()
        self._tracks = {}

    def add_playlist(self, playlist_dict):
        assert isinstance(playlist_dict, dict)
        assert self.__pkeys__ <= set(playlist_dict.keys())
        _temp_pl = {_k: playlist_dict.get(_k) for _k in self.__pkeys__}
        _temp_pl['tracks'] = [_k['trackId'] for _k in _temp_pl['tracks'] if not _k.get('deleted')]
        self._playlists[_temp_pl['id']] = _temp_pl
        self._all_track_ids.update(_temp_pl['tracks'])

    @property
    def all_track_ids(self):
        return self._all_track_ids

    @property
    def detailed_playlists(self):
        return self._detailed_playlists

    def define_track(self, track_dict):
        self._tracks[track_dict['id']] = track_dict

    def lookup_track(self, track_id):
        return self._tracks.get(track_id)

    def build_detailed_playlists(self):
        for _k, _v in self._playlists.items():
            assert isinstance(_v, dict)
            _temp_pl = _v.copy()
            _temp_pl['tracks'] = [self.lookup_track(_t_id) for _t_id in _v['tracks']]
            self._detailed_playlists[_k] = _temp_pl


keepers = ['Altivo', 'Runaway', 'Drives', 'Altivo 2.0', 'Slytherin', 'Now Showing: Anywhere But Here',
           'Altivo 2.5', 'HELL YEAH', 'Angst 2.0']

api = Mobileclient()

login_success = api.login(__CRED['GMusic']['username'], __CRED['GMusic']['password'], Mobileclient.FROM_MAC_ADDRESS)
assert login_success

new_col = GPlaylistCollection()

for playlist in api.get_all_user_playlist_contents():
    if playlist.get('name') in keepers:
        new_col.add_playlist(playlist)

for s in api.get_all_songs():
    if s.get('id') in new_col.all_track_ids:
        # This track belongs to one of the playlists
        new_col.define_track(s)

new_col.build_detailed_playlists()

found_tracks = []

for k_id in new_col.detailed_playlists.keys():
    cur_pl = new_col.detailed_playlists.get(k_id)
    cur_pl_name = cur_pl.get('name')
    print('=' * 50)
    print(cur_pl_name)

    for s in cur_pl['tracks']:
        found_tracks.append('::'.join([cur_pl_name, ' '.join([s['title'], s['artist'], s['album']])]))
        print('\t', ' - '.join([s['title'], s['artist'], s['album']]))
