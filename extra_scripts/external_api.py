import xmlrpc.client
import time

url = "http://localhost:8069"
db = "redo2oo13"
username = 'admin'
password = 'admin'

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
id = models.execute_kw(db, uid, password, 'res.partner', 'create', [{
    'name': "New Partner" + str(time.time()),
}])


def read_image(path=''):
    """read image from fs and make it json serializable

    Keyword Arguments:
        path {str} -- fs path to image (default: {''})

    Returns:
        [type] -- image as encoded string
    """
    data = ''
    img_path = os.path.normpath('%s%s' % (BASE_PATH, path))
    if os.path.exists(img_path):
        with open(img_path, 'rb') as f:
            data = f.read()
    else:
        print('image not found:%s' % img_path)
    return base64.encodebytes(data).decode("utf-8")
