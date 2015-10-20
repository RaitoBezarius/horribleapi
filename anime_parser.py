from bs4 import BeautifulSoup
from collections import namedtuple
import hashlib

class Provider(object):
    def __init__(self, name, link):
        self.name = name
        self.link = link

    def serialize(self):
        return {'name': self.name, 'link': self.link}

    def __str__(self):
        return '<Provider {}>'.format(self.name)

class Version(object):
    def __init__(self, quality, providers):
        self.quality = quality
        self.providers = providers

    def serialize(self):
        return {'quality': self.quality, 'providers': map(lambda p: p.serialize(), self.providers)}

    def __str__(self):
        return '<Version {}>'.format(self.quality)

class Anime(object):
    def __init__(self, title, release_date, episode):
        self.title = title
        self.release_date = release_date
        self.episode = episode
        self.id = hashlib.new("md5",
                              "{}{}{}"\
                              .format(release_date, title, episode)).hexdigest()

    def serialize(self):
        if not hasattr(self, 'versions'):
            raise RuntimeError('Versions are not specified! Cannot serialize!')

        return {
            'title': self.title,
            'release_date': self.release_date,
            'episode': self.episode,
            'id': self.id,
            'versions': map(lambda v: v.serialize(), self.versions)
        }

    def __str__(self):
        return '<Anime {} - {}>'.format(self.title, self.episode)


def parse_anime_info(entry):
    release_date = entry[0]
    title = ' '.join(entry[1:-2])
    episode_id = int(entry[-1])
    unique_id = hashlib.new("md5",
                            "{}{}{}"\
                            .format(release_date, title, episode_id)).hexdigest()

    return Anime(title,
                 release_date,
                 episode_id)

def parse_providers(providers):
    for provider_block in providers:
        provider = provider_block.a['title']
        link = provider_block.a['href']

        yield Provider(name=provider, link=link)

def parse_versions(versions):
    for version in versions:
        quality = version.text.split(' ')[-1]
        providers_nodes = version.parent.find_all(attrs={'class': 'dl-type'})


        yield Version(quality=quality,
                      providers=set(parse_providers(providers_nodes)))

def parse_animes(pageContent):
    try:
        soup = BeautifulSoup(pageContent, 'html.parser')
        episodes = soup.find_all(attrs={'class': 'release-info'})
        for episode in episodes:
            try:
                entry = episode.td.text.split(' ')
                anime = parse_anime_info(entry)
                matching_versions_nodes = filter(lambda n: n.text.startswith(anime.title), soup.find_all(attrs={'class': 'dl-label'}))
                anime.versions = set(parse_versions(matching_versions_nodes))
                yield anime
            except Exception as e:
                print ('Failed while parsing an anime, skipping it ({})'.format(e))
    except Exception as e:
        print ('Fatal failure while parsing animes, aborting the parsing. ({})'.format(e))

if __name__ == '__main__':
    import requests
    animes = list(parse_animes(requests.get('http://horriblesubs.info/lib/latest.php').text))
    print (animes)
    import pdb;
    pdb.set_trace()
