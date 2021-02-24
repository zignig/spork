fwtest.py:141:# TODO this needs to be moved into the spork
fwtest.py:146:    # TODO abstract this plaform set
fwtest.py:185:# TODO this main needs to be moved below the spork.
spork/peripheral/switch.py:3:# TODO , bind multiple switches
spork/firmware/runtime.py:66:#TODO align 8
spork/firmware/allocator.py:184:            # TODO add in window pointer and jump target
spork/firmware/allocator.py:199:        # TODO move this into the allocator
spork/firmware/base.py:125:    # TODO make this sequential
spork/firmware/base.py:273:    # TODO spill and reuse registers
spork/firmware/base.py:346:        self._size = 8  # for later ( stack frames ) TODO
spork/firmware/base.py:383:        # TODO this will need to be rewritten for the allocator
spork/firmware/base.py:432:        # TODO This needs to change for the allocator
spork/lib/uartIO.py:362:            MOVR(w.endpoint, "end_of_data"),  # TODO share full mem size into SubR
spork/lib/console.py:30:# TODO add a working cursor
spork/lib/console.py:38:    # TODO hard fail on overflow
spork/lib/console.py:188:                    # TODO make this a vector
spork/lib/console.py:198:        # TODO if not handle other
spork/lib/commands.py:24:# TODO , convert to radix tree ?
spork/lib/commands.py:115:                # TODO , restructure the headers
spork/lib/commands.py:234:    # TODO pass down chomped strings
spork/cores/periph/bus.py:14:    # TODO export in various formats
spork/cores/periph/bus.py:70:            # TODO this makes a double decoder
spork/cores/warmboot.py:27:        # TODO fix the internal selector
bootloader.py:5:# TODO port to allocator IR
bootloader.py:26:# TODO compress the banner, it is phat.
bootloader.py:44:    # TODO find best way to attach this to the peripherals.
bootloader.py:122:    # TODO check requirements
Binary file __pycache__/hexloader.cpython-37.pyc matches
hexloader.py:18:# TODO
hexloader.py:84:            Rem("TODO, fix checksum"),
hexloader.py:157:        # TODO , make the target
