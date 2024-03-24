import copy

import route_processor as rp
import Routes_Generator as Rg
from opt.opt_interface import OptMethod, opt_fac
import Ports
from util import utils

from collections import deque


def checkStampValid(timestamp, ent_ts, max_route_ts=0):
    if ent_ts and timestamp > ent_ts:
        return False
    elif max_route_ts and timestamp > max_route_ts:
        return False
    return True

def gen_route(order_obj,
              table_obj,
              SHIP,
              is_arrange=False,
              opt_method=OptMethod.MAX_PROFIT):
    """
    Generate Optimize Routing Schedules.
    :return: best routing list by opt_method
    """
    route_len = len(order_obj.new_df)
    maxIncome = order_obj.max_income
    print(f"maxIncome={maxIncome}")

    best_target_ls = []
    opt = opt_fac(opt_method)(route_len, best_target_ls, order_obj.N)

    SHIP.set_cargo_ls_from_order(order_obj.new_df.cargo.unique(),
                                 table_obj.cargo_dic)
    SHIP.init_current_com(table_obj.arrange_com_obj.current_com, table_obj.cargo_dic)
    print("\n  ----- CARGOS : ")
    for cargo in SHIP.Cargos:
        print(f"{SHIP.Cargos[cargo].get_cargoName} ({SHIP.Cargos[cargo].get_cargoGroup}): \
                {SHIP.Cargos[cargo].get_current_weight}")

    SHIP.count = 0
    if order_obj.isPanama:
        cal_counts = utils.CountRoutes(panama_struc=order_obj.input_struct).count_panama()
    else:
        cal_counts = utils.CountRoutes(orig=order_obj.origin_ls,
                                       single=order_obj.single_ls,
                                       prior=order_obj.prior_set).count()

    Routes_Generator = Rg.RoutesGen(order_obj.laycan_dic, order_obj.input_struct, opt.abandable()).gen_routes()

    print(f"```\nEstimated Count = {int(cal_counts)}, "
          f"About {cal_counts * 0.00015031265031265032: .0f} sec "
          f"({cal_counts * 0.00015031265031265032 / 60: .2f} min )\n```")
    for route in Routes_Generator:
        SHIP.count += 1
        if is_arrange:
            table_obj.arrange_com_obj.reset()

        access_route(SHIP, route, order_obj, table_obj, is_arrange, opt)

    best_target_ls.sort(key=lambda x: x[opt.target_index], reverse=opt.target_max_best)
    print("REAL COUNT = ", SHIP.count)

    if len(best_target_ls):
        best_target = best_target_ls[0][opt.target_index]
        for i in range(len(best_target_ls)):
            target = best_target_ls[i][opt.target_index]
            if opt.button_condition(target, best_target):
                best_target_ls = best_target_ls[:i]
                break

    return best_target_ls

