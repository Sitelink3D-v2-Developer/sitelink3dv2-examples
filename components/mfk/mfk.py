
from textwrap import indent
import numpy as np
import numpy.matlib
import functools
import base64
import uuid
from collections import OrderedDict
from struct import Struct
import logging
import json

def rot_matrix(rx, ry, rz):
    mz = np.matrix([(np.cos(rz),-np.sin(rz), 0.),
                    (np.sin(rz), np.cos(rz), 0.),
                    (0.,         0.,         1.)], float)
    my = np.matrix([( np.cos(ry), 0., np.sin(ry)),
                    ( 0.,         1., 0.        ),
                    (-np.sin(ry), 0., np.cos(ry))], float)
    mx = np.matrix([(1., 0.,         0.        ),
                    (0., np.cos(rx),-np.sin(rx)),
                    (0., np.sin(rx), np.cos(rx))], float)
    return mz * my * mx

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

    def decode(self, manifest_binary):
        items = self.struct.unpack(manifest_binary)
        logging.debug("Replicate interface object has decoded the binary manifest to produce the following items: {0}".format(items))
        return dict(zip(list(m.ref for m in self.manifest_items), items))

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
            return np.matrix([(self.tx, self.ty, self.tz, 1.)]).T

        def get_id(self):
            return self.id

        def __repr__(self):
            return str((self.id, self.tx, self.ty, self.tz, "+" + self.node_ref))

class AuxControlData(Interface):
    def __init__(self, aux_control_json):
        super(AuxControlData, self).__init__(aux_control_json)
        self.control_data = list(map(functools.partial(self.ControlData, interface=self), aux_control_json["data"]))
    
    class ControlData(object):
        def __init__(self, control_json, interface):
            self.id = control_json.get("id", 0)
            self.description = control_json.get("description", "")
            self.value = control_json.get("value", 0)
            self.interface = interface
            interface[self.id] = self

        def get_id(self):
            return self.id

        def __setitem__(self, key, value):
            setattr(self, key, value)

        def __repr__(self):
            return str((self.id, self.description, self.value))

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
        n = len(nodes)
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
            self.id = node_json["id"]

            self.transform = None
            interface[self.id] = self

            nodes = node_json["nodes"]
            n = len(nodes)
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

            M = np.matlib.eye(4)
            M[:3, :3] = rot_matrix(self.rx, self.ry, self.rz)
            M[0, 3] = self.tx
            M[1, 3] = self.ty
            M[2, 3] = self.tz

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

    def get_transform(self):
        M = np.matlib.eye(4)
        M[:3, :3] = rot_matrix(self.local_rotation.roll,
                               self.local_rotation.pitch,
                               -self.local_rotation.yaw)
        M[0, 3] = self.local_position.northing
        M[1, 3] = self.local_position.easting
        M[2, 3] = -self.local_position.elevation

        return M

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

class Component(object):
    interface_factory = {
        "aux_control_data" : AuxControlData,
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
            if name not in self.interface_factory:
                continue
            klass = self.interface_factory[name]
            interfaces[name] = klass(interface)
        self.interfaces = interfaces

    def cache(self):
        for name, interface in self.interfaces.items():
            interface.cache(self)

    def get_interface_object(self, key):
        oem, name, node_name = key.split(".")
        interface = self.interfaces.get(name, None)
        return interface and interface[node_name]

    def update(self, values):
        for key,value in values.items():
            node_name, prop = key.rsplit(".", 1)
            logging.debug("Updating node name {} and property {} to value {}".format(node_name, prop, value))
            node = self.get_interface_object(node_name)
            if node:
                node[prop] = value

    def decode_manifest(self, manifest):
        if not manifest:
            return {}

        replicate = self.interfaces["replicate"]
        return replicate.decode(base64.b64decode(manifest))

class ResourceConfiguration(object):
    def __init__(self, rc_json):
        self._json = rc_json
        self.components = list(map(Component, rc_json["data"]["components"])) 
        
        self.cache()
        self.update_transforms()

    def apply_manifest(self, manifests):
        for manifest, component in zip(manifests, list(self.components)):
            values = component.decode_manifest(manifest)
            logging.debug("values = {0}".format(values))
            component.update(values)
        self.update_transforms()
        return self

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
                    attach_transform = np.matlib.eye(4)

                nodes = component.interfaces["nodes"]
                nodes.update_transforms(attach_transform)
