# Sistemas-Distribuidos-P2

What is fitxer.py
This project corresponds to a practice developed by Marc Infante and Iñigo Arriazu that implements a list of mutual exclusion in which, from a certain number of threads, they will be granted access to a list in a unique way. To check that this happens correctly, a check will be carried out using lists.
The practice is made up of two main functions, one master and the other slave implemented in the code.


MAIN:
Function: Initialize the program and check that the parameters are correct, lastly check if the process was successful.
Global Parameters:
x → how often the function will be monitored.
ibm_cos → IBM server configuration.
Output parameters
it has no output parameters.
Preconditions:
N_SLAVES <100 → the number of slaves must never exceed 100.
“To be taken into account” → the parameter TIME = 0.3 can alter the performance of the program and tiny times can be useless if no changes have occurred on the server.
Updates to the list will be made when the name of the created objects changes from "p_write" + "id" to "write_" + "id"

Postconditions
results (obtained from “results.txt” must be equivalent to write_permission_list for the process to be considered correct

if __name__ == '__main__':
    param = []
    if (N_SLAVES <= 0 or N_SLAVES >= 100):
        N_SLAVES = 10

    print("el nnumero de esclavos es:", N_SLAVES)
    pw = pywren.ibm_cf_executor(config_cf)
    pw.call_async(master, TIME)
    for num in range(N_SLAVES):
        param.append([TIME])
    pw.map(slave, param)
    write_permission_list = pw.get_result()
------------------------------------------------------------------------------------------------------------------------------------------
MASTER:
Function: It is responsible for starting slaves, carrying the order of items in the list write_permission_list and returns it at the end of the function.
Input parameters
x → how often the function will be monitored.
ibm_cos → IBM server configuration.
Output parameters
write_permission_list → all identifier elements calculated and ordered according to when their respective "slave" functions were accessed.
Preconditions:
N_SLAVES <100 → the number of slaves must never exceed 100.
“To be taken into account” → the parameter TIME = 0.3 can alter the performance of the program and tiny times can be useless if no changes have occurred on the server.


  ----------------------------------------------------------------------------------------------------------------------------------

SLAVE:
Function: create an object on the IBM server with the name "p_write" and concatenating its identifier all the calculated results and fill an array that returns as output parameter
Input parameters
id → identifier of each of the slaves.
x → how often the function will be monitored.
ibm_cos → IBM server configuration.
Output parameters
it has no output parameters.
Preconditions:
N_SLAVES <100 → the number of slaves must never exceed 100.
“To be taken into account” → the parameter TIME = 0.3 can alter the performance of the program and tiny times can be useless if no changes have occurred on the server.
Updates to the list will be made when the name of the created objects changes from "p_write" + "id" to "write_" + "id"


--------------------------------------------------------------------------------------------------------------------------------------

Additional resources
[1] - Josep Sampé, Gil Vernik, Marc Sánchez-Artigas, Pedro García-López, “Serverless Data Analytics in the IBM Cloud”. Middleware Industry 2018: 1-8 
[2] IBM-PyWren - PyWren on IBM Cloud, URL: https://github.com/pywren/pywren-ibm-cloud
[3] - Asignatura Sistemas Distribuidos y apuntes asociados
[4] IBM-botocore: https://github.com/pywren/pywren-ibm-cloud/blob/master/docs/functions.md#reserved-parameters 