def access_route(SHIP, route, order_obj, table_obj, is_arrange, opt):

    route_check = rp.route2check(route, order_obj.item_dic_for_routecheck, order_obj.group_dic_for_routecheck)
    route_len = len(route)

    # Initialize
    idle_dq = deque()
    tmp_cost = 0

    opt.reset()

    cargo_name = order_obj.order_dic['cargo'][route[0]]
    SHIP.init_timestamp(order_obj.initTS)
    SHIP.reset_weight()

    # First Port
    pre_port = order_obj.initPort
    port = order_obj.order_dic['port'][route[0]]
    period = table_obj.days_dic[pre_port][port]
    SHIP.add_timestamp(period * 86400)
    opt.get_datets_dq[0] = SHIP.get_timestamp  # TODO: set date_ts

    if not checkStampValid(SHIP.get_timestamp, order_obj.order_dic['end_ts'][route[0]], order_obj.max_route_ts):
        return False
    elif SHIP.get_timestamp < order_obj.order_dic['start_ts'][route[0]]:
        idleTime = order_obj.order_dic['start_ts'][route[0]] - SHIP.get_timestamp
        idle_dq.append(idleTime)
        SHIP.add_timestamp(idleTime)
        tmp_cost += (table_obj.fee_dic.OIL_RUN * period + table_obj.fee_dic.OIL_IDLE * idleTime / 86400)
    else:
        idle_dq.append(0)
        tmp_cost += (table_obj.fee_dic.OIL_RUN * period)

    if route_check[0] > 0:
        opt.get_income_dic[order_obj.item_dic_for_routecheck[route[0]]] = \
            order_obj.income_dic_for_routecheck[order_obj.item_dic_for_routecheck[route[0]]]['income']

    tmp_cost += table_obj.fee_dic.PORT_FEE[port]
    tmp_cost += (order_obj.stay_dic[route[0]] * table_obj.fee_dic.OIL_IDLE)

    # -- Set Cargo
    SHIP.add_weight(cargo_name, order_obj.order_dic['weights'][route[0]])
    if table_obj.draft_limit_dic[port] and SHIP.get_draft > table_obj.draft_limit_dic[port]:
        return False

    if (SHIP.currentWeight <= SHIP.weightLimit and
            (SHIP.Cargos[cargo_name].get_current_weight >= 0 or
             (SHIP.Cargos[cargo_name].get_current_weight + SHIP.initCargos[cargo_name] >= 0))):
        sumDist = Ports.get_dist(pre_port, port, table_obj.mile_dic)

        SHIP.add_timestamp(order_obj.stay_dic[route[0]] * 86400)  # Stay day
        tmp_cost += ((period + idle_dq[-1] / 86400 + order_obj.stay_dic[route[0]]) * table_obj.fee_dic.DAILY_FEE)  # Daily Fee
        opt.get_cost_dq[0] = tmp_cost

        pre_port = port
        pre_port_no = order_obj.order_dic['port_no'][route[0]]
        valid_weight, valid_timestamp = True, True
        for i in range(1, route_len):

            order_no = route[i]
            cargo_name = order_obj.order_dic['cargo'][order_no]
            valid_weight = SHIP.add_weight(cargo_name, order_obj.order_dic['weights'][order_no])
            port = order_obj.order_dic['port'][order_no]
            port_no = order_obj.order_dic['port_no'][order_no]

            if table_obj.draft_limit_dic[port] and SHIP.get_draft > table_obj.draft_limit_dic[port]:
                valid_weight = False

            stay_day = order_obj.stay_dic[order_no]

            tmp_cost = 0
            period = table_obj.days_dic[port][pre_port]
            valid_timestamp = checkStampValid(SHIP.get_timestamp + period * 86400,
                                              order_obj.order_dic['end_ts'][order_no],
                                              order_obj.max_route_ts)
            SHIP.add_timestamp(period * 86400)

            if SHIP.currentWeight > SHIP.current_maxWeight:
                SHIP.set_currentMaxWeight(SHIP.currentWeight)

            if not valid_weight or not valid_timestamp:
                return False
            elif SHIP.get_timestamp < order_obj.order_dic['start_ts'][order_no]:
                idleTime = order_obj.order_dic['start_ts'][order_no] - SHIP.get_timestamp
                idle_dq.append(idleTime)
                tmp_cost += (idleTime / 86400 * table_obj.fee_dic.OIL_IDLE)
                opt.get_datets_dq[i] = SHIP.get_timestamp
                SHIP.add_timestamp(idleTime)
            else:
                idle_dq.append(0)
                opt.get_datets_dq[i] = SHIP.get_timestamp

            sumDist += Ports.get_dist(pre_port, port,
                                      table_obj.mile_dic)

            tmp_cost += (period * table_obj.fee_dic.OIL_RUN)

            if pre_port != port:
                tmp_cost += table_obj.fee_dic.PORT_FEE[port]
            elif pre_port_no != port_no:
                tmp_cost += table_obj.fee_dic.PORT_FEE[port] * 0.333333

            if route_check[i] > 0:
                opt.get_income_dic[order_obj.item_dic_for_routecheck[order_no]] = \
                    order_obj.income_dic_for_routecheck[order_obj.item_dic_for_routecheck[order_no]]['income']

            SHIP.add_timestamp(stay_day * 86400)  # Stay day
            tmp_cost += (stay_day * table_obj.fee_dic.OIL_IDLE)
            tmp_cost += ((period + idle_dq[-1] / 86400 + stay_day) * table_obj.fee_dic.DAILY_FEE)

            opt.get_cost_dq[i] = tmp_cost
            pre_port = port
            pre_port_no = port_no

        if valid_weight and valid_timestamp:

            sumDist_pick = sumDist
            sumCost = sum(opt.get_cost_dq)
            ds = SHIP.get_timestamp - order_obj.initTS
            income = opt.sum_income()

            real_profit = income - sumCost
            opt.set_real_profit(real_profit, route_len)
            mode = opt.is_in(real_profit)
            if mode:
                cargo_items = [order_obj.cargo_items[no] for no in route]
                if is_arrange and not table_obj.arrange_com_obj.arrange_tot(cargo_items):
                    return False

                opt.add_to_target_ls([
                    route, opt.get_datets_dq, idle_dq, sumDist_pick, ds,
                    sumCost, real_profit, route_len, opt.get_cost_dq
                    , table_obj.arrange_com_obj.get_plan()
                ], mode)
    return True

