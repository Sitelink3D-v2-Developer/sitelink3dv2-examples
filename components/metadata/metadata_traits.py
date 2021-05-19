#!/usr/bin/python
import hashlib
import json
import uuid
import time

class MetadataTraitsBase():
    def __init__(self, a_object_value, a_display_name):
        self.value = a_object_value
        self.display_name = a_display_name

    def class_name(self):
        return self.display_name

    def object_name(self):
        return self.value["name"]

class GenericNamedMetadataTraits(MetadataTraitsBase):
    def __init__(self, a_object_value, a_display_name):
        MetadataTraitsBase.__init__(self, a_object_value, a_display_name)

    def object_details(self):
        return "\'{}\'.".format(self.object_name())

class FileMetadataTraits(MetadataTraitsBase):
    def __init__(self, a_object_value, a_display_name):
        MetadataTraitsBase.__init__(self, a_object_value, a_display_name)

    @staticmethod
    def post_bean_json(a_file_name, a_id, a_upload_uuid, a_file_size, a_parent_uuid=None):
        ret = {
            "_id": a_id,
            "name" : a_file_name,
            "uuid" : a_upload_uuid,
            "size" : a_file_size,
            "_rev": str(uuid.uuid4()),
            "_v"   : 0,
            "_type":"fs::file",
            "_at":int(round(time.time() * 1000))
        }
        if a_parent_uuid:
            ret["parent"] = str(a_parent_uuid)
        return ret

class DelayMetadataTraits(MetadataTraitsBase):
    def __init__(self, a_object_value, a_display_name):
        MetadataTraitsBase.__init__(self, a_object_value, a_display_name)

    @staticmethod
    def post_bean_json(a_delay_name, a_id, a_delay_code=None):
        ret = {
            "_id": a_id,
            "name" : a_delay_name,
            "_rev": str(uuid.uuid4()),
            "_v"   : 0,
            "_type":"sl::delay",
            "_at":int(round(time.time() * 1000))
        }
        if a_delay_code:
            ret["code"] = a_delay_code
        return ret

class SmartViewWidgetMetadataTraits(MetadataTraitsBase):
    def __init__(self, a_object_value):
        MetadataTraitsBase.__init__(self, a_object_value, "Live Statistics Widget")

    def smartview_instance_type_details(self):
        try:
            if "sl::smartview::hauls" == self.value["smartview_type"] : 
                return "Haul Summary configured by {}".format(self.value["_extra"]["sl::smartview::hauls"]["reported"])
        except KeyError as err:  
            pass  
        return ""

    def object_details(self):
        return "\'{}\' ({}).".format(self.object_name(), self.smartview_instance_type_details())

class TaskMetadataTraits(MetadataTraitsBase):
    def __init__(self, a_object_value):
        MetadataTraitsBase.__init__(self, a_object_value, "Task")

    def object_details(self):
        designObjectStatus = ""
        designObjectSetLength = len(self.value["design"]["designObjectSets"])
        if designObjectSetLength > 0:
            designObjectStatus = "{} assigned Design Object Sets".format(designObjectSetLength)
        else:
            designObjectStatus = "no Design Data"

        materialStatus = "no material filtering"
        try:
            materialLength = len(self.value["materials"]["available"])
            if materialLength > 0:
                materialStatus = "filtered to provide only {} materials".format(materialLength)
        
        except KeyError as err:  
            pass     

        return "\'{}\' with {} and {}.".format(self.object_name(), designObjectStatus, materialStatus)

    @staticmethod
    def post_bean_json(a_task_name, a_design_set_id=None):
        ret = { 
            "activities":[],
            "design": { "alignment":{"locked":False},
                        "designObjectSets":[],
                        "surface":{"locked":False}
                    },
            "materials":{},
            "name":a_task_name,
            "sequenceTypeClass":"none",
            "_rev":str(uuid.uuid4()),
            "_type":"sl::task",
            "_id": str(uuid.uuid4()),
            "_at": int(round(time.time() * 1000))
        }
        if a_design_set_id is not None:
            ret["design"]["designObjectSets"] = [a_design_set_id]
        return ret
        
