import pysaver

dev_id = pysaver.load("device_id", "ApolloXXXX")

tags = pysaver.load("tags", [dev_id, ])

def add_tag(tag):
    global tags
    if tag not in tags:
        tags.append(tag)
        pysaver.save("tags", tags)
        print("Tag " + str(tag) + " added")
    else:
        print("Tag already exists")

def remove_tag(tag):
    global tags
    if tag in tags:
        tags.remove(tag)
        pysaver.save("tags", tags)
        print("Tag " + str(tag) + " removed")
    else:
        print("Tag not found")

def has_tag(tag):
    global tags
    if tag in tags:
        return True
    else:
        return False

def get_all_tags():
    global tags
    return tags