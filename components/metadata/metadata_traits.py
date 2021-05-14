#!/usr/bin/python

import json

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
        return "\'{}\'.".format(self.object_name().encode("utf8"))

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
        return "\'{}\' ({}).".format(self.object_name().encode("utf8"), self.smartview_instance_type_details())

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

        return "\'{}\' with {} and {}.".format(self.object_name().encode("utf8"), designObjectStatus, materialStatus)
        
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
    
class RegionMetadataTraits(MetadataTraitsBase):
    def __init__(self, a_object_value):
        MetadataTraitsBase.__init__(self, a_object_value, "Region")

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

        return "\'{}\' with {} vertices and {}.".format(self.object_name().encode("utf8"), verticiesLen, siteDiscoveryStatus)


class OperatorMetadataTraits():
    def __init__(self, a_object_value):
        self.value = a_object_value
        
    def class_name(self):
        return "Operator"

    def object_name(self):
        return "{} {}".format(self.value["firstName"], self.value["lastName"])

    def object_details(self):
        return "\'{}\'.".format(self.object_name())

class MaterialMetadataTraits(MetadataTraitsBase):
    def __init__(self, a_object_value):
        MetadataTraitsBase.__init__(self, a_object_value, "Material")

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

        return "\'{}\' with {} Design Object(s).".format(self.object_name().encode("utf8"), designObjectLen)

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

        return "\'{}\' with validity of {} day(s).".format(self.object_name().encode("utf8"), validDays)

class AssetMetadataTraits(MetadataTraitsBase):
    def __init__(self, a_object_value):
        MetadataTraitsBase.__init__(self, a_object_value, "Asset")

    def object_details(self):
        assetClass = ""
        try:          
            assetClass = self.value["asset_class"]
        except KeyError as err:  
            pass    

        return "\'{}\' ({}).".format(self.object_name().encode("utf8"), assetClass)

class Metadata(object):

    def traits_factory(a_object_value):
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
        if a_object_value["_type"] == "sl::operator":
            return OperatorMetadataTraits(a_object_value)
        if a_object_value["_type"] == "sl::material":
            return MaterialMetadataTraits(a_object_value)    
        if a_object_value["_type"] == "_type" and a_object_value["_mixin"] == "sl::smartview":
            return GenericNamedMetadataTraits(a_object_value, "Widget Type")   
        if a_object_value["_type"] == "sl::designObjectSet":
            return DesignObjectSetMetadataTraits(a_object_value)      
        if a_object_value["_type"] == "sl::delay":
            return GenericNamedMetadataTraits(a_object_value, "Delay")    
        if a_object_value["_type"] == "sl::list":
            return ListMetadataTraits(a_object_value)   
        if a_object_value["_type"] == "sl::auth_code":
            return AuthCodeMetadataTraits(a_object_value)
        if a_object_value["_type"] == "sl::asset":
            return AssetMetadataTraits(a_object_value)
        if a_object_value["_type"] == "sl::asbuilt_passcount_color_map":
            return GenericNamedMetadataTraits(a_object_value, "AsBuilt Pass Count Color Map")
        if a_object_value["_type"] == "sl::asbuilt_cutfill_color_map":
            return GenericNamedMetadataTraits(a_object_value, "AsBuilt Cut Fill Color Map")
        if a_object_value["_type"] == "sl::asbuilt_stiffness_color_map":
            return GenericNamedMetadataTraits(a_object_value, "AsBuilt Stiffness Color Map")
        if a_object_value["_type"] == "sl::asbuilt_temperature_color_map":
            return GenericNamedMetadataTraits(a_object_value, "AsBuilt Temperature Color Map")
        if a_object_value["_type"] == "fs::file":
            return GenericNamedMetadataTraits(a_object_value, "File")
        if a_object_value["_type"] == "fs::folder":
            return GenericNamedMetadataTraits(a_object_value, "Folder")

        else:
            print(json.dumps(a_object_value, sort_keys=True, indent=4))

    traits_factory = staticmethod(traits_factory)
