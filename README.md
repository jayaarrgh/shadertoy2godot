# Shader Toy 2 Godot
Handles some of the basic conversion tasks when porting from Shadertoy to Godot as outlined in [Migrating to Godot Shader Language](https://docs.godotengine.org/en/3.2/tutorials/shading/migrating_to_godot_shader_language.html)

# How To
This script creates a folder in current working directory with converted .shader files.
1. Copy and paste shader code from shadertoy into a file with .shader (or .glsl) ending. Gather all of these into a single folder.
2. You can copy the python script into that a folder and run `python shadertoy2godot.py` 

	OR  

	you can provide other flags and arguments
	
	`python shadertoy2godot.py -i ../my/shadertoy/folder -o new_folder --gdcompile -cid`

For help use: `python shadertoy2godot.py -h`

# TODO (Future improvement)
- Convert #define F() --Functional defines are currently commented out
- Create another script/arg to integrate shadertoy api
