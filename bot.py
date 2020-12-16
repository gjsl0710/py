import discord
import asyncio
import os
from discord.ext import commands
import urllib
from urllib.request import URLError
from urllib.request import HTTPError
from urllib.request import urlopen
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from urllib.parse import quote
import re # Regex for youtube link
import warnings
import requests
import time

client = discord.Client() # Create Instance of Client. This Client is discord server's connection to Discord Room
bottoken = ""


class ko_Avatar(commands.Cog):
 
    def __init__(self, client):
        self.client = client
 
# Comands embed
async def on_message(message):
    if message.content.startswith("크시야 내정보"):
    date = datetime.datetime.utcfromtimestamp(((int(message.author.id) >> 22) + 1420070400000) / 1000)
    embed = discord.Embed(Color=0x8b00ff)
    embed.add_field(name="이름", value=message.author.name, inline=True)
    embed.add_field(name="서버별명", value=message.author.display_name, inline=True)
    embed.add_field(name="가입일", value=str(date.year) + "년" str(date.month) + "월" + str(date.day) + "일", inline=True)
    embed.add_field(name="유저아이디", value=message.author.id, inline=True)
    embed.set_thumbnail(url=message.author.avatar_url)
    await message.channel.send(embed=embed)

    # Commands
    @commands.command()
    async def 아바타(self, ctx):
        if (ctx.message.mentions.__len__() > 0):
            for user in ctx.message.mentions:
                pfp = str(user.avatar_url)
                embed = discord.Embed(title="**" +user.name + "**님의 아바타", description="[Link]" + "(" + pfp + ")",
                                      color=0xffffff)
                embed.set_image(url=pfp)
                embed.set_footer(text="Offered by NACL - Shio", icon_url="https://raw.githubusercontent.com/Shio7/EZ-Bot/master/images/Shio71.png")
                await ctx.trigger_typing()
                await ctx.send(embed=embed)
        else:
            pfp = ctx.author.avatar_url
            embed = discord.Embed(title="**" + ctx.author.name + "**님의 아바타", description="[Link]" + "(" + str(pfp) + ")",
                                color=0xffffff)
            embed.set_image(url=pfp)
            embed.set_footer(text="Offered by NACL - Shio", icon_url="https://raw.githubusercontent.com/Shio7/EZ-Bot/master/images/Shio71.png")
            await ctx.trigger_typing()
            await ctx.send(embed=embed)
 
def setup(client):
    client.add_cog(ko_Avatar(client))

@client.event
async def on_message(message):
    if message.content.startswith('!실시간검색어') or message.content.startswith('!실검'):
        json = requests.get('https://www.naver.com/srchrank?frm=main').json()
        ranks = json.get("data")
        data = []
        for r in ranks:
            rank = r.get("rank")
            keyword = r.get("keyword")
            if rank > 10:
                break
            data.append(f'**{rank}**위 {keyword}')

        dat = str(data)
        dat = dat.replace("'","")
        dat = dat.replace(", ","\n")
        dat = dat[1:-1]
        print(dat)
        embed = discord.Embed(title= '네이버 실시간 검색어 순위', description=(dat),colour=0x19CE60)
        await message.channel.send(embed=embed)


@client.event # Use these decorator to register an event.
async def on_ready(): # on_ready() event : when the bot has finised logging in and setting things up
    await client.change_presence(status=discord.Status.online, activity=discord.Game("크시야 코로나 | 코로나19 현황"))
    print("New log in as {0.user}".format(client))

@client.event
async def on_message(message): # on_message() event : when the bot has recieved a message
    #To user who sent message
    # await message.author.send(msg)
    print(message.content)
    if message.author == client.user:
        return

    if message.content.startswith("크시야 코로나"):
        # 보건복지부 코로나 바이러스 정보사이트"
        covidSite = "http://ncov.mohw.go.kr/index.jsp"
        covidNotice = "http://ncov.mohw.go.kr"
        html = urlopen(covidSite)
        bs = BeautifulSoup(html, 'html.parser')
        latestupdateTime = bs.find('span', {'class': "livedate"}).text.split(',')[0][1:].split('.')
        statisticalNumbers = bs.findAll('span', {'class': 'num'})
        beforedayNumbers = bs.findAll('span', {'class': 'before'})

        #주요 브리핑 및 뉴스링크
        briefTasks = []
        mainbrief = bs.findAll('a',{'href' : re.compile('\/tcmBoardView\.do\?contSeq=[0-9]*')})
        for brf in mainbrief:
            container = []
            container.append(brf.text)
            container.append(covidNotice + brf['href'])
            briefTasks.append(container)
        print(briefTasks)

        # 통계수치
        statNum = []
        # 전일대비 수치
        beforeNum = []
        for num in range(7):
            statNum.append(statisticalNumbers[num].text)
        for num in range(4):
            beforeNum.append(beforedayNumbers[num].text.split('(')[-1].split(')')[0])

        totalPeopletoInt = statNum[0].split(')')[-1].split(',')
        tpInt = ''.join(totalPeopletoInt)
        lethatRate = round((int(statNum[3]) / int(tpInt)) * 100, 2)
        embed = discord.Embed(title="코로나19 현황", description="대한민국의 코로나19 현황을 보여줍니다.",color=0x8b00ff,url="http://ncov.mohw.go.kr/index.jsp")
        embed.add_field(name="현황기준",value="해당 자료는 " + latestupdateTime[0] + "월 " + latestupdateTime[1] + "일 "+latestupdateTime[2] +" 자료입니다.", inline=False)
        embed.set_author(name="아래 제목을 클릭해 더 많은정보를 확인할 수 있습니다.",icon_url=message.author.avatar_url)
        embed.add_field(name="확진환자(누적)", value=statNum[0].split(')')[-1]+"("+beforeNum[0]+")",inline=True)
        embed.add_field(name="완치환자(격리해제)", value=statNum[1] + "(" + beforeNum[1] + ")", inline=True)
        embed.add_field(name="치료중(격리 중)", value=statNum[2] + "(" + beforeNum[2] + ")", inline=True)
        embed.add_field(name="사망", value=statNum[3] + "(" + beforeNum[3] + ")", inline=True)
        embed.add_field(name="누적확진률", value=statNum[6], inline=True)
        embed.add_field(name="치사율", value=str(lethatRate) + " %",inline=True)
        embed.add_field(name="관련 브리핑" + briefTasks[0][0],value="Link : " + briefTasks[0][1],inline=False)
        embed.add_field(name="관련 브리핑" + briefTasks[1][0], value="Link : " + briefTasks[1][1], inline=False)
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/757231148933054467/788366198874177536/A0002257455_T.jpg")
        embed.set_footer(text='출처 : 중앙방역대책본부 | 중앙사고수습본부 | 질병관리본부 | 질병관리처 | 보건복지부 | 대한민국정부',
                         icon_url='https://cdn.discordapp.com/attachments/757231148933054467/788366694560301086/c8edc2d34fa9521b.jpeg')
        await message.channel.send("대한민국 코로나-19 현황", embed=embed)
        

client.run(os.environ['token'])