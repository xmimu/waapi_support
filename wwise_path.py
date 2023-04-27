import enum
from pathlib import PurePath


class RootPath:
    master_mixer_hierarchy = PurePath('\\Master-Mixer Hierarchy')
    actor_mixer_hierarchy = PurePath('\\Actor-Mixer Hierarchy')
    interactive_music_hierarchy = PurePath('\\Interactive Music Hierarchy')
    events = PurePath('\\Events')
    dynamic_dialogue = PurePath('\\Dynamic Dialogue')
    sound_banks = PurePath('\\SoundBanks')
    switches = PurePath('\\Switches')
    states = PurePath('\\States')
    game_parameters = PurePath('\\Game Parameters')
    triggers = PurePath('\\Triggers')
    effects = PurePath('\\Effects')
    attenuations = PurePath('\\Attenuations')
    conversion_settings = PurePath('\\Conversion Settings')
    modulators = PurePath('\\Modulators')
    audio_devices = PurePath('\\Audio Devices')
    virtual_acoustics = PurePath('\\Virtual Acoustics')
    soundcaster_sessions = PurePath('\\Soundcaster Sessions')
    mixing_sessions = PurePath('\\Mixing Sessions')
    control_surface_sessions = PurePath('\\Control Surface Sessions')
    queries = PurePath('\\Queries')

    @classmethod
    def path_list(cls):
        ls = []
        for k, v in cls.__dict__.items():
            if not k.startswith('__') and k != 'path_list':
                ls.append(v)
        return ls
