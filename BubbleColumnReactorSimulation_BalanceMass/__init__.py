import json
import logging
import numpy as np 
import azure.functions as func
import numpy as np
from scipy.integrate import solve_ivp


def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    try:
        req_body = req.get_json()
    except ValueError:
        pass
    else:
        # Variable declarations
        
        e_mf = req_body.get('e_mf')  # adimensional
        K_a = req_body.get('K_a')  # (m3_gas / (m3_solid · s)) = (1/s)
        D = req_body.get('D')  # (m_2/s)
        d_b = req_body.get('d_b')  # m
        u_0 =  req_body.get('u_0')  # m/s
        u_mf = req_body.get('u_mf')  # m/s
        alpha = req_body.get('alpha')  # adimensional
        H_bfb = req_body.get('H_bfb')  # m
        g =  req_body.get('g')  # m/s
        Ca_0 = req_body.get('Ca_0') # mol/m3

        logging.info('Initial variables')
        logging.info('-------------------------------------------------------------------------------')
        logging.info(' ')
        logging.info('Fraction of voids for minimal fluidization bed --> e_mf  = ' + str(e_mf))
        logging.info('Kinetics costant of A --> K_a  = ' + str(K_a) + ' (m3_gas / (m3_solid · s)) = (1/s)')
        logging.info('Diffusion constant --> D  = ' + str(D) + ' (m_2/s)')
        logging.info('Bubble diameter --> d_b  = ' + str(d_b) + ' m')
        logging.info('Superficial gas velocity in the bed --> u_0  = ' + str(u_0) + ' (m/s)')
        logging.info('Minimal fluidization gas velocity --> u_mf  = ' + str(u_mf) + ' (m/s)')
        logging.info('alpha (volume wake / volume of bubble) = ' + str(alpha))
        logging.info('H_bfb (Height of column)  = ' + str(H_bfb) + ' m')
    
        logging.info(' ')

        logging.info('Calculations')
        logging.info('-------------------------------------------------------------------------------')
        logging.info(' ')

        u_br = 0.711 * (g * d_b) ** (1 / 2)

        logging.info('Rise velocity of a single bubble --> u_br = ' + str(u_br) + ' m/s')

        u_b = u_0 - u_mf + u_br

        logging.info('Rise bubbles speed in bubbling bed --> u_b = ' + str(u_b) + '  m/s')

        delta = (u_0 - u_mf) / u_b

        logging.info('Bed fractions --> delta = ' + str(delta))

        K_bc = (4.50 * (u_mf / d_b)) + 5.85 * ((D ** (1 / 2) * g ** (1 / 4)) / (d_b ** (5 / 4)))

        logging.info('Davidson coefficient K_bc = ' + str(K_bc) + '  1/s')

        K_ce = 6.77 * ((e_mf * D * u_br) / d_b ** (3)) ** (1 / 2)

        logging.info('Davidson coefficient K_ce = ' + str(K_ce) + '  1/s')

        f_b = 0.01

        logging.info('f_b = ' + str(f_b))

        f_c = delta * (1 - e_mf) * (((3 * u_mf / e_mf) / (u_br - (u_mf / e_mf))) + alpha)

        logging.info('f_c = ' + str(f_c))

        f_e = ((1 - e_mf) * (1 - delta)) - f_c - f_b

        logging.info('f_e = ' + str(f_e))

        f_total = f_b + f_c + f_e

        logging.info('f_total = ' + str(f_total))

        fbTimesKa = f_b * K_a

        # logging.info(fbTimesKa)

        oneDividedDeltaTimesKbc = 1 / (delta * K_bc)

        # logging.info(oneDividedDeltaTimesKbc)

        oneDividedFcTimesK = f_c * K_a

        # logging.info(oneDividedFcTimesK)

        lastEquationOperand = 1 / ((1 / (delta * K_ce)) + (1 / (f_e * K_a)))

        # logging.info(lastEquationOperand)

        K_effective = (fbTimesKa + ( 1 / (oneDividedDeltaTimesKbc + 1 / (oneDividedFcTimesK + lastEquationOperand)))) / f_total

        logging.info("K_effective : " + str(K_effective))

        t_init = 0
        t_final = 6900

        t_eval = range(0,6900,300)

        Ca0 =[Ca_0]
        def reactionSystem(t,Ca):

            dyCa = - K_effective * Ca

            return np.array([dyCa])

        sol = solve_ivp(reactionSystem, (t_init, t_final), Ca0, t_eval = t_eval)

        # Consolidating outputs:
        dyCa = sol.y[0]
        t = sol.t

        logging.info("dyCa : ")
        logging.info(dyCa)
        logging.info("t : ")
        logging.info(sol.t)

        sol_json = []

        for item in range(0, len(dyCa), 1):
            sol_details = {
                "e_mf": str(e_mf),  # adimensional
                "K_a": str(K_a),  # (m3_gas / (m3_solid · s)) = (1/s)
                "D": str(D),  # (m_2/s)
                "d_b": str(d_b),  # m
                "u_0": str(u_0),  # m/s
                "u_mf": str(u_mf),  # m/s
                "alpha": str(alpha),  # adimensional
                "H_bfb": str(H_bfb),  # m
                "g": str(g),  # m/s
                "Ca" : str(dyCa[item]),
                "t" : str(t[item])
            }

            sol_json.append(sol_details)

        logging.info(sol_json)

        return json.dumps(sol_json)

    return func.HttpResponse("Reactor simulated succesfully...",status_code=200)
