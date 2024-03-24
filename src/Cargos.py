from status import CargoAction


class CARGO:
    def __init__(self, cargo_name, group, density):
        self.__cargoName = cargo_name
        self.__currentWeight = 0
        self.__currentCom = None
        self.__density = density
        self.__group = group
        self.__nextAction = CargoAction.NONE
        self.__timeline = [None, None]

    def set_currentWeight(self, weight):
        self.__currentWeight = weight

    def add_weight(self, weight):
        self.__currentWeight += weight
        return self.__currentWeight

    def set_currentCom(self, com):
        self.__currentCom = com

    @property
    def get_cargoName(self):
        return self.__cargoName

    @property
    def get_current_weight(self):
        return self.__currentWeight

    @property
    def get_density(self):
        return self.__density

    @property
    def get_cargoGroup(self):
        return self.__group

    @property
    def get_currentCom(self):
        return self.__currentCom

class CARGOS:
    def __init__(self, cargoLs=()):
        self.__cargos = dict()
        if len(cargoLs) > 0:
            self.initCargos(cargoLs)

    def initCargos(self, cargoLs, cargo_group_dic):
        for cargo in cargoLs:
            self.__cargos[cargo] = CARGO(cargo, cargo_group_dic[cargo])

    @property
    def CARGOS(self) -> dict:
        return self.__cargos
