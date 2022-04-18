"""
Generate a prefix tree to process the escape codes 

this is take 2 , this was done in action.py with switch tables
"""
# lifted from https://algotree.org/algorithms/trie_python_java/

from .tree import Tree

escape_codes = {}


class TrieNode:
    """A trie node"""

    def __init__(self, char):

        # Character stored in this node
        self.char = char

        # A flag that marks if the word ends on this particular node.
        self.end_of_word = False

        # A dictionary of child nodes where the keys are the characters (letters)
        # and values are the nodes
        self.children = {}


class Trie:
    """The trie structure"""

    def __init__(self):
        """
        The root node of a trie is empty and does not store any character.
        """
        self.root = TrieNode("")

    def Insert(self, string):
        """Insert a string i.e a word into the trie"""
        node = self.root

        # Check each character in the string
        # If none of the children of the current node contains the character,
        # create a new child of the current node for storing the character.
        for char in string:
            if char in node.children:
                node = node.children[char]
            else:
                # As the character is not found, create a new trie node
                new_node = TrieNode(char)
                node.children[char] = new_node
                node = new_node

        # Mark the end of a word
        node.end_of_word = True

    def Search(self, string):
        """Search a string i.e search a word in the trie"""
        node = self.root

        # Check each character in the string
        # If none of the children of the node contains the character,
        # Return none
        for char in string:
            if char in node.children:
                node = node.children[char]
            else:
                node = None
                break

        return node

    def PrintLexical(self, node, prefix, suffix):
        """Print words in the Trie in lexical order"""

        if node.end_of_word == True and len(suffix):
            print(prefix + suffix)

        # Iterate through all the nodes in the dictionary
        # key is the character and children[key] is the child node
        for key in node.children:
            temp = suffix
            child = node.children[key]
            temp += key
            self.PrintLexical(child, prefix, temp)


def main():

    t = Trie()
    t.Insert("we")
    t.Insert("walk")
    t.Insert("want")
    t.Insert("wish")
    t.Insert("wit")
    t.Insert("am")
    t.Insert("yo")
    t.Insert("will")
    t.Insert("wee")
    t.Insert("war")
    t.Insert("win")
    t.Insert("warp")

    # Search for a prefix in the Trie

    prefix = input("Enter prefix : ")

    node = t.Search(prefix)

    if node == None or node == t.root:
        print("No words with matching prefix found")
    else:
        # Prefix has been found in the Trie. Now look for children
        if len(node.children):
            print("Words with prefix : " + prefix)
            t.PrintLexical(node, prefix, "")
        else:
            print("Just the prefix exists in the Trie, but not the matching words")


if __name__ == "__main__":
    main()
