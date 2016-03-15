bbc-openstack-plugins
---------------------
Much of OpenStack provides plugin capabilites via [stevedore](https://github.com/openstack/stevedore/) plugin loading. There are various times where we would like to extend or fix existing OpenStack python modules.  In these cases, stevedore allows us to modify the runtime without forking the upstream OpenStack project. This is a collection of those changes and enhancements that are waiting to move upstream.

how?
----
stevedore works by declaring the appropriate plugin entry points (see: [setup.cfg](setup.cfg)). Find the appropriate entry points used by the upstream project and then namespace your own in this repository. By convention, we prefix these plugins with 'bbc'.
