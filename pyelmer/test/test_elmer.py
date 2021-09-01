import pytest
import yaml
import gmsh
from pyelmer.gmsh import add_physical_group, get_boundaries_in_box
from pyelmer import elmer

elmer.data_dir = "./test_data"


def test_body():
    #setup gmsh
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 1)
    gmsh.model.add("test-2d")
    factory = gmsh.model.occ

    #create test domain
    test_domain = factory.addRectangle(0, 0, 0, 1, 1)
    ph_test_body = add_physical_group(2, [test_domain], "test_material")

    #setup simulation
    sim = elmer.Simulation()
    test_initial_condtion = elmer.InitialCondition(sim, "T0", {"Temperature": 1.0})
    test_solver = elmer.Solver(sim, "test_solver",  data={'Equation': 'HeatSolver', 
    'Procedure': '"HeatSolve" "HeatSolver"', 
    'Variable': '"Temperature"', 
    'Variable Dofs': 1, 
    'Calculate Loads': True, 
    'Exec Solver': 'Always', 
    'Nonlinear System Convergence Tolerance': 1e-06, 
    'Nonlinear System Max Iterations': 1000, 
    'Nonlinear System Relaxation Factor': 0.7, 
    'Steady State Convergence Tolerance': 1e-06, 
    'Stabilize': True, 
    'Optimize Bandwidth': True, 
    'Linear System Solver': 'Iterative', 
    'Linear System Iterative Method': 'BiCGStab', 
    'Linear System Max Iterations': 1000, 
    'Linear System Preconditioning': 'ILU', 
    'Linear System Precondition Recompute': 1, 
    'Linear System Convergence Tolerance': 1e-08, 
    'Linear System Abort Not Converged': True, 
    'Linear System Residual Output': 1,
    'Smart Heater Control After Tolerance': 0.0001})
    test_eqn = elmer.Equation(sim, "main", [test_solver])

    #setup body object
    test_body = elmer.Body(sim, "test_material", [ph_test_body])

    #initialize body data
    test_material = {'Density': 1.0, 'Heat Capacity': 1.0, 'Heat Conductivity': 1.0}
    test_body.material = elmer.Material(sim, "test_material", data=test_material)
    test_body.initial_condition = test_initial_condtion
    test_body.equation = test_eqn

    assert test_body.get_data() == {'Target Bodies(1)': '1', 'Equation': '0  ! main', 'Initial Condition': '0  ! T0', 'Material': '0  ! test_material'}


def test_boundary():
    # setup gmsh
    gmsh.initialize()
    gmsh.option.setNumber("General.Terminal", 1)
    gmsh.model.add("test-2d")
    factory = gmsh.model.occ

    # create test domain
    test_domain = factory.addRectangle(0, 0, 0, 1, 1)
    factory.synchronize()
    
    # detect boundary
    line = get_boundaries_in_box(0, 0, 0, 1, 0, 0, 2, test_domain)
    ph_test_boundary = add_physical_group(1, [line], "test_boundary")

    #setup simulation
    sim = elmer.Simulation()
    # initialize boundary data
    test_boundary = elmer.Boundary(sim, "test_boundary", [ph_test_boundary])
    test_boundary.data.update({"Temperature": 1.0})
    assert test_boundary.get_data() == {'Target Boundaries(1)': '1', 'Temperature': 1.0}


def test_material():
    pass


def test_body_force():
    pass


def test_initial_condition():
    sim = elmer.Simulation()
    T0 = elmer.InitialCondition(sim, "T0", {"Temperature": 1.0})
    assert T0.get_data() == {"Temperature": 1.0}


def test_solver():
    pass


def test_equation():
    pass


@pytest.mark.parametrize("name", [
    "2D_steady",
    "2D_transient",
    "axi-symmetric_steady",
    "axi-symmetric_transient",
])
def test_load_simulation(name):
    with open("./test_data/simulations.yml") as f:
        settings = yaml.safe_load(f)[name]
    assert elmer.load_simulation(name).settings == settings


@pytest.mark.parametrize("material", [
    "air",
    "water",
    "tin_liquid",
    "tin_solid",
])
def test_load_material(material):
    with open("./test_data/materials.yml") as f:
        data = yaml.safe_load(f)[material]
    sim = elmer.Simulation()
    assert elmer.load_material(material, sim).get_data() == data


@pytest.mark.parametrize("solver", [
    "ThermoElectricSolver",
    "HeatSolver",
    "MagnetoDynamics2DHarmonic",
    "MagnetoDynamicsCalcFields",
    "StatMagSolver",
    "SaveMaterials",
    "ResultOutputSolver",
    "FluxSolver",
    "SaveScalars",
    "SaveLine",
    "SteadyPhaseChange",
])
def test_load_solver(solver):
    with open("./test_data/solvers.yml") as f:
        data = yaml.safe_load(f)[solver]
    sim = elmer.Simulation()
    assert elmer.load_solver(solver, sim).get_data() == data