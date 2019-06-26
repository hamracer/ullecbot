import random
import sqlite3

conn = sqlite3.connect('messages.db')
c = conn.cursor()


c.execute("SELECT content from logs WHERE author_id='147659601658118144' AND channel_id='339155308767215618'")
conn.commit()

data = c.fetchall()

# print(data)
allthedata = []
for f in data:
    f = ''.join(f)
    f.replace(',', '')
    if len(f) < 3:
        continue
    elif 'http' in f:
        continue
    elif '.gif' in f:
        continue
    elif '.png' in f:
        continue
    elif '.jpg' in f:
        continue
    else:
        allthedata.append(f)

allthedata = '. '.join(allthedata)
with open("corpus.txt", "w", encoding="utf-8") as file:
    file.write(allthedata)


class Markov(object):


    def __init__(self, order):  # receive the values
        self.order = order
        self.group_size = self.order + 1
        self.text = None
        self.graph = {}
        return


    def train(self, filename):  # receive the text file
        self.text = (filename).read().split()
        self.text = self.text + self.text[: self.order]
        for i in range(0, len(self.text) - self.group_size):
            key = tuple(self.text[i: i + self.order])
            value = self.text[i + self.order]
            if key in self.graph:
                self.graph[key].append(value)
            else:
                self.graph[key] = [value]
        return


    def generate(self, length):
        index = random.randint(0, len(self.text) - self.order)
        result = self.text[index: index + self.order]  # choose a random point to start
        for i in range(length):
            state = tuple(result[len(result) - self.order:])
            next_word = random.choice(self.graph[state])
            result.append(next_word)
        return " ".join(result[self.order:])

x = Markov(2)

file = open("corpus.txt", "r", encoding="utf-8")
filename = file

x.train(filename)
yay =x.generate(21)

# yayers = yay.replace('.','.\ibot:')
print("Snacksbot: " + yay)
