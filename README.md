# SPORK 

This is some nmigen infrastructure for the Boneless-v3 gateware CPU

The 'spork' folder has the current sections

## cores

    Elboratable Gateware

## cpu

    A Boneless-v3 with a 16bit CSR bus

## firmware

    Scaffolding and structure for building binaries

# lib

    Some function librariesies

# peripheral

    Gateware that will name and connect to the CSR bus

# utils



TODO

- [X] Use checksum on HexLoader
- [X] ANSI terminal codes
- [X] Command search
- [ ] RLE encode the banner
- [ ] Debug Symbols
- [ ] Tree menu on commands !! see radix tree
- [X] Escape code parser
- [ ] Triple check the bootload sequence
- [X] Fix the warmboot fail

HEXLOADER

- [ ] Timeout
- [ ] : id starter
- [X] Checksum with - no blanking 
- [X] as a SubR for multi boot ! need to block and ROM