class SiteMetadataTraits(MetadataTraitsBase):
    def __init__(self, a_object_value):
        MetadataTraitsBase.__init__(self, a_object_value, "Site")

    def object_details(self):
        siteDiscoveryStatus = "site discovery disabled"
        location = "unknown location"

        try:
            if True == self.value["_extra"]["sl::site::site_discovery"]["discoverable"]:
                siteDiscoveryStatus = "site discovery enabled"

            location = "lat:{}, lon:{}".format(self.value["marker"]["lat"],self.value["marker"]["lon"])

        except KeyError as err:  
            pass    

        return "\'{}\' at {} with {}.".format(self.object_name(), location, siteDiscoveryStatus)

    @staticmethod
    def post_bean_json(a_site_name, a_latitude, a_longitude, a_phone, a_email, a_name, a_timezone):
        return {
            "_at"  : int(round(time.time() * 1000)),
            "_id"  : "site",
            "_rev" : str(uuid.uuid4()),
            "_type": "sl::site",
            "_v"   : 3,
            "job_code": "code",
            "marker": {
                "lat": float(a_latitude),
                "lon": float(a_longitude)
            },
            "contact": {
                "phone": a_phone,
                "email": a_email,
                "name" : a_name
            },
            "name"     : a_site_name,
            "timezone" : a_timezone
        }
    
class RegionMetadataTraits(MetadataTraitsBase):
    def __init__(self, a_object_value):
        MetadataTraitsBase.__init__(self, a_object_value, "Region")

    class Vertices:
        def __init__(self, a_data):
            self.data = a_data
        
        def to_json(self):
            ret =  { "storage_type" : "data", "data" : self.data }

            return ret

    class Haul:
        def __init__(self, a_autoload_material_uuid=None, a_autodump_material_uuid=None):
            self.autoload_material_uuid = a_autoload_material_uuid
            self.autodump_material_uuid = a_autodump_material_uuid

        def to_json(self):
            ret = {}
            if self.autoload_material_uuid is not None:
                ret["autoload_material"] = self.autoload_material_uuid
            if self.autodump_material_uuid is not None:
                ret["autodump_material"] = self.autodump_material_uuid

            return ret

    @staticmethod
    def post_bean_json(a_region_name, a_id, a_verticies, a_discoverable=False, a_color="#ff00ff", a_coordinate_system="wgs84", a_opacity=50, a_haul_mixin=None, a_rds_mixin=None):
        ret = {
            "_id": a_id,
            "name" : a_region_name,
            "color" : a_color,
            "opacity" : a_opacity,
            "coordinate_system" : a_coordinate_system,
            "vertices" : a_verticies.to_json(),
            "is_site_discovery" : a_discoverable,
            "_rev": str(uuid.uuid4()),
            "_v"   : 1,
            "_type":"sl::region",
            "_at":int(round(time.time() * 1000))
        }

        extras_json = {}
        extras_json["sl::region::haul"] = {}
        extras_json["sl::region::rds"] = { "usage":"" }
        extras_json["sl::region::import"] = {
            "import_file":{}
        }
        if a_haul_mixin is not None:
            extras_json["sl::region::haul"] = a_haul_mixin.to_json()

        if a_rds_mixin is not None:        
            extras_json["sl::region::rds"] = a_rds_mixin.to_json()

        if bool(extras_json):
            ret["_extra"] = extras_json

        return ret   

    def object_details(self):
        siteDiscoveryStatus = "site discovery disabled"
        verticiesLen = 0
        try:
            if True == self.value["is_site_discovery"]:
                siteDiscoveryStatus = "site discovery enabled"
        except KeyError as err:  
            pass     
        try:          
            verticiesLen = len(self.value["vertices"]["data"])
        except KeyError as err:  
            pass    

        return "\'{}\' with {} vertices and {}.".format(self.object_name(), verticiesLen, siteDiscoveryStatus)


class OperatorMetadataTraits():
    def __init__(self, a_object_value):
        self.value = a_object_value
        
    def class_name(self):
        return "Operator"

    def object_name(self):
        return "{} {}".format(self.value["firstName"], self.value["lastName"])

    def object_details(self):
        return "\'{}\'.".format(self.object_name())

    @staticmethod
    def post_bean_json(a_first_name, a_last_name, a_code=None):
        ret = {
            "_id": str(uuid.uuid4()),
            "firstName" : a_first_name,
            "lastName" : a_last_name,
            "_rev": str(uuid.uuid4()),
            "_v"   : 0,
            "_type":"sl::operator",
            "_at":int(round(time.time() * 1000))
        }
        if a_code:
            ret["code"] = a_code
        return ret

