# Shader Toy 2 Godot
Handles some of the basic conversion tasks when porting from Shadertoy to Godot as outline in the [Godot Docs](https://docs.godotengine.org/en/3.2/tutorials/shading/migrating_to_godot_shader_language.html)

# How To
1. Copy and paste shader code from shadertoy into a file with .shader (or .glsl) ending. Gather all of these into a single folder.
You can copy the python script into that a folder and run it via `python shadertoy2godot.py`  OR  you can provide a path to the program via the first argument. `python shadertoy2godot path-to-my-shadertoy-shader-folder`
This executable currently creates a folder in current working directory to put all converter.shader files into.


# TODO (Future improvement)
- Convert #defines - both functions and various other const types.
- Comment out #ifdef to #endif OR create a uniform and use it in the if
- Maybe a webscraper variant which will pull the code from a shadertoy link?
