import os
import sys
# from glob import glob


## Utility to help convert shader toy to godot .shader files
## Requires: PYTHON 3

## HOW TO: Copy code from shadertoy into files ending in .shader to get started (what about glsl for glslViewer type files?)
## This will not alter the file but create a new folder and put "converted" versions in

## Is not a complete solution - merely a helper to do the boring work
## This just provides a bunch of operations I might as well automate.

#TODO: Mouse (and other UNIFORMS)
    # Need a special method to add a mouse uniform... and it needs a script...
    # s = s.replace('iMouse', 'uMouse') and add a uniform

#TODO #ifdef #endif -- just comment these out :)

    
if '--help' in sys.argv or '-h' in sys.argv:
    print('\nhelpful message here... :)\n')
    raise SystemExit 

# RELIES ON COMMAND ARGS OR CURRENT DIR
try:
    the_path = sys.argv[1]
except:
    the_path = os.getcwd()

# this could be argv[2]
new_shader_dir = 'shadertoy2godot-shaders'
if not os.path.exists(new_shader_dir):
    os.makedirs(new_shader_dir)


## WHY NOT JUST A FUNCTION WITH CLOUSURE?
class ShadertoyLineConverter:
    CONVERSION_TABLE = [
                ('fragColor', 'COLOR'),
                ('fragCoord', 'FRAGCOORD.xy'),
                ('iResolution', '(1.0/SCREEN_PIXEL_SIZE)'),
                ('iTime', 'TIME'),
                ('iChannelResolution[4]', '(1.0/TEXTURE_PIXEL_SIZE)')
                ]
    
    def __init__(self, line):
       self.line = line

    def convert(self):
        self._convert_mainImage()
        self._convert_vars()
        self._convert_defines()
        self._convert_ifdefs()
        return self.line

    # TODO: add uniforms for stuff not in REPLACER -- ex: iMouse
    def _add_uniforms(self):
       pass
    
    def _convert_vars(self):
        for old, new in ShadertoyLineConverter.CONVERSION_TABLE:
            self.line = self.line.replace(old, new)
    
    def _convert_mainImage(self):
        if not 'void mainImage' in self.line: return
        if '{' in self.line:
            self.line = 'void fragment() {\n'
        else:
            self.line = 'void fragment()\n' 

    # TODO: Replace defines with const (float, vec2? how do we know?)
    def _convert_defines(self):
        if not "#define" in self.line: return
        if "(" in self.line:  # we are in a function define
            self._convert_function_define()
        else:
            self._convert_typed_define()

    # TODO: comment every line until endif - But then its not in line parser...
    def _convert_ifdefs(self):
        if '#ifdef' in self.line or '#endif' in self.line:
            self.line = f'// {self.line}' # comment out the line
    
    def _convert_function_define(self):
        print('found a function #define - no action taken')

    def _convert_typed_define(self):
        print('found a #define - no action taken')
        # if is defining a const? # letters followed by space followed by numbers?
        # psedo---type_ = 'float' || 'int' || 'vec2' || 'vec3'
        # s.replace('#define', f'const {type_}')
        # s.replace_last_space(' ', '= ')


def convert_shadertoy_shaders():
    def is_shader(filepath):
        return os.path.isfile(os.path.join(the_path, filepath)) \
                and (filepath.endswith('.shader') or filepath.endswith('.glsl'))
    
    def get_shaders(): return [f for f in os.listdir(the_path) if is_shader(f)]
    # shaders = glob(f'{the_path}/*.glsl') + glob(f'{the_path}/*.shader')
    
    def add_godot_first_line(s): return f'shader_type canvas_item;\n{s}'
    
    for shader in get_shaders():
        new_shader_code = ""
        shader_path = os.path.join(the_path, shader)
        print(f'\nopening shader at: {shader_path}')
        with open(shader_path, 'r') as f:
            for line in f:
                new_shader_code += ShadertoyLineConverter(line).convert()

        # add the first line
        new_shader_code = add_godot_first_line(new_shader_code)
        
        # TODO: loop through again??? to comment out lines between ifdef && endif

        # print(f'\n{new_shader_code}\n')
        # Write the shader to a file
        shader = shader.replace('.glsl', '.shader')
        nf = open(os.path.join(new_shader_dir, shader), 'w+')
        nf.write(new_shader_code)
        nf.close()
        print(f'shader: {shader} - successfully converted')

if __name__ == '__main__':
    convert_shadertoy_shaders()

