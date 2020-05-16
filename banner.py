
banner = """
┌────────────────────────────────────────────────┐
│░░░█▀▄░█▀█░█▀█░█▀▀░█░░░█▀▀░█▀▀░█▀▀░░░░░█░█░▀▀█░░│
│░░░█▀▄░█░█░█░█░█▀▀░█░░░█▀▀░▀▀█░▀▀█░░░░░▀▄▀░░▀▄░░│
│░░░▀▀░░▀▀▀░▀░▀░▀▀▀░▀▀▀░▀▀▀░▀▀▀░▀▀▀░▀▀▀░░▀░░▀▀░░░│
└────────────────────────────────────────────────┘
"""
text_command = 'toilet -F border -f pagga " Boneless_V3 "'


class Encoder:
    def __init__(self, text_object):
        self.text = text_object
        self.char_list = self.char_list()
        self.len = len(self.char_list)

    def char_list(self):
        dict = {}
        for i in self.text:
            if i not in dict:
                dict[i] = 1
            else:
                dict[i] += 1
        return dict


if __name__ == "__main__":
    e = Encoder(banner)
    cl = e.char_list()
    print(cl)