class MaterialMetadataTraits(MetadataTraitsBase):
    def __init__(self, a_object_value):
        MetadataTraitsBase.__init__(self, a_object_value, "Material")

    class AcceptedMeasurement:
        def __init__(self, a_axis, a_units):
            self.axis = a_axis
            self.units = a_units

        def to_json(self):
            return { "axis": self.axis, self.axis: self.units }

    class Conversion:
        def __init__(self, a_accepted_measurement, a_factor):
            self.accepted_measurement = a_accepted_measurement
            self.factor = a_factor
        
        def to_json(self):
            return { "axis": self.accepted_measurement.to_json(), "factor": self.factor }

    class PairedConversion:
        def __init__(self, a_left_conversion, a_right_conversion):
            self.left_conversion = a_left_conversion
            self.right_conversion = a_right_conversion
        
        def to_json(self):
            return { "left": self.left_conversion.to_json(), "right": self.right_conversion.to_json() }

    class AdditionalState:
        def __init__(self, a_name, a_conversions):
            self.name = a_name
            self.conversions = a_conversions
        
        def to_json(self):
            ret =  { "name": self.name }
            conversions_json = []
            for conversion in self.conversions:
                conversions_json.append(conversion.to_json())

            ret["conversionsFromDefaultState"] = conversions_json

            return ret

    class DefaultState:
        def __init__(self, a_name, a_paired_conversions):
            self.name = a_name
            self.paired_conversions = a_paired_conversions
        
        def to_json(self):
            ret =  { "name": self.name }
            conversions_json = []
            for conversion in self.paired_conversions:
                conversions_json.append(conversion.to_json())

            ret["measurementConversions"] = conversions_json

            return ret

    class Haul:
        def __init__(self, a_operator_entry_measurement, a_operator_entry_state_name):
            self.operator_entry_measurement = a_operator_entry_measurement
            self.operator_entry_state_name = a_operator_entry_state_name
        
        def to_json(self):
            return {"operatorEntryMeasurement": self.operator_entry_measurement.to_json(), "operatorEntryState" : self.operator_entry_state_name}

    class RDS:
        def __init__(self, a_density, a_descriptions, a_price, a_regulation):
            self.density = a_density
            self.descriptions = a_descriptions
            self.price = a_price
            self.regulation = a_regulation
        
        def to_json(self):
            return { "density": self.density, "price" : self.price, "descriptions" : self.descriptions, "regulation" : self.regulation }


    @staticmethod
    def post_bean_json(a_material_name, a_id, a_accepted_measurements=None, a_default_state=None, a_additional_states=None, a_haul_mixin=None, a_rds_mixin=None):
        ret = {
            "_id": a_id,
            "name" : a_material_name,
            "_rev": str(uuid.uuid4()),
            "_v"   : 2,
            "_type":"sl::material",
            "_at":int(round(time.time() * 1000))
        }
        measurements_json = []
        accepted_measurement_volume =  MaterialMetadataTraits.AcceptedMeasurement(a_axis="volume", a_units="cubic_metres")
        ret["acceptedMeasurements"] = [accepted_measurement_volume.to_json()]
        if a_accepted_measurements is not None:
            for measurement in a_accepted_measurements:
                measurements_json.append(measurement.to_json())
            ret["acceptedMeasurements"] = measurements_json

        states_json = []
        if a_additional_states is not None:
            for state in a_additional_states:
                states_json.append(state.to_json())

        default_state_json = { "measurementConversions":[], "name":"Default" }
        if a_default_state is not None:
            default_state_json = a_default_state.to_json()

        amalgamated_states_json = {"additionalState" : states_json, "defaultState": default_state_json}
        ret["states"] = amalgamated_states_json

        haul_mixin = MaterialMetadataTraits.Haul(a_operator_entry_measurement=accepted_measurement_volume, a_operator_entry_state_name="Default")
        rds_mixin = MaterialMetadataTraits.RDS(a_density=1, a_descriptions=[], a_price=0, a_regulation="none")
        extras_json = {}


        extras_json["sl::material::haul"] = haul_mixin.to_json()
        if a_haul_mixin is not None:
            extras_json["sl::material::haul"] = a_haul_mixin.to_json()

        extras_json["sl::material::rds"] = rds_mixin.to_json()
        if a_rds_mixin is not None:        
            extras_json["sl::material::rds"] = a_rds_mixin.to_json()

        if bool(extras_json):
            ret["_extra"] = extras_json
        return ret        

    def object_details(self):
        acceptedMeasurementsLen = 0
        try:          
            acceptedMeasurementsLen = len(self.value["acceptedMeasurements"])
        except KeyError as err:  
            pass   
        additionalStateLen = 0
        try:          
            additionalStateLen = len(self.value["additionalState"])
        except KeyError as err:  
            pass   

        return "\'{}\' with {} accepted measurement type(s) and {} material state(s).".format(self.object_name(), acceptedMeasurementsLen, additionalStateLen+1)

class DesignObjectSetMetadataTraits(MetadataTraitsBase):
    def __init__(self, a_object_value):
        MetadataTraitsBase.__init__(self, a_object_value, "Design Object Set")

    def object_details(self):
        designObjectLen = 0
  
        try:          
            designObjectLen = len(self.value["designObject"])
        except KeyError as err:  
            pass    

        return "\'{}\' with {} Design Object(s).".format(self.object_name(), designObjectLen)

