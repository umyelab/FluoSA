'''
Copyright (C)
This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with this program. If not, see https://tldrlegal.com/license/gnu-general-public-license-v3-(gpl-3)#fulltext. 

For license issues, please contact:

Dr. Bing Ye
Life Sciences Institute
University of Michigan
210 Washtenaw Avenue, Room 5403
Ann Arbor, MI 48109-2216
USA

Email: bingye@umich.edu
'''




import requests
from packaging import version
from FluoSA import __version__,gui


def main():

	try:

		current_version=version.parse(__version__)
		pypi_json=requests.get('https://pypi.org/pypi/FluoSA/json').json()
		latest_version=version.parse(pypi_json['info']['version'])

		if latest_version>current_version:
			print('A newer version '+'('+str(latest_version)+')'+' of FluoSA is available.')
			print('You may upgrade it by "python3 -m pip install --upgrade FluoSA".')
			print('For the details of new changes, check: "https://github.com/yujiahu415/FluoSA".')

	except:
		
		pass

	gui.main_window()


if __name__=='__main__':

	main()

