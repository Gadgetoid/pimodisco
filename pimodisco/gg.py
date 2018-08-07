import random
import ast
import sys

#sys.path.insert(0, "../")
import ns2

from pimodisco import source_url, version as version__
from pimodisco.checks import authCheck

from discord import TextChannel
from discord.ext import commands


def setup_args(parser):
    pass

def setup(bot, args):
    server = ns2.Server()

    @bot.command()
    async def map(ctx):
        """
        Displays current map of server
        """
        info = server.get_info()
        map_url = ''

        map_name = info.map

        if info.map in ns2.map_info.keys():
            mapdata = ns2.map_info[info.map]

            map_url = "\n" + ns2.map_src + mapdata.image
            map_name = "{} ({})".format(mapdata.name, info.map)

            await ctx.send("""{server}
Current map: {map} ({type})
Tech Points: {tech}
Res Nodes: {res}
{map_url}""".format(
    server=info.server,
    type='Official' if mapdata.official else 'Community', 
    map=map_name, 
    map_url=map_url, 
    tech=mapdata.tech, 
    res=mapdata.res))
            return

        await ctx.send("Current map: {map}".format(map=map_namel))

    @bot.command()
    async def info(ctx):
        """
        Displays information about the server
        """
        async with ctx.typing():
            info = server.get_info()
            info.address = server.address
            await ctx.send("""
    {server}
    Map: {map}
    Players: {num_players}/{max_players}
    Type: {type}
    Running on: {environment}
    VAC: {vac_secured}
    Play: steam://connect/{address}:{port}
    """.format(**info))

    @bot.command(aliases=['players','online','pop'])
    async def playing(ctx):
        """
        Lists players on NS2 GG server
        """
        async with ctx.typing():
            info = server.get_info()
            players = server.get_players()
            if len(players.players) > 0:
                output = ["{server}".format(**info),
                        "{num_players} of {max_players} players online.".format(**info),
                        ""]
                output.append("```")

                max_name_len = 0
                for player in players.players:
                    max_name_len = max(max_name_len, len(player.name))

                max_name_len += 4

                format_string = "{rank:<4s} | {score:<7s} | {name:<" + str(max_name_len) + "s} | {time:>8s}"

                output.append(format_string.format(
                    rank="Rank",
                    score="Score",
                    name="Name",
                    time="Time"
                ))
                output.append("-"*(28 + max_name_len))
                rank = 1

                for player in reversed(sorted(players.players, key=lambda p: p.score)):
                    played_hours = int(player.duration // 60 // 60)
                    played_mins = int((player.duration % (60*60)) // 60)
                    played_seconds = int(player.duration % 60)

                    player_name = player.name
                    output.append(format_string.format(
                        rank=str(rank),
                        name=player_name,
                        score=str(player.score),
                        time="{hours:02d}:{mins:02d}:{seconds:02d}".format(
                            hours=played_hours,
                            mins=played_mins,
                            seconds=played_seconds
                        )
                    ))
                    rank += 1
                output.append("```")
                if info.num_players < info.max_players / 2:
                    output.append("Help seed: steam://connect/{}:{}".format(
                        server.address,
                        server.port
                    ))
                elif info.num_players < info.max_players:
                    output.append("Play now: steam://connect/{}:{}".format(
                        server.address,
                        server.port
                    ))
                await ctx.send("\n".join(output))
            else:
                await ctx.send("Nobody is playing right now :(\nSeed: steam://connect/{}:{}".format(
                        server.address,
                        server.port
                    ))
