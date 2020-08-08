banner = """
┌────────────────────────────────────────────────┐
│░░░█▀▄░█▀█░█▀█░█▀▀░█░░░█▀▀░█▀▀░█▀▀░░░░░█░█░▀▀█░░│
│░░░█▀▄░█░█░█░█░█▀▀░█░░░█▀▀░▀▀█░▀▀█░░░░░▀▄▀░░▀▄░░│
│░░░▀▀░░▀▀▀░▀░▀░▀▀▀░▀▀▀░▀▀▀░▀▀▀░▀▀▀░▀▀▀░░▀░░▀▀░░░│
└────────────────────────────────────────────────┘
"""
text_command = 'toilet -F border -f pagga " Boneless_V3 "'

banner = """
┌───────────────────────────────────────┐
│   ┏┓ ┏━┓┏┓╻┏━╸╻  ┏━╸┏━┓┏━┓   ╻ ╻┏━┓   │
│   ┣┻┓┃ ┃┃┗┫┣╸ ┃  ┣╸ ┗━┓┗━┓   ┃┏┛╺━┫   │
│   ┗━┛┗━┛╹ ╹┗━╸┗━╸┗━╸┗━┛┗━┛╺━╸┗┛ ┗━┛   │
└───────────────────────────────────────┘
"""


class Encoder:
    def __init__(self, text_object):
        self.text = text_object
        self.breakdown = self.symbol_list()
        self.len = len(self.breakdown)
        self.slide_dict = {}

        self.enc = []
        self.rle()

        self.symbols()

    def symbol_list(self):
        dict = {}
        for i in self.text:
            if i not in dict:
                dict[i] = 1
            else:
                dict[i] += 1
        return dict

    def slide(self, length):
        "unused"
        for i in range(len(self.text)):
            v = self.text[i : i + length]
            if v not in self.slide_dict:
                self.slide_dict[v] = 1
            else:
                self.slide_dict[v] += 1

    def chunk(self, start=2, finish=20):
        "unused"
        for i in range(start, finish):
            self.slide(i)

    def clean(self, l=2):
        "unused"
        c = self.slide_dict.copy()
        sd = self.slide_dict
        for i in sd:
            if sd[i] <= l:
                del (c[i])
        self.slide_dict = c

    def symbols(self):
        for i in self.breakdown:
            val = i.encode("utf-8")
            print(i, val)

    def rlerle(self, depth=3):
        log.critical("Check for RLE patterns")

    def rle(self, max_chunk=256):
        cur = self.text[0]
        count = 1
        for i in range(1, len(self.text)):
            if (self.text[i] == cur) and (count < max_chunk):
                count += 1
            else:
                self.enc.append((cur, count))
                count = 1
                cur = self.text[i]


if __name__ == "__main__":
    e = Encoder(banner)
    cl = e.breakdown
    print("Unecoded", len(banner.encode("utf-8")))
    print("Symbols", len(cl))
    print(cl)
    print(e.enc)
    print(len(e.enc))
