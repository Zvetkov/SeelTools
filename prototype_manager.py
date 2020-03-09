class PrototypeManager(object):
    def __init__(self):
        self.Clear()
        self.prototypes = []
        self.prototypeNamesToIds = {}  # int: int
        self.prototypeFullNamesLocalizedForms = {}  # unsgn_int:unsgn_int
        self.prototypeFullNames = {}  # str:str
        self.loadingLock = 0

    def Clear(self):
        pass

    def LoadFromXMLFile(self, fileName):
        self.loadingLock += 1
        self._LoadGameObjectsFolderFromXML(fileName, self._ReadNewPrototype())
        self.loadingLock -= 1
        for prototype in self.prototypes:
            prototype.PostLoad()

    def _LoadGameObjectsFolderFromXML(self, fileName):
        pass
