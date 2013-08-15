
from setuptools import setup, find_packages

version = '1.0.0'

entry_points = {'console_scripts': ['audio_convert = audio_convert.ffmpeg_audio:main_convert',
                                   ]}

# Do it.
setup(name='audio_convert',
      packages=find_packages(),
      package_data={'': ['*.txt',
                         ]},

      entry_points=entry_points,

      # Metadata
      version=version,
      author='Pierre V. Villeneuve',
      author_email='pierre.villeneuve@gmail.com',
      url='https://github.com/Who8MyLunch/Audio_Convert',
      description='Convert audio files using ffmpeg',
)



