from qubots.base_problem import BaseProblem
import random
import os

def read_integers(filename):

# Resolve relative path with respect to this module’s directory.
    if not os.path.isabs(filename):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(base_dir, filename)


    with open(filename) as f:
        return [int(elem) for elem in f.read().split()]

class FlowshopProblem(BaseProblem):
    """
    Flowshop Scheduling Problem for Qubots.
    
    A set of jobs must be processed on every machine in the shop following the same sequence.
    On machine 0, the first job starts at time 0 and each subsequent job starts immediately after
    the previous job is finished. On every other machine, a job can only start once it has been
    processed on the previous machine and the machine itself is free (i.e. the previous job has finished).
    
    The objective is to minimize the makespan – the completion time of the last job on the last machine.
    
    **Decision Variable:**
      A permutation (list) of job indices (0-indexed) representing the processing order.
    
    **Instance Format:**
      - First line: number of jobs, number of machines, seed used to generate the instance,
        upper bound, and lower bound.
      - Then, for each machine, a line with the processing times of each job on that machine.
    """
    
    def __init__(self, instance_file: str):
        self.nb_jobs, self.nb_machines, self.processing_time_data = self._read_instance(instance_file)
    
    def _read_instance(self, instance_file: str):
        integers = read_integers(instance_file)
        it = iter(integers)
        nb_jobs = int(next(it))
        nb_machines = int(next(it))
        # Skip seed, upper bound, and lower bound.
        next(it); next(it); next(it)
        # For each machine, read processing times for each job.
        processing_time_data = []
        for m in range(nb_machines):
            machine_times = [int(next(it)) for _ in range(nb_jobs)]
            processing_time_data.append(machine_times)
        return nb_jobs, nb_machines, processing_time_data

    def evaluate_solution(self, solution) -> float:
        """
        Evaluates a candidate solution.
        
        Expects:
          solution: a list representing a permutation of job indices (0-indexed).
        
        Returns:
          The makespan (completion time of the last job on the last machine) if the solution is feasible.
          Otherwise, returns a high penalty (e.g. 1e9).
        """
        penalty = 1e9
        # Verify the solution is a permutation of all jobs.
        if not isinstance(solution, list) or len(solution) != self.nb_jobs:
            return penalty
        if sorted(solution) != list(range(self.nb_jobs)):
            return penalty
        
        # Compute completion times in a flowshop.
        # completion[m][j] is the completion time of the j-th job in the sequence on machine m.
        completion = [[0] * self.nb_jobs for _ in range(self.nb_machines)]
        sequence = solution
        
        # On machine 0.
        completion[0][0] = self.processing_time_data[0][sequence[0]]
        for j in range(1, self.nb_jobs):
            completion[0][j] = completion[0][j-1] + self.processing_time_data[0][sequence[j]]
        
        # For machines 1 to nb_machines-1.
        for m in range(1, self.nb_machines):
            # The first job on machine m can only start after finishing on machine m-1.
            completion[m][0] = completion[m-1][0] + self.processing_time_data[m][sequence[0]]
            for j in range(1, self.nb_jobs):
                # A job on machine m starts when both the previous job on machine m and the same job on machine m-1 are finished.
                start_time = max(completion[m][j-1], completion[m-1][j])
                completion[m][j] = start_time + self.processing_time_data[m][sequence[j]]
        
        makespan = completion[self.nb_machines - 1][self.nb_jobs - 1]
        return makespan

    def random_solution(self):
        """
        Generates a random candidate solution: a random permutation of job indices.
        """
        perm = list(range(self.nb_jobs))
        random.shuffle(perm)
        return perm
