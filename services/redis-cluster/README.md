# If you need REDIS

The top level `./manage` script does not stand up the redis cluster by default, it must be started manually. 

Redis must connect to the same docker network that the AATH agents use, however it must be created first. You can will need to manually run the command inside the `createNetwork()` function of the `./manage script`, currently line 626 manually.