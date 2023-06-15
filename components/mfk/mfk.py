import functools
import base64
import uuid
from collections import OrderedDict
import struct
import math
import glm
from enum import Enum

def lla_to_ecef(lat, lon, alt):
    # WGS-84 ellipsoid parameters
    a = 6378137.0                   # semi-major axis
    e2 = 6.6943799901377997e-3      # first eccentricity squared

    # Calculate the radius of curvature in the prime vertical
    n = a / math.sqrt(1 - e2 * math.sin(lat) * math.sin(lat))

    # Convert geodetic coordinates to ECEF coordinates
    x = (n + alt) * math.cos(lat) * math.cos(lon)
    y = (n + alt) * math.cos(lat) * math.sin(lon)
    z = (n * (1 - e2) + alt) * math.sin(lat)

    return glm.vec3(x, y, z)

class SpaceConverter(object):
    def __init__(self, source_forward_axis, source_forward_positive,
    source_up_axis, source_up_positive, source_right_handed,
    dest_forward_axis, dest_forward_positive,
    dest_up_axis, dest_up_positive, dest_right_handed):

        # setup source space vectors
        forward = glm.vec3()
        forward[source_forward_axis] = 1 if source_forward_positive else -1

        up = glm.vec3()
        up[source_up_axis] = 1 if source_up_positive else -1

        right = glm.cross(forward, up)
        if not source_right_handed:
            right = -right

        # setup dest space vectors
        new_forward = glm.vec3()
        new_forward[dest_forward_axis] = 1 if dest_forward_positive else -1

        new_up = glm.vec3()
        new_up[dest_up_axis] = 1 if dest_up_positive else -1

        new_right = glm.cross(new_forward, new_up)
        if not dest_right_handed:
            new_right = -new_right

        # build a conversion matrix
        space_convert = glm.identity(glm.mat4)
        current_axis = [forward, right, up]
        new_axis = [new_forward, new_right, new_up]

        for i in range(3):
            sign, direction = self.__find_axis(i, current_axis)
            space_convert[i] = glm.vec4(new_axis[direction] * sign, 0)

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

