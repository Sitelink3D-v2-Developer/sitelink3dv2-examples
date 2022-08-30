import numpy as np
import functools
import base64
import uuid
from collections import OrderedDict
from struct import Struct
import logging
import math
import json

def lla_to_ecef(lat, lon, alt):
    a = 6378137.0                   # WGS-84 semi-major axis
    e2 = 6.6943799901377997e-3      # WGS-84 first eccentricity squared

    n = a / math.sqrt(1 - e2 * math.sin(lat) * math.sin(lat))

    x = (n + alt) * math.cos(lat) * math.cos(lon)
    y = (n + alt) * math.cos(lat) * math.sin(lon)
    z = (n * (1 - e2) + alt) * math.sin(lat)

    return np.array([x, y, z])

def scale_matrix(m, v):
    result = np.zeros((4,4))
    result[0] = m[0] * v[0]
    result[1] = m[1] * v[1]
    result[2] = m[2] * v[2]
    result[3] = m[3]

    return result

def rotate_matrix(m, angle, axis):
    c = np.cos(angle)
    s = np.sin(angle)

    temp = (1 - c) * axis

    rotate = np.zeros((4,4))
    rotate[0][0] = c + temp[0] * axis[0]
    rotate[0][1] = 0 + temp[0] * axis[1] + s * axis[2]
    rotate[0][2] = 0 + temp[0] * axis[2] - s * axis[1]

    rotate[1][0] = 0 + temp[1] * axis[0] - s * axis[2]
    rotate[1][1] = c + temp[1] * axis[1]
    rotate[1][2] = 0 + temp[1] * axis[2] + s * axis[0]

    rotate[2][0] = 0 + temp[2] * axis[0] + s * axis[1]
    rotate[2][1] = 0 + temp[2] * axis[1] - s * axis[0]
    rotate[2][2] = c + temp[2] * axis[2]

    result = np.zeros((4,4))
    result[0] = m[0] * rotate[0][0] + m[1] * rotate[0][1] + m[2] * rotate[0][2]
    result[1] = m[0] * rotate[1][0] + m[1] * rotate[1][1] + m[2] * rotate[1][2]
    result[2] = m[0] * rotate[2][0] + m[1] * rotate[2][1] + m[2] * rotate[2][2]
    result[3] = m[3]

    return result

class SpaceConverter(object):
    def __init__(self, source_forward_axis, source_forward_positive,
    source_up_axis, source_up_positive, source_right_handed,
    dest_forward_axis, dest_forward_positive,
    dest_up_axis, dest_up_positive, dest_right_handed):

        # setup source space vectors
        forward = np.zeros(3)
        forward[source_forward_axis] = 1 if source_forward_positive else -1

        up = np.zeros(3)
        up[source_up_axis] = 1 if source_up_positive else -1

        right = np.cross(forward, up)
        if not source_right_handed:
            right = -right

        # setup dest space vectors
        new_forward = np.zeros(3)
        new_forward[dest_forward_axis] = 1 if dest_forward_positive else -1

        new_up = np.zeros(3)
        new_up[dest_up_axis] = 1 if dest_up_positive else -1

        new_right = np.cross(new_forward, new_up)
        if not dest_right_handed:
            new_right = -new_right

        # build a conversion matrix
        space_convert = np.eye(4)

        current_axis = np.array([forward, right, up])
        new_axis = np.array([new_forward, new_right, new_up])

        for i in range(3):
            sign, direction = self.__find_axis(i, current_axis)
            space_convert[i] = np.append(new_axis[direction] * sign, 0)

        self.space_convert = space_convert

    def __find_axis(self, axis, vectors):
        sign = 0; direction = 0
        for i in range(3):
            if vectors[i][axis] > 0.00001:
                sign = 1; direction = i
                return sign, direction
            elif vectors[i][axis] < -0.00001:
                sign = -1; direction = i
                return sign, direction
        return sign,direction

    def get_matrix(self):
        return self.space_convert

class Interface(object):
    oem = "topcon"
    name = "interface"

    def __init__(self, interface_json):
        self._object_map = OrderedDict()
        self.oem = interface_json["oem"]
        self.name = interface_json["name"]
        self._json = interface_json

    def __setitem__(self, name, value):
        self._object_map[name] = value

    def __contains__(self, name):
        return name in self._object_map

    def __getitem__(self, name):
        return self._object_map[name]

    def iterobjects(self):
        return self._object_map.values()

    def cache(self, component):
        pass

