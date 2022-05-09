import json
import numpy as np
import base64


def numpy2dict(a):
    s = base64.b64encode(a).decode()
    r = dict(base64=s, shape=a.shape, dtype=str(a.dtype))

    return r


def dict2numpy(r):
    b = base64.decodebytes(r["base64"].encode())
    q = np.frombuffer(b, dtype=r["dtype"])

    return q.reshape(r["shape"])


def write_to_json(icons, fn):
    fdict = {}
    for fontsize, d in icons.items():
        for k, im in d.items():
            fdict.setdefault(fontsize, {})[k] = numpy2dict(np.array(im))

    import json

    s = json.dumps(fdict)
    open(fn, "w").write(s)


def load_from_json(fn):
    fdict2 = json.load(open(fn))

    ff = {}
    for fontsize, d in fdict2.items():
        for k, r in d.items():
            ff.setdefault(int(fontsize), {})[k] = dict2numpy(r)

    return ff


def load_from_json_string(s):
    fdict2 = json.loads(s)

    ff = {}
    for fontsize, d in fdict2.items():
        for k, r in d.items():
            ff.setdefault(int(fontsize), {})[k] = dict2numpy(r)

    return ff
