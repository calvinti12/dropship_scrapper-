import re
from numbers import Number
import xml.etree.cElementTree as ET

# Python 2 and 3 compatibility
from past.builtins import basestring
from future.utils import iteritems
from builtins import str as utext

# Automatically convert string to integers, when possible
autoint = True

# Allow access to tag attributes with '.xxx' (in addition to '["xxx"]')
get_attr_as_member = True

class XMLStruct(object):

    def __init__(self, arg, **kwargs):
        if isinstance(arg, basestring):
            if '<' in arg:
                # XML text
                self.elem = ET.fromstring(arg)
            elif arg.lower().endswith('.xml'):
                # XML file name
                self.elem = ET.parse(arg).getroot()
            else:
                # Top element
                attr = ''.join([' %s="%s"'%(k, v) for k,v in sorted(iteritems(kwargs))])
                self.elem = ET.fromstring("<%s%s></%s>"%(arg, attr, arg))
        else:
            self.elem = arg
        self._by_key_ = {}
        self._objcache_ = {}
        self._has_children_ = len(self.elem) > 0
    
    def _elem2struct(self, elem):
        if id(elem) in self._objcache_:
            return self._objcache_[id(elem)]
        result = XMLStruct(elem)
        self._objcache_[id(elem)] = result
        return result

    def __getattr__(self, attr):
        elem = self.elem.find(attr)
        if elem is not None:
            result = self._elem2struct(elem)
        elif  attr in ('text', 'tag'):
            result = getattr(self.elem, attr)
        elif get_attr_as_member and attr in self.elem.attrib:
            result = self[attr]
        else:
            result = None
        if result is None and not self._has_children_:
            # for simple values, try treating attr as a value function
            result = getattr(self._value(), attr, None)
        return result

    def __setattr__(self, attr, value):
        if isinstance(value, basestring) or isinstance(value, int):
            elem  = self.elem.find(attr)
            if elem is not None:
                # If there exists child element with a name of a given attribute,
                # set it to a given value
                child = self._elem2struct(elem)
                child.elem.text = utext(value)
                return
        self.__dict__[attr] = value

    def __getitem__(self, item):
        if isinstance(item, int):
            # List-like access
            elem = self.elem[item]
            result = self._elem2struct(elem)
            return result
        # Get XML attribute ("blah" from <tag item="blah">)
        s = self.elem.get(item)
        return try_str2int(s)

    def __setitem__(self, item, value):
        self.elem.attrib[item] = value

    def get(self, item, default=None):
        result = self.elem.attrib.get(item, default)
        return result

    def __len__(self):
        if self._has_children_:
            return len(self.elem)
        else:
            return len(str(self))

    def __repr__(self):
        if self._has_children_:
            s_attr = ''.join(", %s='%s'"%(k, v) for k,v in self.elem.items())
            return "XMLStruct('%s'%s)"%(self.elem.tag, s_attr)
        else:
            return repr(self._value())

    def __str__(self):
        if self._has_children_:
            return self.__repr__()
        elif self.elem.text is None:
            return ''
        else:
            return self.elem.text

    def __call__(self, match, **kwargs):
        """
        Find first element by tag name or path, filtering by given attributes
        If there is no matching element, return None
        """
        try:
            return next(self.iterfind(match, **kwargs))
        except StopIteration:
            return None

    def iterfind(self, match, **kwargs):
        for e in self.elem.iterfind(match):
            mismatch = any([e.get(k) != v for k, v in iteritems(kwargs)])
            if not mismatch:
                yield self._elem2struct(e)

    def __eq__(self, other):
        diff = self.is_different(other)
        return not diff

    def __ne__(self, other):
        diff = self.is_different(other)
        return diff

    if hasattr(0, '__cmp__'): # python 2
        def __cmp__(self, other): return -other.__cmp__(self._value())
    else: # python 3
        def __gt__(self, other): return -other.__gt__(self._value())
        def __ge__(self, other): return -other.__ge__(self._value())
    def __add__(self, other): return self._value() + other
    def __radd__(self, other): return other + self._value()
    def __sub__(self, other): return other.__rsub__(self._value())
    def __rsub__(self, other): return other.__sub__(self._value())
    def __mul__(self, other): return other.__rmul__(self._value())
    def __rmul__(self, other): return other.__mul__(self._value())
    def __div__(self, other): return other.__rdiv__(self._value())
    def __truediv__(self, other): return other.__rtruediv__(self._value())
    def __rdiv__(self, other): return other.__div__(self._value())
    def __rtruediv__(self, other): return other.__truediv__(self._value())
    def __floordiv__(self, other): return other.__rfloordiv__(self._value())
    def __rfloordiv__(self, other): return other.__floordiv__(self._value())
    def __mod__(self, other): return other.__rmod__(self._value())
    def __rmod__(self, other): return other.__mod__(self._value())
    def __divmod__(self, other): return other.__rdivmod__(self._value())
    def __rdivmod__(self, other): return other.__divmod__(self._value())
    def __lshift__(self, other): return other.__rlshift__(self._value())
    def __rlshift__(self, other): return other.__lshift__(self._value())
    def __rshift__(self, other): return other.__rrshift__(self._value())
    def __rrshift__(self, other): return other.__rshift__(self._value())
    def __pow__(self, other): return other.__rpow__(self._value())
    def __rpow__(self, other): return other.__pow__(self._value())

    def __nonzero__(self): # python 2
        if self._has_children_:
            return True
        else:
            return bool(self._value())

    def __bool__(self): # python 3
        return self.__nonzero__()

    def __hash__(self):
        if self._has_children_:
            return hash(self.dumps)
        else:
            return hash(self._value())

    def __contains__(self, value):
        if self._has_children_:
            return value in self.elem # bogus
        else:
            return value in self._value()

    #def append(self, _tag, *args, **kwargs):
    #    # args[0] - element text (optional)
    #    # kwargs - element attributes
    #    attr = ''.join([' %s="%s"'%(k, v) for k,v in sorted(iteritems(kwargs))])
    #    if len(args) > 0:
    #        text = args[0]
    #    else:
    #        text = ''
    #    s = '<%s%s>%s</%s>'%(_tag, attr, text, _tag)
    #    e = ET.fromstring(s)
    #    self.elem.append(e)

    def is_different(self, other, recheck=None):
        if other is None:
            if not recheck or recheck(self, other):
                return True
        if isinstance(other, basestring) or isinstance(other, Number):
            _value = self._value()
            if _value != other:
                if not recheck or recheck(_value, other):
                    return True
            return False
        if self.elem.tag != other.elem.tag or \
           self.elem.attrib != other.elem.attrib or \
           self._value() != other._value() or \
           len(self) != len(other):
            if not recheck or recheck(self, other):
                return True
        a1 = list(self)
        a2 = list(other)
        for i, e1 in enumerate(a1):
            e2 = a2[i]
            if e1 == e2: continue
            if not hasattr(e1, 'is_different') or e1.is_different(e2):
                return True
        return False

    def as_dict(self, key):
        if key in self._by_key_:
            return self._by_key_[key]
        ans = {}
        for e in self:
            if key in e.elem.attrib:
                keyval = e[key]
            elif hasattr(e, key):
                keyval = getattr(e, key)
            else:
                raise KeyError("Attribute or tag '%s' not found in %s"%(key, e))
            skeyval = try_str2int(str(keyval))
            ans[skeyval] = e
        self._by_key_[key] = ans
        return ans

    def dumps(self, indent=2, level=0):
        pre = ' ' * indent * level
        attr = ''.join([' %s="%s"'%(k, v) for k,v in sorted(self.elem.items())])
        if not self._has_children_:
            text = str(self)
            if '\n' in text:
                # Reformat multi-line text
                # TODO: can potentially reformat better, remove/add extra space when level changes
                text = re.sub(r'[ \t]+$', pre, text)
            return pre + '<%s%s>%s</%s>\n'%(self.tag, attr, text, self.tag)
        if level == 0:
            ans = u'<?xml version="1.0" encoding="UTF-8"?>\n'
        else:
            ans = u''
        ans += pre + '<%s%s>\n'%(self.tag, attr)
        for e in self:
            ans += e.dumps(indent=indent, level=level+1)
        ans += pre + '</%s>\n'%self.tag
        return ans

    def _value(self):
        return try_str2int(str(self))

def try_str2int(s):
    if not autoint or s is None: return s
    try:
        if s.lower().startswith('0x'):
            return int(s[2:], 16)
        else:
            return int(s)
    except ValueError:
        pass
    return s

def get_func(func):
    def foo(obj, *args): # FIXME: why doesn't it work for multi-arg?
        return getattr(obj._value(), func)(*args)
    return foo

for func in [
    '__float__',
    '__int__',
    '__long__',
    '__index__',
    '__hex__',
    '__oct__',
    '__neg__',
    '__abs__',
    '__invert__',
    ]:
    setattr(XMLStruct, func, get_func(func))
