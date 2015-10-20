from twisted.internet.defer import inlineCallbacks
from twisted.internet import task
from twisted.internet import reactor
from twisted.web.client import getPage

from autobahn import wamp
from autobahn.twisted.wamp import ApplicationSession

import anime_parser

class HorribleSubsBackend(ApplicationSession):

    def __init__(self, config):
        super(HorribleSubsBackend, self).__init__(config)
        self.initialize()

    def initialize(self):
        self.animes_cache = {}
        self.polling_task = task.LoopingCall(self.fetchAnimes)
        self.polling_task.start(0.5)

    def fetchAnimes(self):
        d = getPage('http://horriblesubs.info/lib/latest.php')
        d.addCallbacks(self.parseAnime, self.onFetchError)

    def parseAnime(self, pageContent):
        hasChanged = False
        for anime in anime_parser.parse_animes(pageContent):
            try:
                if anime.id in self.animes_cache:
                    # I need to update partially the object
                    pass
                else:
                    hasChanged = True
                    self.animes_cache[anime.id] = anime
                    self.publish(u'horriblesubs.new_anime_released', anime.serialize())
            except Exception as e:
                print ('Failed to update an anime. ({})'.format(e))

        if hasChanged:
            print ('Cache updated! ({} animes in the DB)'.format(len(self.animes_cache)))

    def onFetchError(self, error):
        print ("Error while fetching the page: {}".format(error))

    @wamp.register(u'horriblesubs.get_latest')
    def getLatest(self, limit=50):
        return dict(map(lambda tpl: (tpl[0], tpl[1].serialize()), self.animes_cache.items()[:limit]))

    @inlineCallbacks
    def onJoin(self, details):
        res = yield self.register(self)
        print ("HorribleSubsBackend: {} procedures registered.".format(len(res)))

