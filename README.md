# SPORK 

This is some nmigen infrastructure for the Boneless-v3 gateware CPU

The 'spork' folder has the current sections

##cores/

    Elboratable Gateware

##cpu/

    A Boneless-v3 with a 16bit CSR bus

##firmware/

    Scaffolding and structure for building binaries

#lib/

    Some ASM lib.

#peripheral/

    Gateware that will name and connect to the CSR bus

#utils/



TODO

- [ ] Use checksum on HexLoader
- [ ] ANSI terminal codes
- [ ] Command search
- [ ] RLE encode the banner
- [ ] Debug Symbols
- [ ] Tree menu on commands
- [ ] Escape code parser
- [ ] Triple check the bootload sequence
- [ ] Fix the warmboot fail

HEXLOADER

- [ ] Timeout
- [ ] : id starter
- [ ] Checksum with blanking
- [ ] as a SubR for multi boot
