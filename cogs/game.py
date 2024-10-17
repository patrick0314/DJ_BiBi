import os
import cv2
import random
import discord
import numpy as np

from discord.ext import commands
from utility.embed import embed_base
from PIL import Image, ImageDraw, ImageFont

class Game(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # AB game params
        self.ABanswer = {}
        self.count = {}

        # Gomoku game params
        self.start = {}
        self.size = {}
        self.board = {}
        self.go_round = {}
        self.chess = ["●","○"]

        # Codenames params
        self.text = {}
        self.code_answer = {}
        self.code_check = {}
    
    def generate_number(self):
        numbers = []
        while len(numbers) < 4:
            digit = random.randint(0, 9)
            if digit not in numbers: numbers.append(digit)
        answer = "".join(map(str, numbers))
        return answer

    @commands.command(name="abstart")
    async def abstart(self, ctx):
        try:
            # Set the answer
            self.ABanswer[ctx.guild.id] = self.generate_number()
            self.count[ctx.guild.id] = 0

            await ctx.send(embed=embed_base(ctx, title="BiBi is ready for AB Game", description="Are you ready for challenge??\n\n (( ◞•̀д•́)◞⚔◟(•̀д•́◟ ))", color="green", author=False))
        except Exception as e:
            print(e)
    
    @commands.command(name="guess", aliases=["g"])
    async def guess(self, ctx, number):
        try:
            # Check if the answer is set
            if ctx.guild.id not in self.ABanswer:
                await ctx.send(embed=embed_base(ctx, title="BiBi is not ready (ಠ ∩ಠ)", color="red", author=False))
                raise
            # Check if the number conform to regulations
            if len(number) != 4 or len(set(number)) != 4 or not number.isdigit():
                await ctx.send(embed=embed_base(ctx, title="What's your problem? (ಠ ∩ಠ)", color="red", author=False))
                raise

            A = B = 0
            for i in range(4):
                if self.ABanswer[ctx.guild.id][i] == number[i]: A += 1
                elif number[i] in self.ABanswer[ctx.guild.id]: B += 1
            self.count[ctx.guild.id] += 1
            
            if A == 4:
                await ctx.send(embed=embed_base(ctx, title="Congratulations ヾ(*~∀~*)ゞ", description=f"The answer is {number}\n You guess {self.count[ctx.guild.id]} times.", color="green", author=False))

                del self.ABanswer[ctx.guild.id]
                del self.count[ctx.guild.id]
            else:
                await ctx.send(embed=embed_base(ctx, title=f"{number} is `{A}` A `{B}` B", description=f"You guess {self.count[ctx.guild.id]} times.", color="orange", author=False))

        except Exception as e:
            print(e)

    @commands.command(name="gostart")
    async def gostart(self, ctx, size=15):
        try:
            self.start[ctx.guild.id] = True
            self.size[ctx.guild.id] = size
            self.go_round[ctx.guild.id] = 0
            self.board[ctx.guild.id] = [["+" for _ in range(self.size[ctx.guild.id])] for _ in range(self.size[ctx.guild.id])]
            if os.path.exists(f"./tmp/{ctx.guild.id}_board.png"): os.remove(f"./tmp/{ctx.guild.id}_board.png")
            await self.printBoard(ctx)

        except Exception as e:
            print(e)
    
    async def printBoard(self, ctx):
        try:
            if self.go_round[ctx.guild.id] % 2 == 0: title = "Black Turn"
            elif self.go_round[ctx.guild.id] % 2 == 1: title = "White Turn"
            await ctx.send(embed=embed_base(ctx, title=title, author=False))

            if not os.path.exists(f"./tmp/{ctx.guild.id}_board.png"):
                # Draw the board
                img = np.zeros((self.size[ctx.guild.id] * 30 + 30, self.size[ctx.guild.id] * 30 + 30, 3), np.uint8)
                img[:, :, 0].fill(176); img[:, :, 1].fill(215); img[:, :, 2].fill(234)
                for l in range(self.size[ctx.guild.id]):
                    # Draw horizontal line
                    cv2.line(img, (l * 30 + 30, 30), (l * 30 + 30, self.size[ctx.guild.id] * 30), (0, 0, 0), 3)
                    # Draw vertical line
                    cv2.line(img, (30, l * 30 + 30), (self.size[ctx.guild.id] * 30, l * 30 + 30), (0, 0, 0), 3)
                    # Draw number
                    if l + 1 < 10: cv2.putText(img, f"{l+1}", (l * 30 + 23, self.size[ctx.guild.id] * 30 + 23), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 0))
                    else: cv2.putText(img, f"{l+1}", (l * 30 + 20, self.size[ctx.guild.id] * 30 + 23), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 0))
                    cv2.putText(img, f"{l+1}", (self.size[ctx.guild.id] * 30 + 7, l * 30 + 33), cv2.FONT_HERSHEY_PLAIN, 1, (0, 0, 0))
            else:
                img = cv2.imread(f"./tmp/{ctx.guild.id}_board.png")
            for i in range(self.size[ctx.guild.id]):
                for j in range(self.size[ctx.guild.id]):
                    if self.board[ctx.guild.id][i][j] == "+": continue
                    elif self.board[ctx.guild.id][i][j] == "●": cv2.circle(img, (j * 30 + 30, i * 30 + 30), 10, (0, 0, 0), -1)
                    elif self.board[ctx.guild.id][i][j] == "○": cv2.circle(img, (j * 30 + 30, i * 30 + 30), 10, (255, 255, 255), -1)
            
            cv2.imwrite(f"./tmp/{ctx.guild.id}_board.png", img)
            picture = discord.File(f"./tmp/{ctx.guild.id}_board.png")
            await ctx.send(file=picture)
        except Exception as e:
            print(e)

    @commands.command(name="place")
    async def place(self, ctx, x, y):
        try:
            if ctx.guild.id not in self.start or not self.start[ctx.guild.id]:
                await ctx.send(embed=embed_base(ctx, title="BiBi is not ready (ಠ ∩ಠ)", color="red", author=False))
                raise

            x = int(x)
            y = int(y)
            # Check x and y range
            if (x or y) == -1:
                await ctx.send(embed=embed_base(ctx, title=f"{ctx.message.author.name} Surrender!", color="red", author=False))
                raise
            elif (x or y) > self.size[ctx.guild.id] or (x or y) < -1:
                await ctx.send(embed=embed_base(ctx, title="What's your problem? (ಠ ∩ಠ)", color="red", author=False))
                raise

            # Place
            if self.board[ctx.guild.id][y-1][x-1] == "+":
                self.board[ctx.guild.id][y-1][x-1] = self.chess[self.go_round[ctx.guild.id]]
            else:
                await ctx.send(embed=embed_base(ctx, title="This position is occupied", color="red", author=False))
                raise

            # Check win and print board
            check = await self.go_checkwin(ctx)
            self.go_round[ctx.guild.id] ^= 1
            if check:
                del self.start[ctx.guild.id]
                await ctx.send(embed=embed_base(ctx, title=f"{ctx.message.author.name} Win!!!", color="green", author=False))
            else: await self.printBoard(ctx)
        except Exception as e:
            print(e)
    
    async def go_checkwin(self, ctx):
        for i in range(self.size[ctx.guild.id]):
            for j in range(self.size[ctx.guild.id]):
                if self.board[ctx.guild.id][i][j] == self.chess[self.go_round[ctx.guild.id]]:
                    try:
                        if self.board[ctx.guild.id][i][j] == self.board[ctx.guild.id][i][j+1] == self.board[ctx.guild.id][i][j+2] == self.board[ctx.guild.id][i][j+3] == self.board[ctx.guild.id][i][j+4]: return True
                        elif self.board[ctx.guild.id][i][j] == self.board[ctx.guild.id][i+1][j] == self.board[ctx.guild.id][i+2][j] == self.board[ctx.guild.id][i+3][j] == self.board[ctx.guild.id][i+4][j]: return True
                        elif self.board[ctx.guild.id][i][j] == self.board[ctx.guild.id][i+1][j+1] == self.board[ctx.guild.id][i+2][j+2] == self.board[ctx.guild.id][i+3][j+3] == self.board[ctx.guild.id][i+4][j+4]: return True
                        elif self.board[ctx.guild.id][i][j] == self.board[ctx.guild.id][i-1][j-1] == self.board[ctx.guild.id][i-2][j-2] == self.board[ctx.guild.id][i-3][j-3] == self.board[ctx.guild.id][i-4][j-4]: return True
                    except Exception as e:
                        print(e)
        return False
    
    @commands.command(name="codestart")
    async def codestart(self, ctx):
        try:
            # Initial
            self.code_answer[ctx.guild.id] = random.sample(range(1, 26), 25)
            with open("./data/words.txt", "r", encoding="utf-8") as f:
                data = f.readlines()
            f.close()
            self.text[ctx.guild.id] = random.sample(data, 25)
            self.code_check[ctx.guild.id] = [0 for _ in range(25)]
            
            # Draw the code_answer
            img = np.zeros((520, 520, 3), np.uint8)
            img.fill(255)
            for v in range(25):
                i = v // 5
                j = v % 5
                if self.code_answer[ctx.guild.id][v] < 9: cv2.rectangle(img, (i*100+10, j*100+10), (i*100+110, j*100+110), (0, 0, 200), -1)
                elif self.code_answer[ctx.guild.id][v] < 16: cv2.rectangle(img, (i*100+10, j*100+10), (i*100+110, j*100+110), (200, 0, 0), -1)
                elif self.code_answer[ctx.guild.id][v] == 16:cv2.rectangle(img, (i*100+10, j*100+10), (i*100+110, j*100+110), (30, 30, 30), -1)
                else: cv2.rectangle(img, (i*100+10, j*100+10), (i*100+110, j*100+110), (128, 128, 128), -1)
                cv2.rectangle(img, (i*100+10, j*100+10), (i*100+110, j*100+110), (0, 0, 0), 5)
            
            # Add Chinese Text
            imgPIL = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            drawPIL = ImageDraw.Draw(imgPIL)
            fontText = ImageFont.truetype("font/simsun.ttc", 26, encoding="utf-8")
            for v in range(25):
                i = v // 5
                j = v % 5
                if len(self.text[ctx.guild.id][v]) == 2: drawPIL.text((i*100+10+(37), j*100+10+(37)), self.text[ctx.guild.id][v][:-1], (255, 255, 255), font=fontText)
                if len(self.text[ctx.guild.id][v]) == 3: drawPIL.text((i*100+10+(24), j*100+10+(37)), self.text[ctx.guild.id][v][:-1], (255, 255, 255), font=fontText)
                if len(self.text[ctx.guild.id][v]) == 4: drawPIL.text((i*100+10+(11), j*100+10+(37)), self.text[ctx.guild.id][v][:-1], (255, 255, 255), font=fontText)
                if len(self.text[ctx.guild.id][v]) == 5: drawPIL.text((i*100+10+(0), j*100+10+(37)), self.text[ctx.guild.id][v][:-1], (255, 255, 255), font=fontText)
            imgPutText = cv2.cvtColor(np.asarray(imgPIL), cv2.COLOR_RGB2BGR)
            cv2.imwrite(f"./tmp/{ctx.guild.id}_answer.png", imgPutText)

            await ctx.send(embed=embed_base(ctx, title="BiBi is ready for Codenames", description="Are you ready for challenge??\n\n (( ◞•̀д•́)◞⚔◟(•̀д•́◟ ))", color="green", author=False))
            await self.code(ctx, "", True)
        except Exception as e:
            print(e)
    
    @commands.command(name="host")
    async def host(self, ctx):
        try:
            if ctx.guild.id not in self.code_answer:
                await ctx.send(embed=embed_base(ctx, title="BiBi is not ready (ಠ ∩ಠ)", color="red", author=False))
                raise

            picture = discord.File(f"./tmp/{ctx.guild.id}_answer.png")
            await ctx.author.send(file=picture)
            await ctx.send(embed=embed_base(ctx, title=f"{ctx.author.name} be the host", color="green", author=False))
        except Exception as e:
            print(e)

    @commands.command(name="code")
    async def code(self, ctx, co, initial=False):
        try:
            # Initial
            if initial == True:
                img = np.zeros((520, 520, 3), np.uint8)
                img.fill(255)
                for v in range(25):
                    i = v // 5
                    j = v % 5
                    cv2.rectangle(img, (i*100+10, j*100+10), (i*100+110, j*100+110), (0, 0, 0), 5)

                # Add Chinese Text
                imgPIL = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                drawPIL = ImageDraw.Draw(imgPIL)
                fontText = ImageFont.truetype("font/simsun.ttc", 26, encoding="utf-8")
                for v in range(25):
                    i = v // 5
                    j = v % 5
                    if len(self.text[ctx.guild.id][v]) == 2: drawPIL.text((i*100+10+(37), j*100+10+(37)), self.text[ctx.guild.id][v][:-1], (0, 0, 0), font=fontText)
                    if len(self.text[ctx.guild.id][v]) == 3: drawPIL.text((i*100+10+(24), j*100+10+(37)), self.text[ctx.guild.id][v][:-1], (0, 0, 0), font=fontText)
                    if len(self.text[ctx.guild.id][v]) == 4: drawPIL.text((i*100+10+(11), j*100+10+(37)), self.text[ctx.guild.id][v][:-1], (0, 0, 0), font=fontText)
                    if len(self.text[ctx.guild.id][v]) == 5: drawPIL.text((i*100+10+(0), j*100+10+(37)), self.text[ctx.guild.id][v][:-1], (0, 0, 0), font=fontText)
                imgPutText = cv2.cvtColor(np.asarray(imgPIL), cv2.COLOR_RGB2BGR)
                cv2.imwrite(f"./tmp/{ctx.guild.id}_text.png", imgPutText)

                picture = discord.File(f"./tmp/{ctx.guild.id}_text.png")
                await ctx.send(file=picture)
                raise

            # Guess
            if ctx.guild.id not in self.text:
                await ctx.send(embed=embed_base(ctx, title="BiBi is not ready (ಠ ∩ಠ)", color="red", author=False))
                raise
            elif (co+"\n") not in self.text[ctx.guild.id]:
                await ctx.send(embed=embed_base(ctx, title="This word is not in board", color="red", author=False))
                raise
            elif self.code_check[ctx.guild.id][self.code_answer[ctx.guild.id][self.text[ctx.guild.id].index(co+"\n")]-1] == 1:
                await ctx.send(embed=embed_base(ctx, title="This text has been decoded", author=False))
                raise
            else:
                img = cv2.imread(f"./tmp/{ctx.guild.id}_text.png")
                idx = self.text[ctx.guild.id].index(co+"\n")
                i = idx // 5
                j = idx % 5
                if self.code_answer[ctx.guild.id][idx] < 9: cv2.rectangle(img, (i*100+10, j*100+10), (i*100+110, j*100+110), (0, 0, 200), -1)
                elif self.code_answer[ctx.guild.id][idx] < 16: cv2.rectangle(img, (i*100+10, j*100+10), (i*100+110, j*100+110), (200, 0, 0), -1)
                elif self.code_answer[ctx.guild.id][idx] == 16: cv2.rectangle(img, (i*100+10, j*100+10), (i*100+110, j*100+110), (30, 30, 30), -1)
                else: cv2.rectangle(img, (i*100+10, j*100+10), (i*100+110, j*100+110), (128, 128, 128), -1)
                cv2.rectangle(img, (i*100+10, j*100+10), (i*100+110, j*100+110), (0, 0, 0), 5)
                self.code_check[ctx.guild.id][self.code_answer[ctx.guild.id][idx]-1] = 1

                # Add Chinese Text
                imgPIL = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                drawPIL = ImageDraw.Draw(imgPIL)
                fontText = ImageFont.truetype("font/simsun.ttc", 26, encoding="utf-8")
                if len(self.text[ctx.guild.id][idx]) == 2: drawPIL.text((i*100+10+(37), j*100+10+(37)), self.text[ctx.guild.id][idx][:-1], (255, 255, 255), font=fontText)
                if len(self.text[ctx.guild.id][idx]) == 3: drawPIL.text((i*100+10+(24), j*100+10+(37)), self.text[ctx.guild.id][idx][:-1], (255, 255, 255), font=fontText)
                if len(self.text[ctx.guild.id][idx]) == 4: drawPIL.text((i*100+10+(11), j*100+10+(37)), self.text[ctx.guild.id][idx][:-1], (255, 255, 255), font=fontText)
                if len(self.text[ctx.guild.id][idx]) == 5: drawPIL.text((i*100+10+(0), j*100+10+(37)), self.text[ctx.guild.id][idx][:-1], (255, 255, 255), font=fontText)
                imgPutText = cv2.cvtColor(np.asarray(imgPIL), cv2.COLOR_RGB2BGR)
                cv2.imwrite(f"./tmp/{ctx.guild.id}_text.png", imgPutText)

                check = await self.code_checkWin(ctx)
                picture = discord.File(f"./tmp/{ctx.guild.id}_text.png")
                await ctx.send(file=picture)
                if check == 1:
                    await self.cleanCode(ctx)
                    await ctx.send(embed=embed_base(ctx, title="Red Team Wins", author=False))
                elif check == 2:
                    await self.cleanCode(ctx)
                    await ctx.send(embed=embed_base(ctx, title="Blue Team Wins", author=False))
                elif check == 3:
                    await self.cleanCode(ctx)
                    await ctx.send(embed=embed_base(ctx, title="Game Over", author=False))
        except Exception as e:
            print(e)

    async def code_checkWin(self, ctx):
        red = sum(self.code_check[ctx.guild.id][:8])
        blue = sum(self.code_check[ctx.guild.id][8:15])
        black = self.code_check[ctx.guild.id][15]
        if red == 8: return 1
        elif blue == 7: return 2
        elif black: return 3
        else: return 0

    async def cleanCode(self, ctx):
        os.remove(f"./tmp/{ctx.guild.id}_text.png")
        os.remove(f"./tmp/{ctx.guild.id}_answer.png")
        del self.text[ctx.guild.id]
        del self.code_answer[ctx.guild.id]
        del self.code_check[ctx.guild.id]

    @commands.command(name="game_help")
    async def game_help(self, ctx):
        try:
            help_message = """
# Game Command (`;`)
```
AB Game:
-abstart           : start the AB game
-(g)uess <number>  : guess the 4-digit number

Gomoku:
-gostart           : start the Gomoku
-place <x> <y>     : place at (x, y)

Codenames:
-codestart         : start the Codenames
-host              : host use this command to get the answer
-code <code>       : guess <code> be author's team code

<> = required information, [] = optional information
```
            """
            await ctx.send(embed=embed_base(ctx, description=help_message, color="orange", author=False))
        except Exception as e:
            print(e)

async def setup(bot):
    await bot.add_cog(Game(bot))