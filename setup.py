
from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

version = '2012.05.01'

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
      description='Convert audio files using ffmpeg',
)



