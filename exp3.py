def run_exp3():
    import numpy as np
    from qiskit_ibm_runtime import SamplerV2 as Sampler
    from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister

    # This calculation was run on ibm_nazca on 11-7-24 and required 2 s to run, with 127 qubits.
    # Qiskit patterns step 1: Mapping your problem to a quantum circuit

    bit_num = 127
    qr = QuantumRegister(bit_num, "q")
    cr = ClassicalRegister(bit_num, "c")
    qc = QuantumCircuit(qr, cr)

    # QKD step 1: Generate Alice's random bits and bases
    rng = np.random.default_rng()
    abits = np.round(rng.random(bit_num))
    abase = np.round(rng.random(bit_num))

    # Alice's state preparation
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

    # Eavesdropping happens here!
    ebase = np.round(rng.random(bit_num))
    for m in range(bit_num):
        if ebase[m] == 1:
            qc.h(m)
        qc.measure(qr[m], cr[m])

    from qiskit_ibm_runtime import QiskitRuntimeService
    service = QiskitRuntimeService(channel="ibm_cloud", token="qGGqN8upOcKVf6Xc0mXTqVkobbKbLp-jCrucM39cc7dP")
    backend = service.backend("ibm_brisbane")
    print(backend.name)

    from qiskit.primitives import BackendSamplerV2
    from qiskit_aer import AerSimulator
    from qiskit_aer.noise import NoiseModel
    from qiskit_ibm_runtime import SamplerV2 as Sampler

    noise_model = NoiseModel.from_backend(backend)
    backend_sim = AerSimulator(noise_model=noise_model)
    sampler_sim = BackendSamplerV2(backend=backend_sim)

    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    target = backend.target
    pm = generate_preset_pass_manager(target=target, optimization_level=3)
    qc_isa = pm.run(qc)

    sampler = Sampler(mode=backend)

    # Step 3: Execute Eve's interception
    job = sampler.run([qc_isa], shots=1)
    counts = job.result()[0].data.c.get_counts()
    countsint = job.result()[0].data.c.get_int_counts()

    # Extract Eve's bits
    keys = counts.keys()
    key = list(keys)[0]
    emeas = list(key)
    emeas_ints = []
    for n in range(bit_num):
        emeas_ints.append(int(emeas[n]))
    ebits = emeas_ints[::-1]

    # Restart process: Eve resends to Bob
    qr = QuantumRegister(bit_num, "q")
    cr = ClassicalRegister(bit_num, "c")
    qc = QuantumCircuit(qr, cr)

    for n in range(bit_num):
        if ebits[n] == 0:
            if ebase[n] == 1:
                qc.h(n)
        if ebits[n] == 1:
            if ebase[n] == 0:
                qc.x(n)
            if ebase[n] == 1:
                qc.x(n)
                qc.h(n)

    # Bob's random bases
    bbase = np.round(rng.random(bit_num))
    for m in range(bit_num):
        if bbase[m] == 1:
            qc.h(m)
        qc.measure(qr[m], cr[m])

    # Transpile again
    target = backend.target
    pm = generate_preset_pass_manager(target=target, optimization_level=3)
    qc_isa = pm.run(qc)

    # Execute for Bob
    job = sampler.run([qc_isa], shots=1)
    counts = job.result()[0].data.c.get_counts()
    countsint = job.result()[0].data.c.get_int_counts()

    # Extract Bob's bits
    keys = counts.keys()
    key = list(keys)[0]
    bmeas = list(key)
    bmeas_ints = []
    for n in range(bit_num):
        bmeas_ints.append(int(bmeas[n]))
    bbits = bmeas_ints[::-1]

    # Compare Alice and Bob
    agoodbits = []
    bgoodbits = []
    match_count = 0
    for n in range(bit_num):
        if abase[n] == bbase[n]:
            agoodbits.append(int(abits[n]))
            bgoodbits.append(bbits[n])
            if int(abits[n]) == bbits[n]:
                match_count += 1

    print("Alice's bits = ", agoodbits)
    print("Bob's bits = ", bgoodbits)
    print("fidelity = ", match_count / len(agoodbits))
    print("loss = ", 1 - match_count / len(agoodbits))

    return {
        "alice_bits": agoodbits,
        "bob_bits": bgoodbits,
        "fidelity": match_count / len(agoodbits),
        "loss": 1 - match_count / len(agoodbits)
    }
