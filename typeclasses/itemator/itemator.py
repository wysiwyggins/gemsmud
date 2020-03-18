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

    def getSkill(self):
        skillsFO = open("typeclasses/itemator/word_lists/skills.txt")
        skillsList = list(skillsFO)
        selection = random.randint(0, len(skillsList) - 1)
        skill = skillsList[selection]
        skill = skill.rstrip("\n")
        return skill
    
    def getArtwork(self):
        artworksFO = open("typeclasses/itemator/word_lists/artworks.txt")
        artworksList = list(artworksFO)
        selection = random.randint(0, len(artworksList) - 1)
        artwork = artworksList[selection]
        artwork = artwork.rstrip("\n")
        return artwork

    def getTheme(self):
        themesFO = open("typeclasses/itemator/word_lists/epicThemes.txt")
        themesList = list(themesFO)
        themesSelection = random.randint(0, len(themesList) - 1)
        theme = themesList[themesSelection]
        theme = theme.rstrip("\n")
        themesFO.close()
        return theme

    def getVerb(self):
        verbsFO = open("typeclasses/itemator/word_lists/artSpeakVerbs.txt")
        verbsList = list(verbsFO)
        verbsSelection = random.randint(0, len(verbsList) - 1)
        verb = verbsList[verbsSelection]
        verb = verb.rstrip("\n")
        verbsFO.close()
        return verb
    
    def getTitle(self):
        titlesFO = open("typeclasses/itemator/word_lists/artTitles.txt")
        titlesList = list(titlesFO)
        titlesSelection = random.randint(0, len(titlesList) - 1)
        title = titlesList[titlesSelection]
        title = title.rstrip("\n")
        title = title.title()
        titlesFO.close()
        return title
    
    def getTitleTwo(self):
        titlesTwoFO = open("typeclasses/itemator/word_lists/artTitles2.txt")
        titlesTwoList = list(titlesTwoFO)
        titlesTwoSelection = random.randint(0, len(titlesTwoList) - 1)
        titleTwo = titlesTwoList[titlesTwoSelection]
        titleTwo = titleTwo.rstrip("\n")
        titleTwo = titleTwo.title()
        titlesTwoFO.close()
        return titleTwo

    def addAorAn(self, word):
        try:
            if word[-1] != "s" and word[0] == "a" or word[0] == "e" or word[0] == "i" or word[0] == "o" or word[0] == "u":
                word = "An " + word
            elif word[-1] != "s":
                word = "A " + word
        except IndexError:
            word = "One " + word
        return word

    def generateItem(self):
        
        itemType = random.randint(0, 5)
        if itemType <= 2:
            self.item_proto = self.generateTalisman()
        elif itemType == 3:
            self.item_proto = self.generateArt()
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
        clothingDescription = self.addAorAn(color) + " " + clothingItem
        self.item_description = clothingDescription
        clothesFO.close()
        self.item_proto = {
            "key": self.item_name,
            "typeclass": "evennia.contrib.clothing.Clothing",
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
            talisman + " made of " + color + " " + substance + "."
        self.item_proto = {
            "key": self.item_name,
            "typeclass": "typeclasses.objects.Object",
            "desc": self.item_description,
        }
        return self.item_proto

    def generateArt(self):
        r = random.randint(0, 5)
        g = random.randint(0, 5)
        b = random.randint(0, 5)
        roll = random.randint(0, 20)
        color = self.getColor()
        substance = self.getSubstance()
        adjective = self.getAdjective()
        artwork = self.getArtwork()
        title = self.getTitle()
        titleTwo = self.getTitleTwo()
        skill = self.getSkill()
        key = title + " " + titleTwo
        textcolor = "|" + str(r) + str(g) + str(b)
        verb = self.getVerb()
        theme = self.getTheme()
        anAdjective = self.addAorAn(adjective)
        self.item_key = key
        if roll <= 10:
            self.item_description = textcolor + "'" + key + "'|n" + ": \n" + anAdjective + " piece of " + artwork + " created from " + color + " " + substance + ". " + "It's a masterful work of " + skill + " as it " + verb + " " + theme + "."
            self.item_proto = {
                "key": self.item_key,
                "typeclass": "typeclasses.objects.Object",
                "desc": self.item_description,
                "artwork": "true",
            }
        if roll >= 19:
            self.item_description = "|500" + "'" + key + "'|n" + ": \n |401 An unspeakable anathema |n " + artwork + " forged in " + color + " " + substance + ". " + "It embodies profane " + skill + " as it " + verb + " " + theme + "."
            self.item_proto = {
                "key": self.item_key,
                "typeclass": "typeclasses.objects.Object",
                "desc": self.item_description,
                "artwork": "true",
                "cursed": "true",
            }
        else:
            self.item_description = textcolor + "'" + key + "'|n" + ": \n" + anAdjective + " example of " + artwork + " rendered in " + color + " " + substance + ". " + "It displays considerable " + skill + " as it " + verb + " " + theme + "."
            self.item_proto = {
                "key": self.item_key,
                "typeclass": "typeclasses.objects.Object",
                "desc": self.item_description,
                "artwork": "true",
            }
        return self.item_proto


""" Doesn't seem to be working yet, evennia/evennia/prototypes/prototypes.py", line 89, in homogenize_prototype

    def generateSciFiBook(self):
        self.book_text = " "
        self.bookDescription = "A paperback book"
        color = self.getColor()
        bookCorpusFO = open("typeclasses/itemator/word_lists/scifi_book_corpus.txt")
        text = bookCorpusFO.read()
        text_model = markovify.NewlineText(text)
        self.book_name = color + "book"
        for i in range(4):
            try:
                self.book_text += text_model.make_sentence(tries=100) + " "
            except TypeError:
                self.book_text += "A fine book about rockets. "
        bookCorpusFO.close()
        self.item_proto = {
            "key": self.book_name,
            "typeclass": "typeclasses.objects.Readable",
            "desc": self.bookDescription,
            "readable_text": self.book_text,
        }

"""
    
