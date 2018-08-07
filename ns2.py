from construct import *
from ratelimit import limits
import socket

class Map():
    def __init__(self, name, image, tech=0, res=0, official=False):
        self.name = name
        self.image = image
        self.tech = tech
        self.res = res
        self.official = official

map_src = 'https://wiki.unknownworlds.com/images'
map_info = {
    'ns2_summit': Map('NS2 Summit', '/3/3b/Ns2_summit.png', tech=5, res=9, official=True),
    'ns2_tram': Map('NS2 Tram', '/b/bf/Ns2_tram.png', tech=5, res=9, official=True),
    'ns2_mineshaft': Map('NS2 Mineshaft', '/6/63/Ns2_mineshaft.png', tech=5, res=11, official=True),
    'ns2_docking': Map('NS2 Docking', '/9/98/Ns2_docking.png', tech=5, res=9, official=True),
    'ns2_veil': Map('NS2 Veil', '/4/4e/Ns2_veil.png', tech=4, res=10, official=True),
    'ns2_refinery': Map('NS2 Refinery', '/e/e5/Ns2_refinery.png', tech=5, res=11, official=True),
    'ns2_biodome': Map('NS2 Biodome', '/9/91/Ns2_biodome.png', tech=5, res=9, official=True),
    'ns2_eclipse': Map('NS2 Eclipse', '/a/af/Ns2_eclipse.png', tech=4, res=9, official=True),
    'ns2_descent': Map('NS2 Descent', '/6/6e/Ns2_descent.png', tech=5, res=9, official=True),
    'ns2_kodiak': Map('NS2 Kodiak', '/d/d9/Ns2_kodiak.png', tech=4, res=10, official=True),
    'ns2_derelict': Map('NS2 Derelict', '/3/3e/Ns2_derelict.png', tech=4, res=9, official=True),

    'ns2_jambi': Map('NS2 Jambi', '/0/06/Ns2_jambi.png', tech=5, res=10),
    'ns2_caged': Map('NS2 Caged', '/1/10/Ns2_caged.png', tech=4, res=10),
    'ns2_fusion': Map('NS2 Fusion', '/1/16/Ns2_fusion.png', tech=4, res=9),
    'ns2_mineral': Map('NS2 Mineral', '/a/a3/Ns2_mineral.png', tech=5, res=10),
    'ns2_uplift': Map('NS2 Uplift', '/2/25/Ns2_uplift.png', tech=5, res=11),
    'ns2_hydra': Map('NS2 Hydra', '/c/cd/Ns2_hydra.png'),
    'ns2_orbital': Map('NS2 Orbital', '/d/d4/Ns2_orbital.png', tech=4, res=11),
    'ns2_prison': Map('NS2 Prison', '/1/1c/Ns2_prison.png', tech=5, res=11),
    'ns2_nothing': Map('NS2 Nothing', '/8/80/Ns2_nothing.png', tech=5, res=9),
    'ns2_outerrimark': Map('NS2 Outer Rimark', '/c/c9/Ns2_outerrimark.png', tech=5, res=9),
    'ns2_light': Map('NS2 Light', '/7/7b/Ns2_light.png', tech=5, res=9),
    'ns2_docking2': Map('NS2 Docking 2', '/7/77/Ns2_docking22.png', tech=5, res=10),
    'ns2_nexus': Map('NS2 Nexus', '', tech=4, res=11),
    'ns2_forge': Map('NS2 Fordge', '/f/f1/Ns2_forge.png', tech=4, res=10)
}

type_text = CString(encoding='UTF-8') 

tags_map = {
    'shine': 'Shine Admin Mod',
    'CHUD_0x0': 'NS2+ Client Mod'
}

def UnpackTag(value):
    try:
        return int(value)
    except ValueError:
        if value in tags_map:
            return tags_map[value]
        return value

def PackTag(value):
    return str(value)

class TagsAdapter(Adapter):
    def _decode(self, obj, context, path):
        return list(map(UnpackTag,obj.split("|")))

    def _encode(self, obj, context, path):
        return "|".join(map(PackTag, obj))