class Replicate(Interface):
    def __init__(self, replicate_json):
        super(Replicate, self).__init__(replicate_json)
        self.manifest_items = list(map(self.ManifestItem, replicate_json["manifest"]))
        self.struct = Struct("<{0}".format("".join(list(m.code for m in self.manifest_items))))

    def decode_manifest(self, manifest):
        manifest_binary = base64.b64decode(manifest)
        items = self.struct.unpack(manifest_binary)
        logging.debug("Replicate interface object has decoded the binary manifest to produce the following items: {0}".format(items))
        return dict(zip(list(m.ref for m in self.manifest_items), items))

    def load_manifests(resource_configuration, manifests):
        if len(manifests) != len(resource_configuration.components):
            raise Exception("number of components mismatch")
        for i, component in enumerate(resource_configuration.components):
            replicate_interface = component.interfaces["replicate"]
            values = replicate_interface.decode_manifest(manifests[i])
            for key,value in values.items():
                node_name, prop = key.rsplit(".", 1)
                logging.debug("Updating node name {} and property {} to value {}".format(node_name, prop, value))
                node = component.get_interface_object(node_name)
                node[prop] = value
        resource_configuration.update_transforms()

    class ManifestItem(object):
        FORMATS = {
            "int8": (int, "b"),
            "int16": (int, "h"),
            "int32": (int, "i"),
            "float": (float, "f"),
            "double": (float, "d"),
        }
        def __init__(self, manifest_json):
            self.ref = manifest_json["value_ref"]
            if "discrete" in manifest_json:
                d = manifest_json["discrete"]
                self.discrete = (d["min"], d["max"], d["discrete_min"], d["discrete_max"])
            self.type_ = None
            self.code = None
            self.set_binary_format(manifest_json["type"])

        def set_binary_format(self, value_type):
            self.type_, self.code = self.FORMATS[value_type]

class PointsOfInterest(Interface):
    def __init__(self, poi_json):
        super(PointsOfInterest, self).__init__(poi_json)
        self.points = list(map(functools.partial(self.Point, interface=self), poi_json["points"]))

    def cache(self, component):
        for point in self.points:
            point.node = component.get_interface_object(point.node_ref)

    class Point(object):
        def __init__(self, pt_json, interface):
            self.tx = pt_json.get("tx", 0)
            self.ty = pt_json.get("ty", 0)
            self.tz = pt_json.get("tz", 0)
            self.id = pt_json["id"]
            self.node = None
            self.node_ref = pt_json["node_ref"]
            self.description = pt_json["description"]
            self.interface = interface
            interface[self.id] = self

        def get_point(self):
            return np.array([(self.tx, self.ty, self.tz, 1.)])

        def get_id(self):
            return self.id

        def __repr__(self):
            return str((self.id, self.tx, self.ty, self.tz, "+" + self.node_ref))

class Attach(Interface):
    def __init__(self, attach_json):
        super(Attach, self).__init__(attach_json)
        self.parent_component = None
        self._parent_component_index = attach_json["parent_component_index"]
        self.parent_node = None
        self._parent_node_ref = attach_json["parent_node_ref"]
        self.local_node = None
        self._local_node_ref = attach_json["local_node_ref"]

    def cache(self, component):
        self.local_node = component.get_interface_object(self._local_node_ref)

    def attach(self, resource_configuration):
        component_list = list(resource_configuration.components)
        self.parent_component = component_list[self._parent_component_index]
        self.parent_node = self.parent_component.get_interface_object(self._parent_node_ref)
