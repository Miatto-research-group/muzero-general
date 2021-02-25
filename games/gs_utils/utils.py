import numpy as np
import itertools
from games.gs_utils.operators import *


def make_init_unitary(size:int=3) -> np.array:
    init_unitary = None
    if size == 1:
        init_unitary = I
    elif size == 2:
        init_unitary = II
    elif size == 3:
        init_unitary = III
    return init_unitary


def get_random_gate(gates):
    l = len(gates)
    idx = np.random.randint(0,l)
    return gates[idx]


def get_random_qbits(nb:int=1, size:int=3):
    poss_qb = list(range(size))
    res_qb = []

    for _ in range(nb):
        l = len(poss_qb)
        rd_pick = np.random.randint(l)
        qb = poss_qb.pop(rd_pick)
        res_qb.append(qb)

    return tuple(res_qb)

def apply_1q_gate(gate:np.array, qbit:int, curr_unitary):
    idx = qbit * 2
    tensored_res = np.tensordot(curr_unitary, gate, axes=(idx, 1))
    N = curr_unitary.ndim
    lst = list(range(N))
    lst.insert(idx, N - 1)
    res = np.transpose(tensored_res, lst[:-1])
    return res


def apply_2q_gate(gate: np.array, qbitA: int, qbitB: int, curr_unitary):
    A = 2 * qbitA
    B = 2 * qbitB
    tensored_res = np.tensordot(curr_unitary, gate, axes=((A, B), (1, 3)))
    N = curr_unitary.ndim
    lst = list(range(N))
    if A < B:
        smaller, bigger = A, B
        first, second = N - 2, N - 1
    else:
        smaller, bigger = B, A
        first, second = N - 1, N - 2
    lst.insert(smaller, first)
    lst.insert(bigger, second)
    res = np.transpose(tensored_res, lst[:-2])
    return res

def apply_gate_on_qbits(action, curr_unitary):
    gate, qbits = action
    resulting_unitary = None

    if len(qbits) == 1:
        qb = qbits[0]
        resulting_unitary = apply_1q_gate(gate, qb, curr_unitary)
    elif len(qbits) == 2:
        qb_a, qb_b = qbits
        resulting_unitary = apply_2q_gate(gate, qb_a, qb_b, curr_unitary)
    else:
        raise ValueError("apply_gate_on_qbits: wrong number of qubits")

    return resulting_unitary


def make_random_unitary(qbg1=[], qbg2=[], nb_steps:int=3, size:int=3):
    """
    Generates a random unitary for learning, based on the specifications
    passed as arguments.

    Parameters
    ----------
    qbg1 : list of gates
        The list of one qubit gates to be used for gate generation.
    qbg2 : list of gates
        The list of two qubit gates to be used for gate generation.
    nb_steps : int
        The number of unitaries to be applied.
    size : int
        The number of qubits of the circuit the unitary should be made for.

    Returns
    ----------
    A tuple containing in its first element the generated random unitary,
    on the second element the list of actions (tuples of gate, qubit(s))
    used to obtain it.
    Theunitary is a "full" one, of the size of the system.
    """

    #generate an identity unitary of the size of the system
    target_unitary = make_init_unitary(size)
    action_path = []

    gate = None
    qbits = None
    for _ in range(nb_steps):
        dice_roll = np.random.randint(1,3)
        if dice_roll == 1:
            gate = get_random_gate(qbg1)
            qbits = get_random_qbits(1)
        elif dice_roll == 2:
            gate = get_random_gate(qbg2)
            qbits = get_random_qbits(2)
        else:
            raise ValueError ("make_random_unitary : Selected a gate too big for the system")
        action = (gate, qbits)
        target_unitary = apply_gate_on_qbits(action, target_unitary)
        action_path.append(action)

    return target_unitary, action_path




def make_permutations(permutation_size, sys_size:int=2):
    """Given a number of qbits of the system and the size of the permutation,
    returns all possible coherent permutations, i.e. uses each index only once"""
    assert sys_size >= permutation_size, 'Impossible to make permutations of size n with system size <n'
    r = []
    if permutation_size == 1:
        r = list(itertools.product(range(sys_size)))
    elif permutation_size == 2:
        all_2q_permutations = list(itertools.product(range(sys_size), range(sys_size)))
        r = list(filter(lambda x: x[0] != x[1], all_2q_permutations))
    else:
        raise ValueError("make_permutations : illegal permutation size, only 1 and 2 available")
    return r


def make_actions_from_permutations(qbp1, qbp2, qb1g, qb2g, sys_size=2):
    all_actions = []
    q1_actions = list(
        itertools.product(qb1g, qbp1))  # all possible qbs with all possible gates
    q2_actions = list(
        itertools.product(qb2g, qbp2))  # all possible pairs with all possible gates
    if sys_size == 1:
        all_actions = q1_actions
    elif sys_size >= 1:
        all_actions = q1_actions + q2_actions
    return  all_actions


def make_full_actions_list(qb1_gates, qb2_gates, sys_size=2):
    assert 0 < sys_size, "System size can not be null"
    perm1 = make_permutations(1, sys_size) #all qb possibles, ici only one
    if sys_size>1:
        perm2 = make_permutations(2, sys_size) # all possible pairs, here 0-1, 1-0 (order matters!)
    else:
        perm2 = []
    all_actions = make_actions_from_permutations(perm1, perm2, qb1_gates, qb2_gates, sys_size)
    r = list(zip([_ for _ in range(len(all_actions))], all_actions))  # [(idx, (gate, qb))]
    return r

