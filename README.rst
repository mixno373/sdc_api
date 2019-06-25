sdc-api.py
==========

Quick Example
--------------

	pip install sdc-api


Quick Example
--------------

.. code:: py

	from sdc_api import SDC
	
	sdc = SDC('dKey')
	
	# Get guild, where you generated dKey
	guild = await sdc.get_guild()
	print(guild)
	
	# Get guild's place
	place = await guild.place()
	print("Place of server in SDC is %d" % place)
    
Get Guild

.. code:: py

	guild = await sdc.get_guild('id')
