import os
import re
import sys
import argparse
import subprocess
# from glob import glob

## Utility to convert shadertoy code to godot .shader files
## Requires: PYTHON 3, godot in PATH

# TODO: make commented bool defines false
# TODO: convert instead of commenting #ifdefs

argparser = argparse.ArgumentParser(description='Convert Shadertoy to Godot.')
argparser.add_argument('-i', help='input path - defaults to current directory')
argparser.add_argument('-o', help='output path - default to new folder in current directory, or relative path')
argparser.add_argument('-cid', action='store_true', help='convert if defs - commented out otherwise')
argparser.add_argument('--gdcompile', action='store_true', help='use godot compilation')

# parse the args
args = argparser.parse_args()

# this logic here isn't needed either
input_path = args.i if args.i else os.getcwd()
output_path = args.o if args.o else os.getcwd() + '/shadertoy2godot-shaders/'

gdcompile = args.gdcompile
cid = args.cid


if not os.path.exists(output_path):
    os.makedirs(output_path)

CONVERSION_TABLE = (
        ('fragColor', 'COLOR'),
        ('fragCoord', 'FRAGCOORD.xy'),
        ('iResolution', '(1.0/SCREEN_PIXEL_SIZE)'),
        # TIME is a problem, if iTime is used in functions other than mainImage
        ('iTime', 'TIME'),
        ('iChannelResolution[4]', '(1.0/TEXTURE_PIXEL_SIZE)'),
        ('void mainImage.*\n\s*{|void mainImage.*{', 'void fragment() {\n')
        )

# compile the conversion table
COMPILED_CONVERSION_TABLE = tuple((re.compile(e[0], flags=re.M), e[1]) for e in CONVERSION_TABLE)
del CONVERSION_TABLE

UNIFORM_TABLE = ((re.compile('iTimeDelta'), 'uniform float iTimeDelta;\n'),
        (re.compile('iFrame'), 'uniform float iFrame;\n'),
        (re.compile('iChannelTime\[4\]'), 'uniform float iChannelTime[4];\n'),
        (re.compile('iMouse'), 'uniform vec4 iMouse;\n'),
        (re.compile('iDate'), 'uniform vec4 iDate;\n'),
        (re.compile('iSampleRate'), 'uniform float iSampleRate;\n'))

channel_regex = re.compile('iChannel\d')
function_define_regex = re.compile('#define.*\(.*') # has a ( in the line 
bool_define = re.compile('((?!.*[\(|\d]).*#define.*\n)') # does not have a ( or digit
digit_define = re.compile('((?!.*[\(]).*#define.*\d)') # has digit


class ShadertoyConverter:
    def convert(self, shader_code):
        self._code = shader_code
        if cid:
            self._convert_ifdefs()
        else:
            self._comment_ifdefs()
        self._sub_conversion_table()
        self._collect_and_add_uniforms()
        self._add_godot_first_line()
        self._convert_defines()
        return self._code
    
    def _sub_conversion_table(self):
        for shadertoy, godot in COMPILED_CONVERSION_TABLE:
            self._code = shadertoy.sub(godot, self._code) 

    def _collect_and_add_uniforms(self):
        self._code = f'{self._get_channel_uniforms()}{self._code}'
        self._code = f'{self._get_uniforms_from_table()}{self._code}'
    
    def _get_uniforms_from_table(self):
        return ''.join([gd for st, gd in UNIFORM_TABLE if re.search(st, self._code)])
    
    def _get_channel_uniforms(self):
        # channels = set([m.group(0) for m in re.finditer('iChannel\d', self._code)]) 
        channels = set([m.group(0) for m in channel_regex.finditer(self._code)]) 
        uniforms = [f'uniform sampler2D {channel};\n' for channel in channels]
        return ''.join(uniforms)
    
    def _add_godot_first_line(self):
        self._code = f'shader_type canvas_item;\n{self._code}'
    
    def _convert_defines(self):
        self._replace_bool_defines()
        self._replace_digit_defines()
        self._find_and_comment(function_define_regex)

    def _find_and_comment(self, regex):
        offset = 0
        for match in regex.finditer(self._code):
            g = match.group(0)
            print(f'Commenting out a function define: ', g)
            # print(self._code[match.start()+offset:match.end()+offset])
            self._code = f'{self._code[:match.start()+offset]}//{self._code[match.start()+offset:]}'
            offset += 2 # add offset because of our addition of //
  
    def _replace_digit_defines(self):
        offset = 0
        for m in digit_define.finditer(self._code):
            match = m.group(0)
            match_split = re.split(' ', match)
            val = match_split[-1]
            name = match_split[-2]
            if "." in val:
                replacement = f'const float {name} = {val};\n'
                print('Replacing a float define')
            else:
                replacement = f'const int {name} = {val};\n'
                print('Replacing an int define')
            self._code = f'{self._code[:m.start() + offset]}{replacement}{self._code[m.end() + offset:]}'
            r_len = len(replacement)
            m_len = len(match)
            offset += r_len - m_len
        
    def _replace_bool_defines(self):
        offset = 0
        for m in bool_define.finditer(self._code):
            print('Replacing a bool define')
            match = m.group(0)
            name = re.split(' ', match)[-1].replace('\n', '')
            replacement = f'const bool {name} = true;\n' # TODO: set to true if not already commented out!
            self._code = f'{self._code[:m.start() + offset]}{replacement}{self._code[m.end() + offset:]}'
            r_len = len(replacement)
            m_len = len(match)
            offset += r_len - m_len

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
   
    def _convert_ifdefs(self):
        # replace  #ifdef and #if  -->  "if ({name})\n{\n"
        # replace  #endif          -->  "}"
        # replace  #else           -->  "}\nelse\n{"
        _lines = ''
        for line in self._code.splitlines(True):
            if '#ifdef' in line:
                variable = line.split('#ifdef')[1].replace('\n', '') # second element should be the name
                _lines += f'if ({variable})\n{{\n'
            elif '#if' in line:
                variable = line.split('#if')[1].replace('\n', '') # second element should be the name
                _lines += f'if ({variable})\n{{\n'
            elif '#endif' in line:
                _lines += '}\n'
            elif '#else' in line:
                _lines += '}\nelse\n{\n'
            else:
                _lines += line
        self._code = _lines

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
            print('The shader will still need some manual fixes')
        else:
            print('No errors found during compilation')


def convert_shadertoy_shaders():
    def is_shader(filepath):
        return os.path.isfile(os.path.join(input_path, filepath)) \
                and (filepath.endswith('.shader') or filepath.endswith('.glsl'))
    
    def get_shaders(): return [f for f in os.listdir(input_path) if is_shader(f)]
    
    converter = ShadertoyConverter()
    
    for shader in get_shaders():
        shader_path = os.path.join(input_path, shader)
        print(f'Opening shader at: {shader_path}')
        with open(shader_path, 'r') as f:
            shader_code = f.read()
        
        # Run converter
        shader_code = converter.convert(shader_code)
        
        # Write the shader to a file
        shader = shader.replace('.glsl', '.shader')  # convert to .shader ending
        new_shader_path = os.path.join(output_path, shader)
        with open(new_shader_path, 'w+') as nf:
            nf.write(shader_code)
        if not gdcompile:
            print('skipping godot compilation - use --gdcompile flag to compile')
        else:
            try:
                GodotShaderCompiler.compile(new_shader_path)
            except:
                print('GodotShaderCompiler requires godot in PATH')
        
        print(f'Shader: {shader} - converted')
        print()

if __name__ == '__main__':
    convert_shadertoy_shaders()

