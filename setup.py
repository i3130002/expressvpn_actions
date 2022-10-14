from setuptools import setup
 
setup(
  name='expressvpn_actions',
  version='0.3',
  description='A better way to use ExpressVPN',
  author='i3130002',
  author_email='i3130002@gmail.com',
  url='https://github.com/cog1to/expressvpn_actions',
  include_package_data=True,
  license='WTFPL',
  entry_points={
        'gui_scripts': [
            'expressvpn_actions_gui = expressvpn_actions:run',
        ]
    }
)
