class Wait(SubR):
    def setup(self):
        self.params = ["value"]
        self.locals = ["counter"]

    def instr(self):
        w = self.w
        ll = LocalLabels()
        return [
            MOV(w.counter, w.value),
            ll("wait"),
            SUBI(w.counter, w.counter, 1),
            CMPI(w.counter, 0),
            BNE(ll.wait),
        ]
