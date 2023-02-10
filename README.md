# PBR-textures-for-Clarisse
Create the relevant mapFile nodes and other nodes to connect an existing PBR texture set on disk.

The "features" of the script..

- It will create the reorder nodes if the texture set is an ARM set.
- Set if the textures should use triplanar projections.
- Creates, renames and organizes the mapFiles, utility nodes in proper contexts.
- Change existing texture sets as well!

The "Bugs" of the script

- You have to click and select an item from both shader and material lists. Even though the list may show a selection you already want. Otherwise it doesnt capture the selected value.
- If you select an already existing shader with textures attached whcih were NOT created with this script, it will probably not work. 

![summary](https://i.ibb.co/qNmHzZ5/PBR-Texture-set-help.jpg)