class Nodes(Interface):
    def __init__(self, nodes_json):
        super(Nodes, self).__init__(nodes_json)
        nodes = nodes_json["nodes"]
        self.nodes = list(map(functools.partial(Nodes.Node, parent=None, interface=self), nodes))

    class Node(object):
        def __init__(self, node_json, parent, interface):
            self.parent = parent
            self._dirty = True
            self._transform = None

            self.rx = node_json.get("rx", 0)
            self.ry = node_json.get("ry", 0)
            self.rz = node_json.get("rz", 0)
            self.tx = node_json.get("tx", 0)
            self.ty = node_json.get("ty", 0)
            self.tz = node_json.get("tz", 0)
            self.sx = node_json.get("sx", 1)
            self.sy = node_json.get("sy", 1)
            self.sz = node_json.get("sz", 1)
            self.id = node_json["id"]

            self.transform = None
            interface[self.id] = self

            nodes = node_json["nodes"]
            self.nodes = list(map(functools.partial(Nodes.Node, parent=self, interface=interface), nodes))

        def __setitem__(self, key, value):
            if len(key) != 2 or key[0] not in "rt" or key[1] not in "xyz":
                raise KeyError("{0} not in Node".format(key))
            setattr(self, key, value)
            self._dirty = True

        def get_id(self):
            return self.id

        def get_local_transform(self):
            if not self._dirty:
                return self._transform

            # translate
            M = np.eye(4)
            M[3, 0] = self.tx
            M[3, 1] = self.ty
            M[3, 2] = self.tz

            if self.rz:
                M = rotate_matrix(M, self.rz, np.array([0,0,1])) # yaw
            if self.ry:
                M = rotate_matrix(M, self.ry, np.array([0,1,0])) # pitch
            if self.rx:
                M = rotate_matrix(M, self.rx, np.array([1,0,0])) # roll

            scale = np.array([self.sx, self.sy, self.sz])
            M = scale_matrix(M, scale)

            self._transform = M
            self._dirty = False
            return M

    def update_transforms(self, root_transform):
        for node in self.iterobjects():
            parent_transform = root_transform
            if node.parent:
                parent_transform = parent_transform * node.parent.get_local_transform()

            node.transform = parent_transform * node.get_local_transform()
class Transform(Interface):
    def __init__(self, xf_json):
        super(Transform, self).__init__(xf_json)
        self.local_rotation = Transform.LocalRotation(xf_json.get("local_rotation", {}))
        self.local_position = Transform.LocalPosition(xf_json.get("local_position", {}))
        self.wgs = Transform.WGS(xf_json.get("wgs", {}))
        self.type = xf_json.get("type", "local")
        self["local_rotation"] = self.local_rotation
        self["local_position"] = self.local_position
        self["wgs"] = self.wgs
    class LocalRotation(object):
        yaw = 0.
        pitch = 0.
        roll = 0.
        def __init__(self, lr_json):
            for k in ("yaw", "pitch", "roll"):
                setattr(self, k, lr_json.get(k, 0.))
        def __setitem__(self, key, item):
            if key in self.__dict__:
                setattr(self, key, item)
        def __getitem__(self, key):
            if key in self.__dict__:
                return getattr(self, key)

    class LocalPosition(object):
        northing = 0.
        easting = 0.
        elevation = 0.
        def __init__(self, lr_json):
            for k in ("northing", "easting", "elevation"):
                setattr(self, k, lr_json.get(k, 0.))
        def __setitem__(self, key, item):
            if key in self.__dict__:
                setattr(self, key, item)
        def __getitem__(self, key):
            if key in self.__dict__:
                return getattr(self, key)
    class WGS(object):
        lat = 0.
        lon = 0.
        alt = 0.
        dir = 0.
        def __init__(self, lr_json):
            for k in ("lat", "lon", "alt", "dir"):
                setattr(self, k, lr_json.get(k, 0.))
        def __setitem__(self, key, item):
            if key in self.__dict__:
                setattr(self, key, item)
        def __getitem__(self, key):
            if key in self.__dict__:
                return getattr(self, key)

    class J670ToLocal(object):
        def __init__(self, northing_axis = 1, northing_positive = True,
            easting_axis = 0, easting_positive = True,
            elevation_axis = 2, elevation_positive = True,
            right_handed = True):

            self.northing_axis = northing_axis
            self.northing_positive = northing_positive
            self.easting_axis = easting_axis
            self.easting_positive = easting_positive
            self.elevation_axis = elevation_axis
            self.elevation_positive = elevation_positive

            # northing is forward, as at yaw=0 resource is facing due north.
            self.j670_to_localized_space = SpaceConverter(0, True, 2, False, True, northing_axis, northing_positive, elevation_axis, elevation_positive, right_handed)

        def get_j670_to_local_transform(self):
            return self.j670_to_localized_space.get_matrix()

    def get_transform(self, a_local: J670ToLocal):
        if self.type != "local":
            raise Exception('expecting type T_LOCAL')
        resource_position = np.zeros(3)
        # northing
        resource_position[a_local.northing_axis] = self["local_position"]["northing"] if a_local.northing_positive else -self["local_position"]["northing"]
        # easting
        resource_position[a_local.easting_axis] = self["local_position"]["easting"] if a_local.easting_positive else -self["local_position"]["easting"]
        # elevation
        resource_position[a_local.elevation_axis] = self["local_position"]["elevation"] if a_local.elevation_positive else -self["local_position"]["elevation"]

        forward = np.zeros(3)
        forward[a_local.northing_axis] = 1 if a_local.northing_positive else -1

        right = np.zeros(3)
        right[a_local.easting_axis] = 1 if a_local.easting_positive else -1

        up = np.zeros(3)
        up[a_local.elevation_axis] = 1 if a_local.elevation_positive else -1

        # translate
        resource = np.eye(4)
        resource[3, 0] = self["local_position"]["easting"]
        resource[3, 1] = self["local_position"]["northing"]
        resource[3, 2] = self["local_position"]["elevation"]

        resource = rotate_matrix(resource, -self["local_rotation"]["yaw"], up)
        resource = rotate_matrix(resource, self["local_rotation"]["pitch"], right)
        resource = rotate_matrix(resource, self["local_rotation"]["roll"], forward)

        return a_local.get_j670_to_local_transform() @ resource

    def get_resource_to_local_transform(self, a_local: J670ToLocal, a_ecef_to_local):
        if self.type == "local":
            return self.get_transform(a_local)
        elif self.type != "wgs":
            raise Exception('expecting type T_WGS')

        lat = math.radians(self["wgs"]["lat"])
        lon = math.radians(self["wgs"]["lon"])
        alt = math.radians(self["wgs"]["alt"])

        ecef = lla_to_ecef(lat,lon,alt)
        local = np.append(ecef, 1) @ a_ecef_to_local

        # translate
        resource = np.eye(4)
        resource[3, 0] = local[0]
        resource[3, 1] = local[1]
        resource[3, 2] = local[2]

        # TODO: add matrix rotation for wgs
        return a_local.get_j670_to_local_transform() @ resource

