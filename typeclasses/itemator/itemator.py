from evennia import create_object, DefaultObject
import evennia.contrib.clothing
from evennia import default_cmds
import random
import markovify
from django.conf import settings



class Item(DefaultObject):
    
    def getSubstance(self):
        substanceFO = open("typeclasses/itemator/word_lists/substances.txt")
        substanceList = list(substanceFO)
        selection = random.randint(0, len(substanceList) - 1)
        substance = substanceList[selection]
        substance = substance.rstrip("\n")
        return substance

    def getAdjective(self):
        adjectiveFO = open("typeclasses/itemator/word_lists/adjectives.txt")
        adjectiveList = list(adjectiveFO)
        selection = random.randint(0, len(adjectiveList) - 1)
        adjective = adjectiveList[selection]
        adjective = adjective.rstrip("\n")
        return adjective

    def getColor(self):
        colorsFO = open("typeclasses/itemator/word_lists/colors.txt")
        colorsList = list(colorsFO)
        colorsSelection = random.randint(0, len(colorsList) - 1)
        color = colorsList[colorsSelection]
        color = color.rstrip("\n")
        colorsFO.close()
        return color

    def addAorAn(self, word):
        if word[-1] != "s" and word[0] == "a" or word[0] == "e" or word[0] == "i" or word[0] == "o" or word[0] == "u":
            word = "an " + word
        elif word[-1] != "s":
            word = "a " + word
        return word

    def generateItem(self):
        
        itemType = random.randint(0, 4)
        if itemType <= 2:
            self.item_proto = self.generateTalisman()
        else:
            self.item_proto = self.generateGarment()

        return self.item_proto
    
    def generateGarment(self):
        clothesFO = open("typeclasses/itemator/word_lists/clothes.txt")
        clothesList = list(clothesFO)
        color = self.getColor()
        clothesSelection = random.randint(0, len(clothesList) - 1)
        clothingItem = clothesList[clothesSelection]
        clothingItem = clothingItem.rstrip("\n")
        self.item_name = clothingItem
        clothingDescription = color + " " + clothingItem
        clothingDescription = self.addAorAn(clothingItem)
        self.item_description = clothingDescription
        clothesFO.close()
        self.item_proto = {
            "key": self.item_name,
            "typeclass": evennia.contrib.clothing.Clothing,
            "desc": self.item_description,
        }
        return self.item_proto


    def generateTalisman(self):
        color = self.getColor()
        substance = self.getSubstance()
        adjective = self.getAdjective()
        talismanFO = open("typeclasses/itemator/word_lists/talismans.txt")
        talismanList = list(talismanFO)
        selection = random.randint(0, len(talismanList) - 1)
        talisman = talismanList[selection]
        talisman = talisman.rstrip("\n")
        talismanFO.close()
        self.item_name = talisman
        anAdjective = self.addAorAn(adjective)
        self.item_description = anAdjective + " " + \
            talisman + " made of " + color + substance + "."
        self.item_proto = {
            "key": self.item_name,
            "typeclass": "typeclasses.objects.Object",
            "desc": self.item_description,
        }
        return self.item_proto

    """  
    def generateSciFiBook(self):
        bookText = " "
        bookDescription = "A paperback book"
        color = self.getColor()
        bookCorpusFO = open("typeclasses/itemator/word_lists/scifi_book_corpus.txt")
        text = bookCorpusFO.read()
        text_model = markovify.NewlineText(text)
        for i in range(4):
            try:
                bookText += text_model.make_sentence(tries=100) + " "
            except TypeError:
                bookText += "A fine book about rockets. "
        bookCorpusFO.close()
        self.item_name = color + "book"
        self.item_description = bookDescription
        self.db.readable_text = bookText
        self.item_typeclass = "typeclasses.objects.Readable" """

    
    