def setvalueref(interface_object, key, value):
    is_number = lambda x : isinstance(x, int) or isinstance(x, float)
    is_list = lambda x : isinstance(x, list)

    if key in interface_object.__dict__:
        current_value = interface_object.__dict__[key]
        if is_number(current_value) and not is_number(value):
            raise TypeError("set value is not a number type (int|float)")
        elif is_list(current_value):
            if not is_list(value):
                raise TypeError("set value is not a list type")
            elif len(value) != len(current_value):
                raise AssertionError("set value size does not match")
            elif not all([is_number(item) for item in value]):
                raise TypeError("set value contains types other than number (int|float)")
        setattr(interface_object, key, value)

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
        self.manifest = list(map(self.Value, replicate_json["manifest"]))

    def write_manifest(self):
        binary = b''
        for replicate_value in self.manifest:
            binary += replicate_value.write()
        return binary

    def read_manifest(self, binary_manifest):
        offset = 0
        for replicate_value in self.manifest:
            offset += replicate_value.read(binary_manifest, offset)
        remaining_bytes = len(binary_manifest) - offset
        return remaining_bytes

    def cache(self, component):
        for replicate_value in self.manifest:
            key, value_id = replicate_value.ref.rsplit(".", 1)
            replicate_value.object = component.get_interface_object(key)
            replicate_value.value_id = value_id

    def save_manifests(resource_configuration):
        manifests = []
        for component in resource_configuration.components:
            replicate_interface = component.interfaces["replicate"]
            binary = replicate_interface.write_manifest()
            b64_manifest = base64.b64encode(binary)
            manifests.append(b64_manifest)
        return manifests

    def load_manifests(resource_configuration, manifests):
        if len(manifests) != len(resource_configuration.components):
            raise Exception("number of components mismatch")
        for i, component in enumerate(resource_configuration.components):
            replicate_interface = component.interfaces["replicate"]
            binary_manifest = base64.b64decode(manifests[i])
            remaining_bytes = replicate_interface.read_manifest(binary_manifest)
            if remaining_bytes > 0:
                raise AssertionError("too much manifest data")

    class Value(object):
        def __init__(self, manifest_json):
            self.object = None
            self.value_id = None
            self.ref = manifest_json["value_ref"]
            self.type = manifest_json["type"]
            if "discrete" in manifest_json:
                d = manifest_json["discrete"]
                self.discrete = (d["min"], d["max"], d["discrete_min"], d["discrete_max"])

        def write(self):
            if self.object == None or self.object[self.value_id] == None:
                raise AttributeError("cannot write manifest with null object reference")

            value = self.object[self.value_id]

            if self.type == "int8":
                data = struct.pack("<b", value)
            elif self.type == "int16":
                data = struct.pack("<h", value)
            elif self.type == "int32":
                data = struct.pack("<i", value)
            elif self.type == "float":
                data = struct.pack("<f", value)
            elif self.type == "double":
                data = struct.pack("<d", value)
            elif self.type == "int8[]":
                data = struct.pack("<{}b".format(len(value)), *value)
            elif self.type == "int16[]":
                data = struct.pack("<{}h".format(len(value)), *value)
            elif self.type == "int32[]":
                data = struct.pack("<{}i".format(len(value)), *value)
            elif self.type == "float[]":
                data = struct.pack("<{}f".format(len(value)), *value)
            elif self.type == "double[]":
                data = struct.pack("<{}d".format(len(value)), *value)
            else:
                raise KeyError("unknown type")

            return data

        def read(self, binary_manifest, offset):
            if self.object == None or self.object[self.value_id] == None:
                raise AttributeError("cannot read manifest with null object reference")

            fmt = "<"

            if self.type == "int8":
                fmt += "b"
                value = struct.unpack_from(fmt, binary_manifest, offset)[0]
            elif self.type == "int16":
                fmt += "h"
                value = struct.unpack_from(fmt, binary_manifest, offset)[0]
            elif self.type == "int32":
                fmt += "i"
                value = struct.unpack_from(fmt, binary_manifest, offset)[0]
            elif self.type == "float":
                fmt += "f"
                value = struct.unpack_from(fmt, binary_manifest, offset)[0]
            elif self.type == "double":
                fmt += "d"
                value = struct.unpack_from(fmt, binary_manifest, offset)[0]
            elif self.type == "int8[]":
                fmt += str(len(self.object[self.value_id])) + "b"
                value = list(struct.unpack_from(fmt, binary_manifest, offset))
            elif self.type == "int16[]":
                fmt += str(len(self.object[self.value_id])) + "h"
                value = list(struct.unpack_from(fmt, binary_manifest, offset))
            elif self.type == "int32[]":
                fmt += str(len(self.object[self.value_id])) + "i"
                value = list(struct.unpack_from(fmt, binary_manifest, offset))
            elif self.type == "float[]":
                fmt += str(len(self.object[self.value_id])) + "f"
                value = list(struct.unpack_from(fmt, binary_manifest, offset))
            elif self.type == "double[]":
                fmt += str(len(self.object[self.value_id])) + "d"
                value = list(struct.unpack_from(fmt, binary_manifest, offset))
            else:
                raise KeyError("unknown type")

            self.object[self.value_id] = value

            return struct.calcsize(fmt)

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

        def __setitem__(self, key, value):
            setvalueref(self, key, value)

        def get_point(self):
            return glm.vec3(self.tx, self.ty, self.tz)

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
            self.dirty = True
            self.local = None
            self.transform = None

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

            interface[self.id] = self

            nodes = node_json["nodes"]
            self.nodes = list(map(functools.partial(Nodes.Node, parent=self, interface=interface), nodes))

        def __setitem__(self, key, value):
            if len(key) != 2 or key[0] not in "rt" or key[1] not in "xyz":
                raise KeyError("{0} not in Node".format(key))
            setvalueref(self, key, value)
            self.dirty = True

        def __getitem__(self, key):
            if key in self.__dict__:
                return getattr(self, key)

        def get_id(self):
            return self.id

        def get_transform(self):
            return self.transform

        def get_local_transform(self):
            if not self.dirty:
                return self.local

            # Update the local transform
            # Note: We apply roll then pitch then yaw.
            local = glm.translate(glm.vec3(self.tx, self.ty, self.tz))

            if self.rz:
                local = glm.rotate(local, self.rz, glm.vec3(0,0,1)) # yaw
            if self.ry:
                local = glm.rotate(local, self.ry, glm.vec3(0,1,0)) # pitch
            if self.rx:
                local = glm.rotate(local, self.rx, glm.vec3(1,0,0)) # roll

            local = glm.scale(local, glm.vec3(self.sx, self.sy, self.sz))

            self.local = local
            self.dirty = False

            return self.local

    def update_transforms(self, root_transform):
        for node in self.iterobjects():
            if node.parent == None:
                node.transform = root_transform @ node.get_local_transform()
            else:
                node.transform = node.parent.transform @ node.get_local_transform()

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
        def __setitem__(self, key, value):
            setvalueref(self, key, value)
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
        def __setitem__(self, key, value):
            setvalueref(self, key, value)
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
        def __setitem__(self, key, value):
            setvalueref(self, key, value)
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
        resource_position = glm.vec3()
        # northing
        resource_position[a_local.northing_axis] = self["local_position"]["northing"] if a_local.northing_positive else -self["local_position"]["northing"]
        # easting
        resource_position[a_local.easting_axis] = self["local_position"]["easting"] if a_local.easting_positive else -self["local_position"]["easting"]
        # elevation
        resource_position[a_local.elevation_axis] = self["local_position"]["elevation"] if a_local.elevation_positive else -self["local_position"]["elevation"]

        forward = glm.vec3()
        forward[a_local.northing_axis] = 1 if a_local.northing_positive else -1

        right = glm.vec3()
        right[a_local.easting_axis] = 1 if a_local.easting_positive else -1

        up = glm.vec3()
        up[a_local.elevation_axis] = 1 if a_local.elevation_positive else -1

        resource = glm.translate(resource_position) # translate
        resource = glm.rotate(resource, -self["local_rotation"]["yaw"], up) # yaw
        resource = glm.rotate(resource, self["local_rotation"]["pitch"], right) # pitch
        resource = glm.rotate(resource, self["local_rotation"]["roll"], forward) #  roll

        return resource @ a_local.get_j670_to_local_transform()

    def get_resource_to_local_transform(self, a_local: J670ToLocal, a_ecef_to_local):
        if self.type == "local":
            return self.get_transform(a_local)
        elif self.type != "wgs":
            raise Exception('expecting type T_WGS')

        lat = math.radians(self["wgs"]["lat"])
        lon = math.radians(self["wgs"]["lon"])
        alt = math.radians(self["wgs"]["alt"])

        ecef = lla_to_ecef(lat,lon,alt)
        local = glm.vec4(ecef, 1) @ a_ecef_to_local

        resource = glm.translate(glm.vec3(local[0], local[1], local[2]))

        # TODO: add matrix rotation for wgs
        return resource @ a_local.get_j670_to_local_transform()

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
            for key, value in json.items():
                setattr(self, key, value)

        def __setitem__(self, key, value):
            setvalueref(self, key, value)

        def __getitem__(self, key):
            if key in self.__dict__:
                return getattr(self, key)