class Unknown(Interface):
    def __init__(self, unknown_json):
        super(Unknown, self).__init__(unknown_json)
        self._load_json_recursive(self._json)

    def _load_json_recursive(self, json):
        for key, value in json.items():
            if type(value) is list:
                for object in value:
                    if type(object) is dict:
                        self._load_json_recursive(object)
            if key == "id":
                self[value] = Unknown.Object(json)
    class Object(object):
        def __init__(self, json):
            for k, v in json.items():
                setattr(self, k, v)
        def __setitem__(self, key, item):
            if key in self.__dict__:
                setattr(self, key, item)
        def __getitem__(self, key):
            if key in self.__dict__:
                return getattr(self, key)

class Component(object):
    interface_factory = {
        "replicate": Replicate,
        "points_of_interest": PointsOfInterest,
        "nodes": Nodes,
        "transform": Transform,
        "attach": Attach
    }

    def __init__(self, component_json):
        self.uuid = uuid.UUID(component_json["uuid"])
        self.description = component_json["description"]
        interfaces = {}
        for interface in component_json["interfaces"]:
            name = interface["name"]
            if name in self.interface_factory:
                klass = self.interface_factory[name]
                interfaces[name] = klass(interface)
            else:
                interfaces[name] = Unknown(interface)
        self.interfaces = interfaces

    def cache(self):
        for name, interface in self.interfaces.items():
            interface.cache(self)

    def get_interface_object(self, key):
        oem, name, node_name = key.split(".")
        interface = self.interfaces.get(name, None)
        return interface and interface[node_name]

class ResourceConfiguration(object):
    def __init__(self, rc_json):
        self._json = rc_json
        self.components = list(map(Component, rc_json["components"]))
        self.cache()
        self.update_transforms()

    def cache(self):
        attachments = {}
        for component in self.components:
            component.cache()
            parent = None
            if "attach" in component.interfaces:
                attach = component.interfaces["attach"]
                attach.attach(self)
                parent = attach.parent_component
            if "transform" in component.interfaces:
                self.transform = component.interfaces["transform"]

            attached = attachments.get(parent, [])
            attached.append(component)
            attachments[parent] = attached

        order = []
        keys = [None]
        while keys:
            key = keys.pop()
            attached = attachments.get(key, [])
            order.extend(attached)
            keys.extend(attached)

        self.ordering = order

    def update_transforms(self):
        for component in self.ordering:
            if "nodes" in component.interfaces:
                if "attach" in component.interfaces:
                    attach_transform = component.interfaces["attach"].parent_node.transform
                else:
                    attach_transform = np.eye(4)

                nodes = component.interfaces["nodes"]
                nodes.update_transforms(attach_transform)