
import pygame
import os

main_dir = os.path.split(os.path.abspath(__file__))[0]


def load_sound(file):
    """ Load a sound from the data/sounds directory. """
    file = os.path.join(main_dir, 'data/sounds', file)
    try:
        sound = pygame.mixer.Sound(file)
    except pygame.error:
        raise SystemExit('Could not load sound "%s" %s' % (file, pygame.get_error()))
    return sound


explosion_sound = load_sound('explosion.wav')  # Sound of an explosion

flag_capture_sound = load_sound('flag_capture.wav')  # Sound of capturing the flag

movement_sound = load_sound('movement.wav')  # Sound of a tank moving

start_sound = load_sound('start_sound.wav')  # Sound of the game starting

tankshot_sound = load_sound('tankshot.wav')  # Sound of a tank shooting

