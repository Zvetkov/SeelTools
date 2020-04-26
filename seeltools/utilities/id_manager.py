
class IdManager(object):
    def __init__(self):
        self.id_list = []

    def GetUniqueId(self):
        new_id = len(self.id_list) + 1
        self.id_list.append(new_id)
        return new_id


theIdManager = IdManager()
