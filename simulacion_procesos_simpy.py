import simpy
import random
import statistics
import matplotlib.pyplot as plt

# ==================================================
# PARÁMETROS MODIFICABLES
# ==================================================

RANDOM_SEED = 42

INTERVAL = 10          # 10, 5, 1
RAM_CAPACITY = 100       # 100 o 200
CPU_CAPACITY = 1         # 1 o 2
INSTR_POR_UNIDAD = 3     # 3 (normal) o 6 (rápido)

PROCESOS_LISTA = [25, 50, 100, 150, 200]

# ==================================================
# PROCESO
# ==================================================

def proceso(env, ram, cpu, tiempos):

    tiempo_llegada = env.now

    memoria = random.randint(1, 10)
    instrucciones = random.randint(1, 10)

    # NEW → solicitar RAM
    yield ram.get(memoria)

    while instrucciones > 0:

        # READY → solicitar CPU
        with cpu.request() as req:
            yield req

            ejecutadas = min(INSTR_POR_UNIDAD, instrucciones)
            yield env.timeout(1)

            instrucciones -= ejecutadas

        # Posible I/O
        if instrucciones > 0:
            if random.randint(1, 21) == 1:
                yield env.timeout(1)

    # TERMINATED → devolver RAM
    yield ram.put(memoria)

    tiempo_total = env.now - tiempo_llegada
    tiempos.append(tiempo_total)

# ==================================================
# GENERADOR
# ==================================================

def generador(env, num_procesos, ram, cpu, tiempos):

    for _ in range(num_procesos):

        env.process(proceso(env, ram, cpu, tiempos))

        llegada = random.expovariate(1.0 / INTERVAL)
        yield env.timeout(llegada)

# ==================================================
# SIMULACIÓN
# ==================================================

def correr_simulacion(num_procesos):

    random.seed(RANDOM_SEED)

    env = simpy.Environment()

    ram = simpy.Container(env,
                          init=RAM_CAPACITY,
                          capacity=RAM_CAPACITY)

    cpu = simpy.Resource(env,
                         capacity=CPU_CAPACITY)

    tiempos = []

    env.process(generador(env, num_procesos, ram, cpu, tiempos))
    env.run()

    promedio = statistics.mean(tiempos)
    desviacion = statistics.stdev(tiempos) if len(tiempos) > 1 else 0

    return promedio, desviacion

# ==================================================
# EJECUCIÓN AUTOMÁTICA
# ==================================================

if __name__ == "__main__":

    promedios = []

    print("\n===== RESULTADOS =====\n")

    for n in PROCESOS_LISTA:

        prom, std = correr_simulacion(n)
        promedios.append(prom)

        print(f"Procesos: {n}")
        print(f"Promedio: {prom:.2f}")
        print(f"Desviación estándar: {std:.2f}")
        print("----------------------------")

    # ===== Gráfica =====
    plt.figure()
    plt.plot(PROCESOS_LISTA, promedios)
    plt.xlabel("Número de procesos")
    plt.ylabel("Tiempo promedio")
    plt.title(f"Procesos vs Tiempo Promedio (Intervalo={INTERVAL})")
    plt.show()

