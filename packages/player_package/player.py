# Class that contains player info
class playerInfo:
    def toDict(self):
        return self.__dict__

    def __init__(self, region, id, tag, summoner_id, rank):
        self.region = region
        self.id = id
        self.tag = tag
        self.summoner_id = summoner_id
        self.rank = rank

# Creates player dictionary
def createPlayerDict(sheet, player, region, id, tag, summoner_id, rank):
    res_dict = {sheet: {player: playerInfo(region, id, tag, summoner_id, rank).toDict()}}
    return res_dict

# Updates dictionary based on player dictionary
def updatePlayerDict(main_dict, player_dict):
    res_dict = main_dict
    sheet_key = list(player_dict.keys())[0]
    return res_dict[sheet_key].update(player_dict[sheet_key])
