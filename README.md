# Shader Toy 2 Godot
Handles some of the basic conversion tasks when porting from Shadertoy to Godot as outlined in [Migrating to Godot Shader Language](https://docs.godotengine.org/en/3.2/tutorials/shading/migrating_to_godot_shader_language.html)

# How To
This script creates a folder in current working directory with converted .shader files.
1. Copy and paste shader code from shadertoy into a file with .shader (or .glsl) ending. Gather all of these into a single folder.
2. You can copy the python script into that a folder and run `python shadertoy2godot.py` 

	OR  

	you can provide a path to the program via the first argument.
	
	`python shadertoy2godot path-to-my-shadertoy-shader-folder`



# TODO (Future improvement)
- Convert #define F() --Functional defines are currently commented out
- Currently commenting out #ifdef to #endif -- instead use created const in the if
- Create another script to integrate shadertoy api