class AsBuiltShapes(Interface):
    def __init__(self, abshapes_json):
        super(AsBuiltShapes, self).__init__(abshapes_json)
        self.shapes = list(map(functools.partial(self.Shape, interface=self), abshapes_json.get("shapes", {})))

    def cache(self, component):
        for shape in self.shapes:
            for vertex in shape.vertices:
                vertex.point = component.get_interface_object(vertex.point_reference)
                for constant in vertex.constants:
                    key, value_id = constant.value_reference.rsplit(".", 1)
                    raw_sensors = component.get_interface_object(key)
                    constant.value = raw_sensors[value_id]

    class Shape(object):
        def __init__(self, shape_json, interface):
            self.id = shape_json["id"]
            self.functions = list(map(functools.partial(AsBuiltShapes.FourCC), shape_json["functions"]))
            self.vertices = list(map(functools.partial(AsBuiltShapes.Shape.Vertex), shape_json["vertices"]))

            self._enum_map = OrderedDict()
            self._enum_map["type"] = AsBuiltShapes.Shape.Type(shape_json["type"])
            self._enum_map["enabled"] = AsBuiltShapes.Shape.Enabled(shape_json["enabled"])
            self._enum_map["apply_when"] = AsBuiltShapes.Shape.ApplyWhen(shape_json["apply_when"])
            interface[self.id] = self

        def __setitem__(self, key, value):
            if key == "type":
                self._enum_map[key] = AsBuiltShapes.Shape.Type(value)
            elif key == "enabled":
                 self._enum_map[key] = AsBuiltShapes.Shape.Enabled(value)
            elif key == "apply_when":
                 self._enum_map[key] = AsBuiltShapes.Shape.ApplyWhen(value)

        def __getitem__(self, name):
            return self._enum_map[name].value

        def is_enabled(self):
            return self._enum_map["enabled"] == AsBuiltShapes.Shape.Enabled.ENABLED

        class Vertex(object):
            def __init__(self, vertex):
                self.point_reference = vertex["point_ref"]
                self.constants = list(map(functools.partial(AsBuiltShapes.Shape.Vertex.Constants), vertex["constants"]))
                self.point = None

            def __getitem__(self, key):
                if key in self.__dict__:
                    return getattr(self, key)

            class Constants(object):
                def __init__(self, constant):
                    self.function = constant["function"]
                    self.value_reference = constant["value_ref"]
                    self.value = None

                def __getitem__(self, key):
                    if key in self.__dict__:
                        return getattr(self, key)

        class Type(Enum):
            LINE = "line"
            QUAD = "quad"
            def __init__(self, value):
                self._value_ = value

        class Enabled(Enum):
            DISABLED = 0
            ENABLED = 1
            def __init__(self, value):
                self._value_ = value

        class ApplyWhen(Enum):
            ALWAYS = 0
            HEIGHT_LOWER = 1
            HEIGHT_HIGHER = 2
            INITIALIZED = 3
            HEIGHT_LOWER_AND_INITIALIZED = 4
            HEIGHT_HIGHER_AND_INITIALIZED = 5
            def __init__(self, value):
                self._value_ = value

    class FourCC(object):
        def __init__(self, function):
            if function is None or len(function) > 4:
                raise RuntimeError(f"expected valid four char code, got: {function}")

            c = [None] * len(function)
            for i in range(len(function)):
                c[i] = chr(ord(function[i]) & 255)

            self.fourCC = "".join(c)

        def __str__(self):
            return self.fourCC

class Component(object):
    interface_factory = {
        "replicate": Replicate,
        "points_of_interest": PointsOfInterest,
        "nodes": Nodes,
        "transform": Transform,
        "attach": Attach,
        "asbuilt_shapes": AsBuiltShapes
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
        self.version = rc_json["version"]
        self.uuid = uuid.UUID(rc_json["uuid"])
        self.description = rc_json["description"]
        self.resource_type = rc_json["resource_type"]
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
                    attach_transform = glm.identity(glm.mat4)

                nodes = component.interfaces["nodes"]
                nodes.update_transforms(attach_transform)