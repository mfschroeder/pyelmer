import os
import gmsh
from pyelmer import elmer
from pyelmer import execute
from pyelmer.gmsh_utils import add_physical_group, get_boundaries_in_box


###############
# set up working directory
sim_dir = './examples/simdata'

if not os.path.exists(sim_dir):
    os.mkdir(sim_dir)

###############
# geometry modeling using gmsh
gmsh.initialize()
gmsh.option.setNumber("General.Terminal", 1)
gmsh.model.add('heat-transfer-2d')
factory = gmsh.model.occ

# main bodies
water =  factory.addRectangle(0, 0, 0, 1, 1)
air = factory.addRectangle(0, 1, 0, 1, 1)

# create connection between the two bodies
factory.synchronize()
factory.fragment([(2, water)], [(2, air)])

# add physical groups
factory.synchronize()
ph_water = add_physical_group(2, [water], 'water')
ph_air = add_physical_group(2, [air], 'air')

# detect boundaries 
line = get_boundaries_in_box(0, 0, 0, 1, 0, 0, 2, water)
ph_bottom = add_physical_group(1, [line], 'bottom')
line = get_boundaries_in_box(0, 2, 0, 1, 2, 0, 2, air)
ph_top = add_physical_group(1, [line], 'top')

# create mesh
gmsh.model.mesh.setSize(gmsh.model.getEntities(0), 0.1)
gmsh.model.mesh.generate(2)

# show mesh & export
gmsh.fltk.run()
gmsh.write(sim_dir + '/case.msh2')  # use legacy file format msh2 for elmer grid

###############
# elmer setup
sim = elmer.load_simulation('2D_steady')

air = elmer.load_material('air', sim)
water = elmer.load_material('water', sim)

solver_heat = elmer.load_solver('HeatSolver', sim)
solver_output = elmer.load_solver('ResultOutputSolver', sim)
eqn = elmer.Equation(sim, 'main', [solver_heat])

T0 = elmer.InitialCondition(sim, 'T0', {'Temperature': 273.15})

bdy_water = elmer.Body(sim, 'water', [ph_water])
bdy_water.material = water
bdy_water.initial_condition = T0
bdy_water.equation = eqn

bdy_air = elmer.Body(sim, 'air', [ph_air])
bdy_air.material = air
bdy_air.initial_condition = T0
bdy_air.equation = eqn

bndry_bottom = elmer.Boundary(sim, 'bottom', [ph_bottom])
bndry_bottom.fixed_temperature = 353.15  # 80 °C
bndry_top = elmer.Boundary(sim, 'top', [ph_top])
bndry_top.fixed_temperature = 293.15  # 20 °C

sim.write_startinfo(sim_dir)
sim.write_sif(sim_dir)

##############
# execute ElmerGrid & ElmerSolver
execute.run_elmer_grid(sim_dir, 'case.msh2')
execute.run_elmer_solver(sim_dir)