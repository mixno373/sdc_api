sdc_api.py
==========

Installation
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

Usage
--------------

Get Guild

.. code:: py

	guild = await sdc.get_guild('id')

Get Guild Votes

.. code:: py

	guild = Guild(id='id')
	votes = await guild.get_votes()

.. code:: py

	votes = await sdc.get_guild_votes('id')

Get Guild Place

.. code:: py

	place = await sdc.get_guild_place('id')
	print("Place of server in SDC is %d" % place)

.. code:: py

	guild = await sdc.get_guild('id')
	place = await guild.place()
	print("Place of server in SDC is %d" % place)

Get User's Votes

.. code:: py

	user = User(id='id')
	votes = await user.get_votes()

.. code:: py

	votes = await sdc.get_user_votes('id')
