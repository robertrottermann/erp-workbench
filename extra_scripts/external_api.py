# https://www.youtube.com/watch?v=isjhwKAL63M
import xmlrpc.client
import time
import os
import base64

url = "http://localhost:8069"
db = "singh_commerce_14"
username = 'sudego'
password = 'sudego'


def read_image(path=''):
    """read image from fs and make it json serializable

    Keyword Arguments:
        path {str} -- fs path to image (default: {''})

    Returns:
        [type] -- image as encoded string
    """
    data = ''
    #img_path = os.path.normpath('%s%s' % (BASE_PATH, path))
    img_path = path
    if os.path.exists(img_path):
        with open(img_path, 'rb') as f:
            data = f.read()
    else:
        print('image not found:%s' % img_path)
    return base64.encodebytes(data).decode("utf-8")



common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
print(common.version())

uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
partners = models.execute_kw(db, uid, password,
    'res.partner', 'search', [[]],)

print(len(partners))

partners = models.execute_kw(db, uid, password,
    'res.partner', 'search', [[]], {'offset': 10, 'limit': 5})

print(len(partners))


models.execute_kw(db, uid, password,
    'res.partner', 'check_access_rights',
    ['read'], {'raise_exception': False})

# using search count
partners_count = models.execute_kw(db, uid, password,
    'res.partner', 'search_count', [[]],)
print(partners_count)

# create record
new_id = models.execute_kw(db, uid, password, 'res.partner', 'create', [{
    'name': "New Partner" + str(time.time()),
}])

# read the fields of the new partner
new_partner = models.execute_kw(db, uid, password, 'res.partner', 'read', [new_id])
# print(new_partner)

# add an image to the new partner, change its name
new_data = {
    'image_1920' : read_image('AK.jpeg'),
    'name' : 'John, %s' % new_partner[0]['name'],
}
models.execute_kw(db, uid, password, 'res.partner', 'write', [[new_id], new_data])
print(models.execute_kw(db, uid, password, 'res.partner', 'read', [new_id])[0]['name'])

