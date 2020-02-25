from evennia import create_object
import random
import markovify
from evennia.prototypes.spawner import spawn

class Item:
    def __init__(self, substance):
        self.seed = 0
        self.name = "horse"
        self.kind = "Human"
        self.description = "A lovely toy horse"
        self.typeclass = typeclasses.objects.Object

    def GenerateItem(self):
        itemType = random.randint(0, 4)
        if itemType <= 2:
            self.generateTalisman()
        elif itemType == 3:
            self.generateBook()
        else:
            self.generateGarment() 

    self.item_proto = {
        "key": self.name,
        "typeclass": self.typeclass,
        "desc": self.description,
        "location": caller.location
    }
    
    def generateGarment(self):
        clothesFO = open("clothes.txt")
        clothesList = list(clothesFO)
        color = self.getColor();
        clothesSelection = random.randint(0, len(clothesList) - 1)
        clothingItem = clothesList[clothesSelection]
        clothingItem = clothingItem.rstrip("\n")
        self.name = clothingItem
        clothingDescription = color + " " + clothingItem
        clothingDescription = self.addAorAn(clothingItem)
        self.description = clothingDescription
        clothesFO.close()


    def GenerateTalisman(substance):
        talismanDescription = " "
        random.seed(self.seed)
        color = self.getColor()
        substance = self.getSubstance()
        adjective = self.getAdjective()
        talismanFO = open("word_lists/talismans.txt")
        talismanList = list(talismanFO)
        selection = random.randint(0, len(talismanList) - 1)
        talisman = talismanList[selection]
        talisman = item.rstrip("\n")
        talismanFO.close()
        self.name = talisman
        anAdvective = self.addAorAn(adjective)
        self.description = anAdvective + " " + talisman + " made of " + color + substance + "."

    
    def generateSciFiBook(self):
        bookText = " "
        bookDescription = "A paperback book"
        random.seed(self.seed)
        color = self.getColor();
        bookCorpusFO = open("scifi_book_corpus.txt")
        text = bookCorpusFO.read()
        text_model = markovify.NewlineText(text)
        for i in range(4):
            try:
                bookText += text_model.make_sentence(tries=100) + " "
            except TypeError:
                bookText += "A fine book about rockets. "
        bookCorpusFO.close()
        self.name = color + "book"
        self.description = bookDescription
        self.db.readable_text = bookText
        self.typeclass = typeclasses.objects.Readable


    def getSubstance(self):
        substanceFO = open("substances.txt")
        substanceList = list(substanceFO)
        selection = random.randint(0, len(substanceList) - 1)
        substance = substanceList[selection]
        substance = substance.rstrip("\n")
        return substance

    def getFeature(self):
        featureFO = open("features.txt")
        featureList = list(featureFO)
        selection = random.randint(0, len(featureList) - 1)
        substance = featureList[selection]
        substance = feature.rstrip("\n")
        return feature


    def getAdjective(self, reversed):
        adjectiveFO = open("adjectives.txt")
        adjectiveList = list(adjectiveFO)
        selection = random.randint(0, len(adjectiveList) - 1)
        if reversed == True:
            adjective = adjectiveList[-selection]
        else:
            adjective = adjectiveList[selection]
        adjective = adjective.rstrip("\n")
        return adjective

    def getColor(self):
        random.seed(self.seed)
        colorsFO = open("colors.txt")
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

 
newItem = itemator.Item()
newItem.generateItem(seed)
print(newItem)
spawn(self.item_proto)
