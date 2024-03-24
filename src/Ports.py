

def get_dist(port1, port2, table):
    return table[port1][port2]

class Position:
    def __init__(self):
        self.Lon = None
        self.Lat = None

class Port:
    def __init__(self, port_name, port_dic=None):
        self.port_name = port_name
        self.position = Position()
        self.country = None
        self.port_dic = dict()  # key: port_no, value: ( draft_limit, fee ... )

        if port_dic:
            self.init_port_ls(port_dic)

    def init_port_ls(self, port_ls):
        for no in port_ls:
            self.port_dic[no] = port_ls[no]


if __name__ == "__main__":

    KAOHSIUNG = Port("KAOHSIUNG")
    print(KAOHSIUNG.port_name)
    print(KAOHSIUNG.position.Lon)
