import opensim

model = opensim.Model("/mnt/d/progress/MotionEq/sim_models/full_body/gait2392_simbody.osim")
model.initSystem()
coords = model.getCoordinateSet()
for i in range(coords.getSize()):
    coord = coords.get(i)
    print(coord.getName())
