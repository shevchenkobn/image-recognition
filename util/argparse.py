from argparse import ArgumentTypeError as err
import os


class PathType(object):
    def __init__(self, exists=True, arg_type='file', dash_ok=True, permission=None):
        """exists:
                True: a path that does exist
                False: a path that does not exist, in a valid parent directory
                None: don't care
           type: file, dir, symlink, None, or a function returning True for valid paths
                None: don't care
           dash_ok: whether to allow "-" as stdin/stdout
           permission: bitmask of access. None if ignored"""

        assert exists in (True, False, None)
        assert arg_type in ('file', 'dir', 'symlink', None) or hasattr(arg_type, '__call__')
        assert permission is None or type(permission) is int

        self._exists = exists
        self._type = arg_type
        self._dash_ok = dash_ok
        self._permission = permission

    def __call__(self, string):
        if string == '-':
            # the special argument "-" means sys.std{in,out}
            if self._type == 'dir':
                raise err('standard input/output (-) not allowed as directory path')
            elif self._type == 'symlink':
                raise err('standard input/output (-) not allowed as symlink path')
            elif not self._dash_ok:
                raise err('standard input/output (-) not allowed')
        else:
            e = os.path.exists(string)
            if self._exists:
                if not e:
                    raise err("path does not exist: '%s'" % string)

                if self._type is None:
                    pass
                elif self._type == 'file':
                    if not os.path.isfile(string):
                        raise err("path is not a file: '%s'" % string)
                elif self._type == 'symlink':
                    if not os.path.symlink(string):
                        raise err("path is not a symlink: '%s'" % string)
                elif self._type == 'dir':
                    if not os.path.isdir(string):
                        raise err("path is not a directory: '%s'" % string)
                elif not self._type(string):
                    raise err("path not valid: '%s'" % string)

                if self._permission is None or not os.access(string, self._permission):
                    raise err("path doesn't have required permission: '%d'" % self._permission)
            else:
                if not self._exists and e:
                    raise err("path exists: '%s'" % string)

                p = os.path.dirname(os.path.normpath(string)) or '.'
                if not os.path.isdir(p):
                    raise err("parent path is not a directory: '%s'" % p)
                elif not os.path.exists(p):
                    raise err("parent directory does not exist: '%s'" % p)

        return string


class RangedFloatType(object):
    def __init__(self, float_range):
        assert len(float_range) >= 2 and float_range[0] <= float_range[1]

        self._range = float_range

    def __call__(self, arg):
        val = float(arg)
        if val < self._range[0] or val > self._range[1]:
            raise err("%r not in range [%r, %r]" % (val, *self._range))
        return val
