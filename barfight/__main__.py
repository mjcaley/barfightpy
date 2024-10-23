import cProfile
import pstats

from .cli import main

profile = cProfile.Profile()
# profile.enable()
# main()
print("Starting")
profile.runcall(main)
print("Stopping")
profile.disable()
stats = pstats.Stats(profile).sort_stats("time").print_stats("barfight")
print(stats)
