extends MainLoop

# INFO:
# This script will compile a shader and throw any errors
# Run this script with `godot -s compile_shader.gd --shader=path/to/myshader.shader`

var _quit = false

func _initialize(): # virtual override
	var shader_path = get_shader_path()
	var file = File.new()
	var file_exists = file.file_exists(shader_path)
	print('FILE EXISTS: ', file_exists)
	if file_exists:
		file.open(shader_path, File.READ)
		var text = file.get_as_text()
		file.close()
		compile_shader(text)
	_quit = true

func _idle(delta): # virtual override - returning true quits MainLoop
	return _quit

func get_shader_path():
	var args = Array(OS.get_cmdline_args())
	for arg in args:
		if '--shader=' in arg:
			arg = arg.lstrip('--shader')
			arg = arg.lstrip('=') # lstrip acts funky, needs ran twice
			return arg
	return ""

func compile_shader(text):
	# NOTE: s.set_custom_defines() # we can put the defines from shadertoy here!
	# Set the code on the Shader
	var s = Shader.new()
	s.set_code(text)
	
	# Use the Shader in ShaderMaterial
	var sm = ShaderMaterial.new()
	sm.set_shader(s)
	
	# Create a ColorRect and use the ShaderMaterial
	# setting the material is compiling the shader and throwing any errors
	var colorRect = ColorRect.new()
	colorRect.material = sm

