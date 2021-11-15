from jproperties import Properties

# do to properties
configs = Properties()
with open('dhealth-monitor.properties', 'rb') as read_prop:
    configs.load(read_prop)

prop_view = configs.items()
for item in prop_view:
    print(item[0], '=', item[1].data)