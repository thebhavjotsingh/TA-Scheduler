"""
Constraint Programming scheduling algorithm using Google OR-Tools CP-SAT.
"""
import pandas as pd
from ortools.sat.python import cp_model

from .data_parser import is_available
from ..utils.time_utils import slots_overlap, get_slots_by_day
from ..config.constants import MAX_DAILY_HOURS, MAX_LABS_PER_TA


class CPSolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Solution callback to track CP-SAT solving progress."""
    
    def __init__(self):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__solution_count = 0
        
    def on_solution_callback(self):
        """Called each time a solution is found."""
        self.__solution_count += 1
        # Solution found callback - silent for GUI
        pass
        
    def solution_count(self):
        return self.__solution_count


def solve_schedule(employees: list, responses_df: pd.DataFrame, max_hours: dict, slots: list, 
                  max_daily_hours: int = MAX_DAILY_HOURS, max_labs_per_ta: int = MAX_LABS_PER_TA,
                  log_func=None):
    """
    Build and solve a CP-SAT model to assign TAs to lab slots.

    The optimization maximizes total assigned hours under coverage
    requirements and individual TA hour limits. Supports partial slot filling
    with preference for fulfilling requirements when possible.

    Additional constraints:
    - No TA can be assigned to overlapping time slots
    - No TA can work more than max_daily_hours hours per day
    - No TA can be assigned to more than max_labs_per_ta different labs

    Args:
        employees (list): List of TA names.
        responses_df (pd.DataFrame): Raw TA availability responses DataFrame.
        max_hours (dict): Mapping TA to maximum hours they can work.
        slots (list): List of slot requirement dicts.
        max_daily_hours (int): Maximum hours per day for any TA.
        max_labs_per_ta (int): Maximum number of labs per TA.
        log_func (callable): Optional logging function for debug output.

    Returns:
        slot_results (list): Coverage summary per slot.
        ta_results (list): Assignment summary per TA.
    """
    # Filter employees who have responses in the DataFrame
    sched = [e for e in employees if e in responses_df['Name'].values]
    
    # Helper function for logging
    def log(message):
        if log_func:
            log_func(message)
        # Only print to console when running standalone (no GUI)
        else:
            print(message)
    
    if not sched:
        raise ValueError("No employees with valid availability data.")
    
    if not slots:
        raise ValueError("No slots to schedule.")

    log(f"Setting up CP model with {len(sched)} TAs and {len(slots)} slots...")
    log(f"Total required positions: {sum(slot['required'] for slot in slots)}")
    log(f"Total available TA hours: {sum(max_hours.get(ta, 0) for ta in sched)}")
    log(f"Max daily hours limit: {max_daily_hours}")
    log(f"Max labs per TA limit: {max_labs_per_ta}")
    log("")

    # Create the CP model
    model = cp_model.CpModel()

    # Decision variables: x[ta_idx][slot_id] = 1 if TA is assigned to slot
    x = {}
    unavailable_assignments = 0
    total_possible_assignments = 0
    
    for ta_idx, ta_name in enumerate(sched):
        x[ta_idx] = {}
        for slot in slots:
            var_name = f'x_{ta_idx}_{slot["id"]}'
            x[ta_idx][slot['id']] = model.NewBoolVar(var_name)
            total_possible_assignments += 1
            
            # Force to 0 if TA is not available for this slot
            if not is_available(ta_name, slot['day'], int(slot['start']), int(slot['end']), responses_df):
                model.Add(x[ta_idx][slot['id']] == 0)
                unavailable_assignments += 1

    log(f"Created {total_possible_assignments} assignment variables")
    log(f"Forced {unavailable_assignments} to zero due to availability constraints")
    log(f"Remaining possible assignments: {total_possible_assignments - unavailable_assignments}")
    log("")

    # Shortage variables: how many TAs are missing from each slot
    shortage = {}
    for slot in slots:
        shortage[slot['id']] = model.NewIntVar(0, slot['required'], f'shortage_{slot["id"]}')

    # Coverage constraints: assigned TAs + shortage = required TAs per slot
    for slot in slots:
        assigned_tas = sum(x[ta_idx][slot['id']] for ta_idx in range(len(sched)))
        model.Add(assigned_tas + shortage[slot['id']] == slot['required'])

    log(f"Added {len(slots)} coverage constraints")

    # Hour limits: do not exceed each TA's hired hours
    hour_constraints = 0
    for ta_idx, ta_name in enumerate(sched):
        total_hours = sum(int(slot['end'] - slot['start']) * x[ta_idx][slot['id']] 
                         for slot in slots)
        model.Add(total_hours <= max_hours.get(ta_name, 0))
        hour_constraints += 1

    log(f"Added {hour_constraints} total hour limit constraints")

    # No overlapping slots constraint: TA cannot be assigned to overlapping time slots
    overlap_constraints = 0
    for ta_idx in range(len(sched)):
        for i, slot1 in enumerate(slots):
            for j, slot2 in enumerate(slots):
                if i < j and slots_overlap(slot1, slot2):
                    # If two slots overlap, TA can be assigned to at most one of them
                    model.Add(x[ta_idx][slot1['id']] + x[ta_idx][slot2['id']] <= 1)
                    overlap_constraints += 1

    log(f"Added {overlap_constraints} no-overlap constraints")

    # Daily hour limits: TA cannot work more than MAX_DAILY_HOURS per day
    daily_constraints = 0
    slots_by_day = get_slots_by_day(slots)
    for ta_idx in range(len(sched)):
        for day, day_slots in slots_by_day.items():
            daily_hours = sum(int(slot['end'] - slot['start']) * x[ta_idx][slot['id']] 
                            for slot in day_slots)
            model.Add(daily_hours <= max_daily_hours)
            daily_constraints += 1

    log(f"Added {daily_constraints} daily hour limit constraints")

    # Lab limit constraint: TA cannot be assigned to more than max_labs_per_ta different labs
    lab_constraints = 0
    for ta_idx in range(len(sched)):
        # For each unique lab, create a binary variable indicating if TA works in that lab
        unique_labs = list(set(slot['section'] for slot in slots))
        lab_indicators = {}
        
        for lab in unique_labs:
            lab_indicators[lab] = model.NewBoolVar(f'lab_indicator_{ta_idx}_{lab}')
            # If TA is assigned to any slot in this lab, the indicator must be 1
            lab_slots = [slot for slot in slots if slot['section'] == lab]
            for slot in lab_slots:
                model.Add(x[ta_idx][slot['id']] <= lab_indicators[lab])
        
        # Total labs assigned to this TA cannot exceed the limit
        model.Add(sum(lab_indicators.values()) <= max_labs_per_ta)
        lab_constraints += 1

    log(f"Added {lab_constraints} lab limit constraints (max {max_labs_per_ta} labs per TA)")
    log(f"Total constraints: {len(slots) + hour_constraints + overlap_constraints + daily_constraints + lab_constraints}")
    log("")

    # Objective: maximize total assigned hours - heavily penalize shortages
    # But also add incentive for partial coverage when full coverage isn't possible
    total_assigned_hours = sum((slot['end'] - slot['start']) * x[ta_idx][slot['id']]
                              for ta_idx in range(len(sched)) for slot in slots)
    total_shortage = sum(shortage[slot['id']] for slot in slots)
    
    # Add bonus for any coverage (encourages partial filling)
    coverage_bonus = sum(x[ta_idx][slot['id']] for ta_idx in range(len(sched)) for slot in slots)
    
    # Use same penalty weight as MILP version for consistency, but add coverage bonus
    shortage_penalty = 1000
    coverage_bonus_weight = 10
    model.Maximize(total_assigned_hours - shortage_penalty * total_shortage + coverage_bonus_weight * coverage_bonus)

    # Solve the model
    solver = cp_model.CpSolver()
    
    # Configure solver parameters for better performance
    solver.parameters.max_time_in_seconds = 60.0  # Time limit
    solver.parameters.log_search_progress = True
    
    # Solution callback to track progress
    solution_printer = CPSolutionPrinter()
    
    print("Solving with CP-SAT...")
    status = solver.Solve(model, solution_printer)

    if status == cp_model.OPTIMAL:
        log("Optimal solution found!")
    elif status == cp_model.FEASIBLE:
        log("Feasible solution found!")
    else:
        log(f"Solver status: {solver.StatusName(status)}")
        if status == cp_model.INFEASIBLE:
            raise ValueError("No feasible solution exists. Try relaxing constraints or reducing requirements.")
        elif status == cp_model.MODEL_INVALID:
            raise ValueError("Invalid model. Please check input data.")
        else:
            raise ValueError(f"Solver failed with status: {solver.StatusName(status)}")

    log(f"Objective value: {solver.ObjectiveValue()}")
    log(f"Solutions found: {solution_printer.solution_count()}")
    log(f"Solve time: {solver.WallTime():.2f} seconds")
    log("")

    # Build slot coverage results
    slot_results = []
    for slot in slots:
        assigned = []
        for ta_idx, ta_name in enumerate(sched):
            if solver.Value(x[ta_idx][slot['id']]):
                assigned.append(ta_name)
        
        shortage_val = solver.Value(shortage[slot['id']])
        
        slot_results.append({
            'Lab Section': slot['section'],
            'Day': slot['day'],
            'Start Time': slot['start'],
            'End Time': slot['end'],
            'Duration (hours)': slot['end'] - slot['start'],
            'TAs Assigned': ', '.join(assigned),
            'Assigned Count': len(assigned),
            'Required Count': slot['required'],
            'Needed': shortage_val
        })

    # Build TA assignment summary
    ta_results = []
    for ta_idx, ta_name in enumerate(sched):
        total_hrs = 0
        assigned_labs = []
        daily_breakdown = {}
        
        # Calculate assignments for this TA
        for slot in slots:
            if solver.Value(x[ta_idx][slot['id']]):
                slot_hours = slot['end'] - slot['start']
                total_hrs += slot_hours
                
                # Track daily hours
                day = slot['day']
                if day not in daily_breakdown:
                    daily_breakdown[day] = 0
                daily_breakdown[day] += slot_hours
                
                # Track lab assignments
                lab_detail = f"{slot['section']} ({slot['day']} {slot['start']}-{slot['end']})"
                assigned_labs.append(lab_detail)
        
        hired = max_hours.get(ta_name, 0)
        rem = hired - total_hrs
        
        daily_info = ', '.join([f"{day}: {hrs}h" for day, hrs in daily_breakdown.items()]) if daily_breakdown else "None"
        labs_info = ', '.join(assigned_labs) if assigned_labs else "None"
        
        ta_results.append({
            'TA Name': ta_name,
            'Hours Assigned': total_hrs,
            'Remaining hours': rem,
            'Hours Hired For': hired,
            'Daily Breakdown': daily_info,
            'Labs Assigned': labs_info
        })

    # Add TAs with no availability data
    for ta_name in employees:
        if ta_name not in sched:
            hired = max_hours.get(ta_name, 0)
            ta_results.append({
                'TA Name': ta_name,
                'Hours Assigned': 0,
                'Remaining hours': hired,
                'Hours Hired For': hired,
                'Daily Breakdown': 'None',
                'Labs Assigned': 'None'
            })

    return slot_results, ta_results
