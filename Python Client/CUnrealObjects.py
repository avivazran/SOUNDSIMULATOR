import abc
import requests
import os
import time


class Singleton(abc.ABCMeta):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class UnrealSoundSimulator(metaclass=Singleton):
    class _CUnrealClient(metaclass=Singleton):
        def __init__(self):
            self._host = 'http://127.0.0.1:8051/'
            os.environ['NO_PROXY'] = '127.0.0.1'

        def send_request(self, url, payload=None):
            address = self._host + url
            if payload is None:
                r = requests.get(address)
            else:
                r = requests.get(address, payload)
            return r

    class _Room(metaclass=Singleton):
        def __init__(self, unreal_client):
            self._unreal_client = unreal_client
            self._url = '/Room/'
            self._materials_list = ['Wood', 'Brick', 'Carpet',
                                    'Rock', 'Plaster', 'Glass',
                                    'Concrete', 'Metal']
            self._current_material = 'Concrete'
            self._min_size = 0.5

        def set_material(self, new_material: str):
            if new_material in self._materials_list:
                address = self._url + 'SetMaterial'
                payload = dict(material=new_material)
                r = self._unreal_client.send_request(address, payload)
                print(r.text)
                self._current_material = new_material
            else:
                print('ERROR: Invalid Material!\nAvailable materials are {0}'.format(self._materials_list))

        def available_materials(self):
            materials = tuple(self._materials_list)
            return materials

        @property
        def current_material(self):
            return self._current_material

        def get_dimensions(self):
            r = self._unreal_client.send_request(self._url + 'GetDimensions').json()
            return r

        def set_dimensions(self, x, y, z):
            url = self._url + 'SetDimensions'
            payload = dict(x=x, y=y, z=z)
            r = self._unreal_client.send_request(url, payload)

    class SoundObject:
        _url: str
        _name: str

        class _OrbitalMotionComponent:
            def __init__(self, name, unreal_client):
                self._name = name
                self._url = '/{0}/'.format(self._name) + 'OrbitHandler'
                self._client = unreal_client

            def orbit_start(self):
                payload = dict(what='Orbit Start')
                r = self._client.send_request(self._url, payload).json()

            def set_orbit_center(self, x, y, z):
                payload = dict(what='Orbit Set Center', x=x, y=y, z=z)
                r = self._client.send_request(self._url, payload).json()
                print(r['Details'])
                return r['Success']

            def set_orbit_rotation(self, x, y, z):
                payload = dict(what='Orbit Set Orbit Rotation', x=x, y=y, z=z)
                r = self._client.send_request(self._url, payload).json()
                print(r['Details'])
                return r['Success']

            def set_orbit_radius(self, x, y):
                payload = dict(what='Orbit Set Radius', x=x, y=y)
                r = self._client.send_request(self._url, payload).json()
                print(r['Details'])
                return r['Success']

            def set_orbit_start_angle(self, angle: float):
                payload = dict(what='Orbit Set Start Angle', angle=angle)
                r = self._client.send_request(self._url, payload).json()
                print(r['Details'])
                return r['Success']

            def set_movement_speed(self, speed: float):
                payload = dict(what='Orbit Set Movement Speed', speed=speed)
                r = self._client.send_request(self._url, payload).json()
                print(r['Details'])
                return r['Success']

            def set_default_rotation(self, x, y, z):
                payload = dict(what='Orbit Set Object Default Rotation', x=x, y=y, z=z)
                r = self._client.send_request(self._url, payload).json()
                print(r['Details'])
                return r['Success']

            def set_rotation_speed(self, vx, vy, vz):
                payload = dict(what='Orbit Set Object Rotation Speed', x=vx, y=vy, z=vz)
                r = self._client.send_request(self._url, payload).json()
                print(r['Details'])
                return r['Success']

            def set_rotate_relative_to_orbit(self, bValue: str):
                payload = dict(what='Orbit Rotate Relative To Orbit', bValue=str(bValue))
                r = self._client.send_request(self._url, payload).json()
                print(r['Details'])
                return r['Success']

            def enable_orbital_motion(self, bValue: str):
                payload = dict(what='Orbit Toggle Enabled', bValue=str(bValue))
                r = self._client.send_request(self._url, payload).json()
                print(r['Details'])
                return r['Success']

            def toggle_show_orbit(self, bValue: str):
                payload = dict(what='Toggle Orbit Show', bValue=str(bValue))
                r = self._client.send_request(self._url, payload).json()
                print(r['Details'])
                return r['Success']

            def get_orbital_settings(self):
                """

                Returns - current orbital motion settings of the object
                -------

                """
                what = 'Get Orbital Movement Settings'
                payload = dict(what=what)
                r = self._client.send_request(self._url, payload=payload).json()
                print(r)
                return r

        def __init__(self, name, unreal_client):
            self._name = name
            self._url = '/{0}/'.format(self._name)
            self._client = unreal_client
            self._orbital_motion = self._OrbitalMotionComponent(name, unreal_client)

        @property
        def name(self):
            return self._name

        def set_location(self, x: float, y: float, z: float):
            """
            sets the object location in the scene with respect
            to center of the room (0,0,0)

            Parameters
            ----------
            x - x coordinates in meters
            y - y coordinates in meters
            z - z coordinates in meters

            Returns
            -------

            """
            url = self._url + 'SetLocation'
            payload = dict(x=x, y=y, z=z)
            r = self._client.send_request(url, payload)
            return r

        def get_location(self):
            url = self._url + 'GetLocation'
            r = self._client.send_request(url)
            return r

        def init_orbital_movement(self):
            """
            initiates the orbital movement component and enables movement.
            must be called once before gaining ability
            to change any motion parameter
            Returns
            -------

            """
            return self._orbital_motion.orbit_start()

        def toggle_show_orbit(self, bValue: bool):
            return self._orbital_motion.toggle_show_orbit(bValue=str(bValue))

        def set_orbit_rotation(self, x, y, z):
            return self._orbital_motion.set_orbit_rotation(x, y, z)

        def set_orbit_center(self, x, y, z):
            return self._orbital_motion.set_orbit_center(x, y, z)

        def set_orbit_radius(self, x, y):
            return self._orbital_motion.set_orbit_radius(x, y)

        def set_orbit_start_angle(self, angle):
            return self._orbital_motion.set_orbit_start_angle(angle)

        def set_movement_speed(self, speed):
            """
            sets the angular velocity of the object in orbit

            Parameters
            ----------
            speed - angular velocity in [deg/sec]

            Returns
            -------

            """
            return self._orbital_motion.set_movement_speed(speed)

        def set_default_rotation(self, x, y, z):
            return self._orbital_motion.set_default_rotation(x, y, z)

        def set_rotation_speed(self, vx, vy, vz):
            return self._orbital_motion.set_rotation_speed(vx, vy, vz)

        def set_rotate_relative_to_orbit(self, bValue):
            return self._orbital_motion.set_rotate_relative_to_orbit(bValue)

        def enable_orbital_motion(self, bValue):
            return self._orbital_motion.enable_orbital_motion(bValue)

        def get_orbital_settings(self):
            return self._orbital_motion.get_orbital_settings()

    class SoundSource(SoundObject):
        def __init__(self, name, unreal_client):
            assert isinstance(name, str)
            super().__init__(name, unreal_client)
            self._wav_path = None
            self._wav_duration = None

        def set_wav_path(self, path: str):
            url = self._url + 'SetSoundWave'
            payload = dict(path=path)
            r = self._client.send_request(url, payload).json()
            print(r['Details'])
            return r['Success']

        def play_sound(self):
            r = self._client.send_request(self._name + '/PlaySound')
            print(r.text)

        def set_delay(self, delay: float):
            url = self._url + 'SetDelay'
            payload = dict(delay=delay)
            r = self._client.send_request(url, payload).json()
            print(r['Details'])
            return r['Success']

        def get_soundwave_details(self):
            url = self._url + 'SoundWaveDetails'
            r = self._client.send_request(url).json()
            return r

        def set_volume_multiplier(self, mult: float):
            url = self._url + 'VolumeMultiplier'
            payload = dict(multiplier=mult)
            r = self._client.send_request(url, payload).json()
            print(r['Details'])
            return r['Success']

    class Microphone(SoundObject):
        def __init__(self, name: str, unreal_client):
            super().__init__(name, unreal_client)

        def set_rotation(self, x, y, z):
            url = self._url + 'SetRotation'
            payload = dict(x=x, y=y, z=z)
            r = self._client.send_request(url, payload)
            return r

        def get_rotation(self):
            url = self._url + 'GetRotation'
            r = self._client.send_request(url)
            return r

    def __init__(self):
        self._url = 'Level/'
        self._unreal_client = self._CUnrealClient()
        self._path_to_export_wav = 'C:/'

    def set_path_to_export(self, path: str):
        self._path_to_export_wav = path

    def set_saved_wav_file_name(self, filename: str):
        self._saved_wav_file_name = filename

    @property
    def room(self):
        return self._Room(self._unreal_client)

    def add_sound_source(self, source_name: str, x=0, y=0, z=0):
        payload = dict(name=source_name, x=x, y=y, z=z)
        r = self._unreal_client.send_request(url='/Level/AddSoundSource', payload=payload).json()
        print(r['Details'])
        new_sound_source = None
        if r['Success']:
            new_sound_source = self.SoundSource(name=source_name, unreal_client=self._unreal_client)
        return new_sound_source

    def destroy_sound_source(self, source_name: str):
        r = self._unreal_client.send_request(url='/Level/DestroySoundSource', payload=dict(name=source_name)).json()
        print(r['Details'])
        return r['Success']

    def destroy_sound_source(self, sound_source_object: SoundSource):
        r = self._unreal_client.send_request(url='/Level/DestroySoundSource',
                                             payload=dict(name=sound_source_object.name)).json()
        print(r['Details'])
        return r['Success']

    def destroy_microphone(self, mic_name: str):
        r = self._unreal_client.send_request(url='/Level/DestroyMicrophone', payload=dict(name=mic_name)).json()
        print(r['Details'])
        return r['Success']

    def destroy_microphone(self, mic_object: Microphone):
        r = self._unreal_client.send_request(url='/Level/DestroyMicrophone',
                                             payload=dict(name=mic_object.get_name())).json()
        print(r['Details'])
        return r['Success']

    def add_microphone(self, microphone_name: str, x=0, y=0, z=0):
        payload = dict(name=microphone_name, x=x, y=y, z=z)
        r = self._unreal_client.send_request(url='/Level/AddMicrophone', payload=payload).json()
        print(r['Details'])
        new_mic = None
        if r['Success']:
            new_mic = self.Microphone(name=microphone_name, unreal_client=self._unreal_client)
        return new_mic

    def set_mic_as_current_listener(self, mic_name: str):
        r = self._unreal_client.send_request(url='/Level/SetListener', payload=dict(name=mic_name)).json()
        print(r['Details'])
        return r['Success']

    def start_simulation(self, save_path: str):
        payload = dict(path=save_path)
        r = self._unreal_client.send_request(url='/Level/Start Simulation', payload=payload).json()
        print(r['Details'])
        if r['Success']:
            print('Expected Duration: {0}'.format(r['Expected Duration']))
        return r['Success'], r['Expected Duration']

    def cancel_simulation(self):
        r = self._unreal_client.send_request(url='/Level/Reset')
        time.sleep(1)
        return r

    def reset(self):
        r = self._unreal_client.send_request(url='/Level/CancelSimulation')
        time.sleep(1)
        return r

    def exit_simulator(self):
        r = self._unreal_client.send_request(url='/Level/Exit')
        return r

    # Global Sound Settings
    def set_default_sound_settings(self):
        payload = dict(what='Set Defaults')
        r = self._unreal_client.send_request(url='/Level/SoundSettings', payload=payload).json()
        return r['Details']

    def set_speed_of_sound(self, speed_of_sound: float):
        payload = dict(what='Speed Of Sound', speed_of_sound=speed_of_sound)
        r = self._unreal_client.send_request(url='/Level/SoundSettings', payload=payload).json()
        return r['Details']

    def set_physics_based_attenuation(self, bValue: bool):
        payload = dict(what='Physics Based Attenuation', bValue=str(bValue))
        r = self._unreal_client.send_request(url='/Level/SoundSettings', payload=payload).json()
        return r['Details']

    def set_air_absorption(self, bValue: bool):
        payload = dict(what='Air Absorption', bValue=str(bValue))
        r = self._unreal_client.send_request(url='/Level/SoundSettings', payload=payload).json()
        return r['Details']

    def set_sound_occlusion_source_radius(self, radius: float):
        payload = dict(what='Sound Occlusion Source Radius', radius=radius)
        r = self._unreal_client.send_request(url='/Level/SoundSettings', payload=payload).json()
        return r['Details']

    def _set_direct_occlusion_mode(self, mode: str):
        payload = dict(what='Direct Occlusion Method', method=mode)
        r = self._unreal_client.send_request(url='/Level/SoundSettings', payload=payload).json()
        return r['Details']

    def set_direct_occlusion_mode_no_transmission(self):
        return self._set_direct_occlusion_method(method='Direct Occlusion, No Transmission')

    def set_direct_occlusion_mode_none(self):
        return self._set_direct_occlusion_method(method='None')

    def set_direct_occlusion_mode_frequency_independent_transmission(self):
        return self._set_direct_occlusion_method(method='Direct Occlusion, Frequency Independent Transmission')

    def set_direct_occlusion_mode_frequency_dependent_transmission(self):
        return self._set_direct_occlusion_method(method='Direct Occlusion, Frequency Dependent Transmission')

    def _set_direct_occlusion_method(self, method: str):
        payload = dict(what='Direct Occlusion Mode', mode=method)
        r = self._unreal_client.send_request(url='/Level/SoundSettings', payload=payload).json()
        return r['Details']

    def set_direct_occlusion_method_partial(self):
        return self._set_direct_occlusion_method('Partial')

    def set_direct_occlusion_method_raycast(self):
        return self._set_direct_occlusion_method('Raycast')

    def get_global_sound_settings(self):
        payload = dict(what='Settings')
        r = self._unreal_client.send_request(url='/Level/SoundSettings', payload=payload).json()
        return r

    def play_all_sounds(self):
        r = self._unreal_client.send_request(url='/Level/PlayAllSounds')
        return r
