# qkd_backend/qkd_runner/exp1.py

def run_exp1():
    # Qiskit patterns step 1: Map your problem to quantum circuit
    # Import some generic packages
    import numpy as np
    from qiskit import QuantumCircuit
    import matplotlib.pyplot as plt 

    # Set up a random number generator and a quantum circuit. 
    rng = np.random.default_rng()
    bit_num = 20
    qc = QuantumCircuit(bit_num, bit_num)

    # QKD step 1: Random bits and bases for Alice
    abits = np.round(rng.random(bit_num))
    abase = np.round(rng.random(bit_num))

    for n in range(bit_num):
        if abits[n] == 0:
            if abase[n] == 1:
                qc.h(n)
        if abits[n] == 1:
            if abase[n] == 0:
                qc.x(n)
            if abase[n] == 1:
                qc.x(n)
                qc.h(n)

    qc.barrier()

    # QKD step 2: Random bases for Bob
    bbase = np.round(rng.random(bit_num))

    for m in range(bit_num):
        if bbase[m] == 1:
            qc.h(m)
        qc.measure(m, m)

    print("Alice's bits are ", abits)
    print("Alice's bases are ", abase)
    print("Bob's bases are ", bbase)

    qc.draw("mpl")
    plt.show()

    from qiskit_ibm_runtime import QiskitRuntimeService
    service = QiskitRuntimeService(channel="ibm_cloud", token="qGGqN8upOcKVf6Xc0mXTqVkobbKbLp-jCrucM39cc7dP")
    backend = service.backend("ibm_brisbane")
    print(backend.name)

    from qiskit.primitives import BackendSamplerV2
    from qiskit_aer import AerSimulator
    from qiskit_aer.noise import NoiseModel
    from qiskit_ibm_runtime import SamplerV2 as Sampler
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

    noise_model = NoiseModel.from_backend(backend)
    backend_sim = AerSimulator(noise_model=noise_model)
    sampler_sim = BackendSamplerV2(backend=backend_sim)

    target = backend.target
    pm = generate_preset_pass_manager(target=target, optimization_level=3)
    qc_isa = pm.run(qc)

    sampler = Sampler(mode=backend)
    job = sampler.run([qc_isa], shots=1)

    counts = job.result()[0].data.c.get_counts()
    countsint = job.result()[0].data.c.get_int_counts()

    keys = counts.keys()
    key = list(keys)[0]
    bmeas = list(key)
    bmeas_ints = []
    for n in range(bit_num):
        bmeas_ints.append(int(bmeas[n]))
    bbits = bmeas_ints[::-1]

    print(bbits)

    # QKD step 3: Public discussion of bases
    agoodbits = []
    bgoodbits = []
    match_count = 0
    for n in range(bit_num):
        if abase[n] == bbase[n]:
            agoodbits.append(int(abits[n]))
            bgoodbits.append(bbits[n])
            if int(abits[n]) == bbits[n]:
                match_count += 1

    print(agoodbits)
    print(bgoodbits)
    print("fidelity = ", match_count / len(agoodbits))
    print("loss = ", 1 - match_count / len(agoodbits))

    # Return results as string for UI
    return {
        "alice_bits": abits.tolist(),
        "alice_bases": abase.tolist(),
        "bob_bases": bbase.tolist(),
        "bob_bits": bbits,
        "agoodbits": agoodbits,
        "bgoodbits": bgoodbits,
        "fidelity": match_count / len(agoodbits),
        "loss": 1 - match_count / len(agoodbits)
    }
