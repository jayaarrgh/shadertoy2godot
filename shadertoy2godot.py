import os
import re
import sys
import subprocess
# from glob import glob

## Utility to help convert shader toy to godot .shader files
## Requires: PYTHON 3, godot in PATH

## HOW TO: Copy code from shadertoy into files ending in .shader to get started (what about glsl for glslViewer type files?)
## This will not alter the file but create a new folder and put "converted" versions in

## Is not a complete solution - merely a helper to do the boring work
## This just provides a bunch of operations I might as well automate.

#TODO: Mouse (and other UNIFORMS)
    # Need a special method to add a mouse uniform... and it needs a script...
    # s = s.replace('iMouse', 'uMouse') and add a uniform

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

CONVERSION_TABLE = (
            ('fragColor', 'COLOR'),
            ('fragCoord', 'FRAGCOORD.xy'),
            ('iResolution', '(1.0/SCREEN_PIXEL_SIZE)'),
            ('iTime', 'TIME'),
            ('iChannelResolution[4]', '(1.0/TEXTURE_PIXEL_SIZE)'),
            ('void mainImage.*\n\s*{|void mainImage.*{', 'void fragment() {\n')
        )

# compile the conversion table
COMPILED_CONVERSION_TABLE = [(re.compile(e[0], flags=re.M), e[1]) for e in CONVERSION_TABLE]

UNIFORM_TABLE = (('iTimeDelta', 'uniform float iTimeDelta;'),
        ('iFrame', 'uniform float iFrame;'),
        ('iChannelTime\[4\]', 'uniform float iChannelTime[4];'),
        ('iMouse', 'uniform vec4 iMouse;'),
        ('iDate', 'uniform vec4 iDate;'),
        ('iSampleRate', 'uniform float iSampleRate;'),
        ('iChannel/d', 'uniform sampler2D iChannel%d;'))

def typed_uniform(datatype, name): return f'uniform {datatype} {name};\n'

function_define_regex = re.compile('#define.*\(.*') # has a ( in the line 

define_regex = re.compile('(?!.*[\(])#define.*') # doesnt have a ( in the line


class ShadertoyConverter:
    def convert(self, shader_code):
        self._code = shader_code
        self._comment_ifdefs()
        self._sub_conversion_table()
        self._collect_and_add_uniforms()
        self._add_godot_first_line()
        self._convert_defines()
        return self._code
    
    def _comment_ifdefs(self):
        # Comments if blocks but not else blocks
        # TODO: another option would be to create a uniform for the if VAR and set it to false
        commenting = False
        _lines = ''
        for line in self._code.splitlines(True):
            if '#if' in line or '#ifdef' in line:
                commenting = True
            elif '#endif' in line or '#else' in line:
                commenting = False
                _lines += f'// {line}'
                continue
            if commenting:
                _lines += f'// {line}'
            else:
                _lines += line
        self._code = _lines
    
    def _sub_conversion_table(self):
        for shadertoy, godot in COMPILED_CONVERSION_TABLE:
            self._code = shadertoy.sub(godot, self._code) 

    def _add_godot_first_line(self):
        self._code = f'shader_type canvas_item;\n{self._code}'
    
    # TODO: convert defines or comment out
    def _convert_defines(self):
        self._use_finditer(function_define_regex, 'found a function define')
        self._use_finditer(define_regex, 'found a define')

    def _use_finditer(self, regex, msg):
        '''Just printing matches for now...'''
        for match in regex.finditer(self._code):
            print(f'\n{msg}')
            print(match.start(), match.end())
            print(match.group(0))
            # self._code = f'{self._code[:match.start()]}//{self._code[match.start():]}'
    
    # TODO: add uniforms for stuff not in CONVERSION_TABLE -- ex: iMouse
    def _collect_and_add_uniforms(self):
        self._code = f'{self._get_channel_uniforms()}{self._code}'
    
    def _get_channel_uniforms(self):
        # uncompiled regex here
        channels = set([m.group(0) for m in re.finditer('iChannel\d', self._code)]) 
        uniforms = [f'uniform sampler2D {channel};\n' for channel in channels]
        return ''.join(uniforms)

    # TODO: Use GodotShaderCompiler to remove remaining errors
    def _fix_compiled_errors(self):
        pass

            

class GodotShaderCompiler:
    @staticmethod
    def compile(shader_path):
        print('Compiling shader in godot to find errors...')
        command = ('godot', '-s', 'compile_shader.gd', f'--shader={shader_path}')
        compiler = subprocess.Popen(command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE)
        stdout, stderr = compiler.communicate()
        stderr_lines = stderr.splitlines(True)
        if len(stderr_lines) > 4:
            print('ERROR: ', stderr_lines[-4:-2])
        else:
            print('No errors found in compilation')


def convert_shadertoy_shaders():
    def is_shader(filepath):
        return os.path.isfile(os.path.join(the_path, filepath)) \
                and (filepath.endswith('.shader') or filepath.endswith('.glsl'))
    
    def get_shaders(): return [f for f in os.listdir(the_path) if is_shader(f)]
    # shaders = glob(f'{the_path}/*.glsl') + glob(f'{the_path}/*.shader')
    
    converter = ShadertoyConverter()
    
    for shader in get_shaders():
        shader_path = os.path.join(the_path, shader)
        print(f'\nopening shader at: {shader_path}')
        with open(shader_path, 'r') as f:
            shader_code = f.read()
        
        # Run converter
        shader_code = converter.convert(shader_code)
        
        # Write the shader to a file
        shader = shader.replace('.glsl', '.shader')  # convert to .shader ending
        new_shader_path = os.path.join(new_shader_dir, shader)
        with open(new_shader_path, 'w+') as nf:
            nf.write(shader_code)
        print(f'\nshader: {shader} - successfully converted')
        
        ## turn on and off with a argv flag?
        GodotShaderCompiler.compile(new_shader_path)


if __name__ == '__main__':
    convert_shadertoy_shaders()

