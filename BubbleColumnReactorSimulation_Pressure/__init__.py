from gettext import npgettext
import logging
import azure.functions as func
import numpy as np 
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

        rho = req_body.get('rho') # Kg/m3 normal value 2110
        H = req_body.get('H') # m
        C_b = req_body.get('C_b') # mol / m3
        T = req_body.get('T') # K
        V = req_body.get('V') # m3
        
        logging.info('Initial variables')
        logging.info('-------------------------------------------------------------------------------')
        logging.info(' ')
        logging.info('Density ' + str(rho) + ' # Kg/m3')
        logging.info('Height ' + str(H) + ' m')
        logging.info('Concentration C_b (N) ' + str(C_b) + ' # mol / m3')
        logging.info('Operation Temperature ' + str(T) + ' # K')
        logging.info('Volume ' + str(V) + ' # m3')


        logging.info(' ')

        logging.info('Calculations')
        logging.info('-------------------------------------------------------------------------------')
        logging.info(' ')

        g = 9.8 # m/s2
        R = 0.00831  # KJ / mol · K

        Operation_P_Hidrostatic =  ( rho * g * H ) + 101325  # Pascals

        logging.info(round(Operation_P_Hidrostatic))

        Operation_P_Gas = ( C_b * R * T ) / V # Pascals

        logging.info(round(Operation_P_Gas))

        Operation_P_Total = Operation_P_Hidrostatic + Operation_P_Gas # Pascal
        
        logging.info(round(Operation_P_Total))

        Temperature_final = int(T) + 10  # K
        Temperature_Initial = int(T) - 10 # K


        sol_json = []

        arrP = []
        arrT = []
        
        for Temperature in range(Temperature_Initial,Temperature_final,1):

                P_Hidrostatic =  ( rho * g * H ) + 101325  # Pascals

                P_Gas = ( C_b * R * Temperature ) / V # Pascals

                P_Total = P_Hidrostatic + P_Gas # Pascal


                arrP.append(P_Total)
                arrT.append(Temperature)
                
                

        for item in range(0,len(arrP),1):
            sol_details = {
                "Op_Pt": Operation_P_Total,
                "Op_Pg": Operation_P_Gas,
                "Op_Ph": Operation_P_Hidrostatic,
                "P": arrP[item],
                "T": arrT[item]
            }

            sol_json.append(sol_details)


        logging.info(sol_json)

        return json.dumps(sol_json)

    return func.HttpResponse("Reactor simulated succesfully...",status_code=200)