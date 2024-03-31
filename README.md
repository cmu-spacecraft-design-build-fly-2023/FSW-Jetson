# Flight Software for the Argus-1 Payload

The repository contains the current flight software stack for the **Jetson Board** within Argus-1.  Argus-1 is a technology demonstration mission with the goal of:
- Demonstrating Visual Attitude and Orbit Determination (A&OD) on a low-cost satellite (Independance from any GPS or ground involvement in the A&OD process)
- Collecting a dataset of images of the Earth to further efforts in CubeSat visual applications.
- Demonstrating efficient on-orbit ML/GPU Payload processing 


## Environment Variables (temp)

Set the PYTHONPATH environment variable to include the root of project to make the package flight discoverable.

```bash
export PYTHONPATH="/path/to/project_root:$PYTHONPATH"
```