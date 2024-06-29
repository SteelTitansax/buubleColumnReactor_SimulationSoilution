from gettext import npgettext
import logging
import azure.functions as func

import json
import math
# Bubble Column reactor mass balance developed by Manuel Portero Leiva


def main(req: func.HttpRequest) -> func.HttpResponse:

    logging.info('BubbleColumnReactor triggered. Simulation beggins....')

    try:
        req_body = req.get_json()
    except ValueError:
        pass
    else:

        # Variable declarations

        K_a = req_body.get('K_a') # (m3_gas / (m3_solid · s)) = (1/s)
        T = req_body.get('T') # K
        Delta_H = req_body.get('Delta_H') # KJ / mol · K 


        logging.info('Initial variables')
        logging.info('-------------------------------------------------------------------------------')
        logging.info(' ')
        logging.info('Kinetics costant of A --> K_a  = ' + str(K_a) + ' (m3_gas / (m3_solid · s)) = (1/s)')
        logging.info('Kinetics Operation Temperature' + str(T) + ' K')
        logging.info('Entalpy formation of A' + str(Delta_H) + ' KJ / mol · K')


        logging.info(' ')

        logging.info('Calculations')
        logging.info('-------------------------------------------------------------------------------')
        logging.info(' ')

        
        R = 0.00831  # KJ / mol · K

        exponentialFactor = - Delta_H / (R * T)  # admimensional

        exponentialValue = math.exp(round(exponentialFactor))

        logging.info(round(exponentialValue))

        A = K_a / exponentialValue  # (1/s)

        logging.info('Pre exponential factor ' + str(A) + ' 1/s')

        logging.info(round(exponentialFactor))

        exponentialValue = math.exp(round(exponentialFactor))

        logging.info(round(exponentialValue))

        A = K_a / exponentialValue  # (1/s)

        logging.info('Pre exponential factor ' + str(A) + ' 1/s')

        Temperature_final = int(T) + 10  # K
        Temperature_Initial = int(T) - 10 # K
        
        sol_json = []

        arrK = []
        arrT = []

        for Temperature in range(Temperature_Initial,Temperature_final,1):

                K = A * math.exp((-1 * Delta_H) / (R * Temperature))  # 1/s

                arrK.append(K)
                arrT.append(Temperature)


        for item in range(0,len(arrK),1):
            sol_details = {
                "K": arrK[item],
                "T": arrT[item]
            }

            sol_json.append(sol_details)


        logging.info(sol_json)
        return json.dumps(sol_json)
    return func.HttpResponse("Reactor simulated succesfully...",status_code=200)