class ListMetadataTraits(MetadataTraitsBase):
    def __init__(self, a_object_value):
        MetadataTraitsBase.__init__(self, a_object_value, "View List")

    def object_details(self):
        view_name = ""
        try:          
            view_name = self.value["view"]
        except KeyError as err:  
            pass    

        view_icon = ""
        try:          
            view_icon = self.value["icon"]
        except KeyError as err:  
            pass  

        return "with view name {} and display icon \'{}\'.".format(view_name, view_icon)

class AuthCodeMetadataTraits(MetadataTraitsBase):
    def __init__(self, a_object_value):
        MetadataTraitsBase.__init__(self, a_object_value, "Auth Code")

    def object_details(self):
        validDays = 0
  
        try:          
            validDays = self.value["valid_days"]
        except KeyError as err:  
            pass    

        return "\'{}\' with validity of {} day(s).".format(self.object_name(), validDays)

    @staticmethod
    def post_bean_json(a_code_name, a_code_pin, a_valid_days=1):
        ret = {
            "_id": str(uuid.uuid4()),
            "name": a_code_name,
            "_rev": str(uuid.uuid4()),
            "valid_days":a_valid_days,
            "_type":"sl::auth_code",
            "pin_sha256" : hashlib.sha256(a_code_pin.encode()).hexdigest(),
            "_at":int(round(time.time() * 1000))
        }
        return ret


class AssetMetadataTraits(MetadataTraitsBase):
    def __init__(self, a_object_value):
        MetadataTraitsBase.__init__(self, a_object_value, "Asset")

    def object_details(self):
        assetClass = ""
        try:          
            assetClass = self.value["asset_class"]
        except KeyError as err:  
            pass    

        return "\'{}\' ({}).".format(self.object_name(), assetClass)

class Metadata(object):

    def traits_factory(a_object_value):
        try:
            if a_object_value["_type"] == "sl::task":
                return TaskMetadataTraits(a_object_value)
            if a_object_value["_type"] == "sl::smartview":
                return SmartViewWidgetMetadataTraits(a_object_value)
            if a_object_value["_type"] == "sl::site":
                return SiteMetadataTraits(a_object_value)
            if a_object_value["_type"] == "sl::shift_plan":
                return GenericNamedMetadataTraits(a_object_value, "Shift Plan")
            if a_object_value["_type"] == "sl::region":
                return RegionMetadataTraits(a_object_value)
            if a_object_value["_type"] == "sl::operator" or  a_object_value["_type"] == "sl::customer":
                return OperatorMetadataTraits(a_object_value)
            if a_object_value["_type"] == "sl::material":
                return MaterialMetadataTraits(a_object_value)    
            if a_object_value["_type"] == "_type" and a_object_value["_mixin"] == "sl::smartview":
                return GenericNamedMetadataTraits(a_object_value, "Widget Type")   
            if a_object_value["_type"] == "sl::designObjectSet":
                return DesignObjectSetMetadataTraits(a_object_value)      
            if a_object_value["_type"] == "sl::delay":
                return DelayMetadataTraits(a_object_value, "Delay")    
            if a_object_value["_type"] == "sl::list":
                return ListMetadataTraits(a_object_value)   
            if a_object_value["_type"] == "sl::auth_code":
                return AuthCodeMetadataTraits(a_object_value)
            if a_object_value["_type"] == "sl::asset":
                return AssetMetadataTraits(a_object_value)
            if a_object_value["_type"] == "sl::designObject":
                return GenericNamedMetadataTraits(a_object_value, "Design Object")
            if a_object_value["_type"] == "sl::asbuilt_passcount_color_map":
                return GenericNamedMetadataTraits(a_object_value, "AsBuilt Pass Count Color Map")
            if a_object_value["_type"] == "sl::asbuilt_cutfill_color_map":
                return GenericNamedMetadataTraits(a_object_value, "AsBuilt Cut Fill Color Map")
            if a_object_value["_type"] == "sl::asbuilt_stiffness_color_map":
                return GenericNamedMetadataTraits(a_object_value, "AsBuilt Stiffness Color Map")
            if a_object_value["_type"] == "sl::asbuilt_temperature_color_map":
                return GenericNamedMetadataTraits(a_object_value, "AsBuilt Temperature Color Map")
            if a_object_value["_type"] == "sl::mapTileset":
                return GenericNamedMetadataTraits(a_object_value, "Map Tile Set")
            if a_object_value["_type"] == "fs::file":
                return GenericNamedMetadataTraits(a_object_value, "File")
            if a_object_value["_type"] == "fs::folder":
                return GenericNamedMetadataTraits(a_object_value, "Folder")
        except TypeError as err:
            pass

        else:
            print(json.dumps(a_object_value, sort_keys=True, indent=4))

    traits_factory = staticmethod(traits_factory)
