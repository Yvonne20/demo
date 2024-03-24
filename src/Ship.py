import Cargos
from status import ShipStatus


class Compartment:
    def __init__(self, ship_id, shipComp_limit, com_dic):
        self.__ship_name = f'ship_{ship_id}'
        self.__ship_com = dict()
        self.__current_com = dict()

        self.init_ship_com(shipComp_limit, com_dic)
        self.init_current_com() ########

    def init_ship_com(self, ship_com, com_dic):
        for com_int in com_dic:
            self.__ship_com[com_int] = ship_com[com_int]

    def init_current_com(self):
        for com in self.__ship_com:
            self.__current_com[com] = [None, 0]  # TODO

    def set_current_com(self, current_com):
        for com in self.__ship_com:
            if com in current_com:
                self.__current_com[com] = current_com[com]

    def add_to_com(self, com_int, cargo_name, volume):
        if self.__current_com[com_int][0] and cargo_name != self.__current_com[com_int][0]:
            raise ValueError(f"Cargo Adding Error in {com_int}")
        new_volume = self.__current_com[com_int][1] + volume
        if new_volume > self.__ship_com[com_int]:
            return False
        else:
            self.__current_com[com_int][1] = new_volume
            if not self.__current_com[com_int][0]:
                self.__current_com[com_int][0] = cargo_name
            return True

    @property
    def get_ship_com(self):
        return self.__ship_com

    @property
    def get_current_com(self):
        return self.__current_com

class ShipDynamic:
    def __init__(self, ship_id, ship_cfg):
        self.__ship_static = ShipStatic(ship_id, ship_cfg)
        self.__ship_id = ship_id

        self.__currentMaxWeight = 0
        self.__current_load_weight = 0
        self.__status = ShipStatus.UNKNOWN
        self.__timestamp = 0
        self.__draft = 0
        self.__cargos = dict()  # Key: cargo, Value: Class CARGO
        self.__init_cargos = dict()  # Initialize From Initial Current Com
        self.__init_load_weight = 0
        self.__compartment = Compartment(ship_id,
                                         self.__ship_static.comp_limit,
                                         self.__ship_static.comp_dic)
        self.count = 0

    def set_cargo_ls_from_order(self, cargo_ls, cargo_dic):
        for cargo in cargo_ls:
            cargo_name = cargo.lower()
            if cargo_name not in self.__cargos:  # Add
                self.__cargos[cargo_name] = Cargos.CARGO(cargo_name,
                                                         cargo_dic[cargo_name]['group_name'],
                                                         cargo_dic[cargo_name]['density'])

    def init_timestamp(self, init_ts):
        self.__timestamp = init_ts

    def init_current_com(self, current_com, cargo_dic):
        # com: [cargo_name, cargo_group, volume, [(previous 3)]]
        for com_int in current_com:
            cargo_name = current_com[com_int]['cargo_name']
            cargo_vol = float(current_com[com_int]['vol'])
            if cargo_name:
                self.__init_cargos[cargo_name] = Cargos.CARGO(cargo_name,
                                                              cargo_dic[cargo_name]['group_name'],
                                                              cargo_dic[cargo_name]['density'])
                self.__init_load_weight += cargo_vol * self.__init_cargos[cargo_name].get_density  # TODO: Check Unit
        # TODO: Add to Ship's Com

    def set_timestamp(self, timestamp):
        if timestamp >= self.__timestamp:
            self.__timestamp = timestamp
        else:
            raise ValueError("setting timestamp is wrong !")

    def add_timestamp(self, duration):
        if duration >= 0:
            self.__timestamp += duration
            return self.__timestamp
        else:
            raise ValueError("duration cannot less than zero")

    def set_currentMaxWeight(self, weight):
        if weight < 0:
            raise ValueError("setting weight as negative!")
        self.__currentMaxWeight = weight
        return self.__currentMaxWeight

    def set_currentWeight(self, weight):
        weight += self.__current_load_weight
        if weight < 0 or weight > self.__currentMaxWeight:
            raise ValueError("weight setting is over limit")
        self.__current_load_weight = weight
        return self.__current_load_weight

    def add_weight(self, cargo_name, weight):
        if not cargo_name:
            return True
        cargo_weight = self.__cargos[cargo_name].get_current_weight + weight
        load_weight = self.__current_load_weight + weight
        if cargo_weight < 0 or load_weight > self.__ship_static.weightLimit:
            return False
        self.__cargos[cargo_name].add_weight(weight)
        self.__current_load_weight = load_weight
        return True

    def reset_weight(self):
        self.__current_load_weight = 0
        for cargo in self.__cargos:
            self.__cargos[cargo].set_currentWeight(0)
        self.__current_load_weight = self.__init_load_weight

    def set_status(self, status):
        self.__status = status

    @property
    def ship_id(self):
        return self.__ship_id

    def set_limit_load_weight(self, limit_load_weight):
        self.__ship_static._weight_limit = limit_load_weight

    @property
    def get_timestamp(self):
        return self.__timestamp

    @property
    def currentWeight(self):
        return self.__current_load_weight

    @property
    def current_maxWeight(self):
        return self.__currentMaxWeight

    @property
    def Cargos(self):
        return self.__cargos

    @property
    def initCargos(self):
        return self.__init_cargos

    @property
    def get_draft(self):
        self.__draft = self.__current_load_weight * 0.1    # TODO: Update Formula
        return self.__draft

    # SHIP_STATIC
    @property
    def shipName(self):
        return self.__ship_static.shipName

    @property
    def weightLimit(self):
        return self.__ship_static.weightLimit

    @property
    def get_ship_com(self):
        return self.__compartment.get_ship_com

    @property
    def comp_limit(self):  # Ex. comp_limit = { 0: 10000, 1: 10000 }
        return self.__ship_static.comp_limit

    @property
    def comp_dic(self):  # Ex. com_dic = { 0:'P1', 1:'P2' }
        return self.__ship_static.comp_dic

class ShipStatic:
    def __init__(self, ship_id, ship_dic):
        self.__ship_name = f'ship_{ship_id}'
        self._weight_limit = ship_dic["ship_weight_limit"]
        self.__com_limit = ship_dic["com_limit"]
        self.__com_load_factor = ship_dic['load_factor']
        self.__com_dic = ship_dic["com_dic"]

    @property
    def shipName(self):
        return self.__ship_name

    @property
    def weightLimit(self):
        return self._weight_limit

    @property
    def comp_limit(self):
        return {int(com): self.__com_limit[com] * self.__com_load_factor[com] / 100 for com in self.__com_limit}

    @property
    def comp_dic(self):
        return {int(com): self.__com_dic[com] for com in self.__com_dic}