type_tags = TagsAdapter(type_text)

type_type = Enum(Int8ul, **{
    'Dedicated': ord('d'),
    'Non-dedicated': ord('l'),
    'SourceTV (relay)': ord('p')
})

type_environment = Enum(Int8ul, **{
    'Linux': ord('l'),
    'Windows': ord('w'),
    'Mac': ord('m'),
    'Mac': ord('m')
})

type_visibility = Enum(Int8ul, **{
    'Public': 0,
    'Private': 1
})

type_vac_secured = Enum(Int8ul, **{
    'No': 0,
    'Yes': 1
})

response_info = Struct(
    Const(0xFFFFFFFF, Int32ub),
    'header' / Int8ub,
    'protocol' / Int8ub,
    'server' / type_text,
    'map' / type_text,
    'folder' / type_text,
    'game' / type_text,
    'steam_id_short' / Int16ul,
    'num_players' / Int8ub,
    'max_players' / Int8ub,
    'num_bots' / Int8ub,
    'type' / type_type, # d for dedicated, l for non-dedicated, p for SourceTV relay
    'environment' / type_environment, # l for linux, w for windows, m or o for Mac
    'visibility' / type_visibility,
    'vac_secured' / type_vac_secured,
    'version' / type_text,
    'extra_data_flag' / Int8ub,
    'port' / If(this.extra_data_flag & 0x80, Int16ul),
    'steam_id' / If(this.extra_data_flag & 0x10, Int64ul),
    'spectator_port' / If(this.extra_data_flag & 0x40, Int16ul),
    'spectator_server' / If(this.extra_data_flag & 0x40, type_text),

    # Example tags: 323|ns2|M|65|0|8|82|30|26|20|100|0|0|2|1|0|-2147483648|shine||CHUD_0x0
    # 323 = NS2 build
    # ns2 = presumably game type
    # M = ?
    # shine = Shine admin mod
    # CHUD_0x0 = NS2+ (previously known as Custom HUD)
    'tags' / If(this.extra_data_flag & 0x20, type_tags),
    'game_id' / If(this.extra_data_flag & 0x01, Int64ul)
)

request_players = Struct(
    Const(0xFFFFFFFF, Int32ul),
    'header' / Default(Int8ub, 0x55),
    'challenge' / Default(Int32sb, -1)
)

response_players = Struct(
    Const(0xFFFFFFFF, Int32ul),
    'header' / Const(0x44, Int8ub), # Always equal to 0x44 or 'D'
    'players' / PrefixedArray(Int8ub, Struct(
        'index' / Int8ub,
        'name' / type_text,
        'score' / Int32ul,
        'duration' / Float32l
    ))
)

request_text = Struct(
    Const(0xFFFFFFFF, Int32ul),
    'command' / type_text
)

class Server():
    def __init__(self, address='88.198.52.23', port=27016):
        self.address = address
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(1.0)
        self.socket.bind(('0.0.0.0', self.port))

    def __del__(self):
        self.socket.close()

    def _send(self, data):
        self.socket.sendto(data, (self.address, self.port))

    def _recv(self, length=1024):
        return self.socket.recvfrom(length)

    def _sendrecv(self, data, length=1024):
        self._send(data)
        return self._recv(length)

    @limits(calls=1, period=1)
    def get_players(self):
        # Build an empty player request asking for a challenge code
        data, addr = self._sendrecv(request_players.build(dict()))
        response = request_players.parse(data)
        # Produce a proper request with the correct challenge code
        request = request_players.build(dict(challenge=response.challenge))
        data, addr = self._sendrecv(request)

        # Parse and return the player data
        return response_players.parse(data)

    @limits(calls=1, period=1)
    def get_info(self):
        data, addr = self._sendrecv(request_text.build(dict(command='TSource Engine Query')))
        return response_info.parse(data)


if __name__ == "__main__":
    gg = Server()
    info = gg.get_info()
    players = gg.get_players()
    print(info)
    print(players)