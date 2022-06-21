import glob
import os
import queue
import sys
import time

import numpy as np
np.set_printoptions(threshold=sys.maxsize)
from pypcd import pypcd # Modified the source of this file!!!

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

import carla
import logging
import random

HOST = "127.0.0.1"
PORT = 2000
TM_PORT = 8000
SEED = 10
FPS = 20
SPEED_DIFF_PERCENT = 30
DISTANCE_TO_LEADING_VEHICLE = 1.0


'''
    All the input and output parameters match with depth camera. In addition range parameter was introduced.
    Output data contains xyz-coordinates array, where each row represents point in local camera space.
'''
def add_lightcode_camera(world, vehicle, queue):
    lightcode_bp = world.get_blueprint_library().find('sensor.camera.lightcode')
    lightcode_bp.set_attribute('image_size_x', str(96))
    lightcode_bp.set_attribute('image_size_y', str(16))
    lightcode_bp.set_attribute('fov', str(80))
    lightcode_bp.set_attribute('range', str(30.0)) # Maximum detection range of the camera
    
    lightcode_transform = carla.Transform(carla.Location(2, 0, 1), carla.Rotation(0, 0, 0))
    lightcode_cam = world.spawn_actor(lightcode_bp, lightcode_transform, attach_to=vehicle, attachment_type=carla.AttachmentType.Rigid)
    lightcode_cam.listen(queue.put)
    return lightcode_cam


def main():
    global HOST, PORT, TM_PORT, FPS, \
        SEED, SPEED_DIFF_PERCENT, DISTANCE_TO_LEADING_VEHICLE

    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.INFO)

    random.seed(SEED)

    client = carla.Client(HOST, PORT)
    client.set_timeout(10.0)
    sync = True

    print("Started client")

    try:
        world = client.get_world()
        client.load_world("Town02_Opt")

        # Change world parameters
        current_settings = world.get_settings()
        current_settings.synchronous_mode = sync
        current_settings.fixed_delta_seconds = 1/FPS
        current_settings.no_rendering_mode = False
        world.apply_settings(current_settings)
        client.reload_world(False)
        print("Map settings done")

        # Set up the traffic manager
        traffic_manager = client.get_trafficmanager(TM_PORT)
        traffic_manager.set_synchronous_mode(sync)
        traffic_manager.set_global_distance_to_leading_vehicle(DISTANCE_TO_LEADING_VEHICLE)
        traffic_manager.set_random_device_seed(SEED)
        traffic_manager.global_percentage_speed_difference(SPEED_DIFF_PERCENT)
        print("Traffic manager done")

        # Spawn hero vehicle
        hero_bp = world.get_blueprint_library().find('vehicle.tesla.model3')
        hero_bp.set_attribute('role_name', 'hero')
        hero_color = random.choice(hero_bp.get_attribute('color').recommended_values)
        hero_bp.set_attribute('color', hero_color)
        spawn_points = world.get_map().get_spawn_points()
        number_of_spawn_points = len(spawn_points)

        if 0 < number_of_spawn_points:
            random.shuffle(spawn_points)
            hero_transform = spawn_points[0]
            hero_vehicle = world.spawn_actor(hero_bp, hero_transform)

            hero_vehicle.set_autopilot(True)

            # Hero car accessories
            hero_lightcode = None
            lightcode_queue = queue.Queue()
            hero_lightcode_cam = add_lightcode_camera(world, hero_vehicle, lightcode_queue)

            print('Hero is spawned')
            
        else: 
            logging.warning('Could not found any spawn points for hero')

        while True:
            if sync:
                world.tick()

                if not lightcode_queue.empty():
                    lightcode_image = lightcode_queue.get()
                    
                    # Array of xyz-coordinates, where each row represents one point in local space. Coordinates are left handed.
                    xyz_coordinates = np.ndarray(shape=((lightcode_image.width * lightcode_image.height), 3), dtype=np.float32, buffer=lightcode_image.raw_data)
                    
                    # Possibility to save .pcd files
                    #point_cloud_to_save = pypcd.make_xyz_point_cloud(xyz_coordinates.copy()) 
                    #pypcd.save_point_cloud_bin(point_cloud_to_save, "../output/lightcode/{frame}_.pcd".format(frame=lightcode_image.frame))
                
            else:
                print("Cannot work in async mode, fix me!")
    finally:
        if sync:
            settings = world.get_settings()
            settings.synchronous_mode = False
            settings.no_rendering_mode = False
            settings.fixed_delta_seconds = None
            world.apply_settings(settings)


        if hero_vehicle is not None:
            if hero_lightcode_cam is not None:
                hero_lightcode_cam.stop()
                hero_lightcode_cam.destroy()
            hero_vehicle.destroy()



if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\nDone\n')
        raise
