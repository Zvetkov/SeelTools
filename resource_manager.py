from em_parse import xml_to_objfy, read_from_xml_node, check_mono_xml_node

from logger import logger


class Resource(object):
    def __init__(self, parent):
        self.id = -1
        self.parentId = -1
        self.name = ''
        self.geomSize_x = -1
        self.geomSize_y = -1
        if parent:
            self.geomSize_x = parent.geomSize_x
            self.geomSize_y = parent.geomSize_y
            self.parentId = parent.id

    def LoadFromXML(self, xmlFile, xmlNode):
        self.name = read_from_xml_node(xmlNode, "Name")
        strGeomSize = xmlNode.attrib.get("geomsize")
        if strGeomSize is not None:
            self.geomSize_x = strGeomSize.split()[0]
            self.geomSize_y = strGeomSize.split()[1]

    def IsKindOf(self, theResourceManager, resourceId):
        resourceVector = theResourceManager.resourceVector
        resourceVectorSize = len(resourceVector)
        if self.id == -1:
            return False
        if self.id == resourceId:
            return True
        if resourceVector:
            if self.id < 0 or self.id > resourceVectorSize:
                logger.warning(f"Resource id given is {self.id}, resourceVector size is {resourceVectorSize}")
                return False
            elif self.parentId == -1:
                return False
            elif self.parentId == resourceId:
                return True
            else:
                return False
        else:
            logger.error("theResourceManager doesn't have a resourceVector!")
            return False


class ResourceManager(object):
    def __init__(self, theServer, isContinuousMap: int = 0, some_other_int=0):
        self.resourceMap = {}
        self.resourceVector = []
        self.vehiclePart2Resource = {}
        self._LoadFromXmlFile(isContinuousMap, theServer.theGlobalProperties.pathToResourceTypes)
        self._LoadVehiclePartTypeToResourceXmlFile(some_other_int, theServer.theGlobalProperties.pathToVehiclePartTypes)

    def _LoadFromXmlFile(self, some_int, fileName):
        resourceTypesXmlNode = xml_to_objfy(fileName)
        if resourceTypesXmlNode.tag == "ResourceTypes":
            check_mono_xml_node(resourceTypesXmlNode, "Type")
            for resource in resourceTypesXmlNode["Type"]:
                self._ReadResourceFromXml(fileName, resource, 0)
        else:
            raise FileNotFoundError("Can't load ResourceTypes from XML!")

    def _LoadVehiclePartTypeToResourceXmlFile(self, some_other_int, fileName):
        vehiclePartTypesXmlNode = xml_to_objfy(fileName)
        if vehiclePartTypesXmlNode.tag == "VehiclePartTypes":
            if len(vehiclePartTypesXmlNode.getchildren()) > 1:
                check_mono_xml_node(vehiclePartTypesXmlNode, "VehiclePart")
                for vehicle_part in vehiclePartTypesXmlNode["VehiclePart"]:
                    vehiclePartName = read_from_xml_node(vehicle_part, "PartName")
                    resourceName = read_from_xml_node(vehicle_part, "ResourceName")
                    if self.GetResourceId(resourceName) == -1:
                        logger.warning(f"ResourceManager: warning - invalid resource name '{resourceName}' "
                                       f"is matched to vehicle part type '{vehiclePartName}'")
                    else:
                        if self.vehiclePart2Resource.get(vehiclePartName) is None:
                            self.vehiclePart2Resource[vehiclePartName] = resourceName
                        else:
                            raise NameError(f"ResourceManager: Can't add vehicle part with name {vehiclePartName} "
                                            f"to vehiclePart2Resource map. Already exist mapping with this name.")
        else:
            raise FileNotFoundError("Can't load VehiclePartTypes from XML!")

    def _ReadResourceFromXml(self, xmlFile, xmlNode, parent=0):
        resource = Resource(parent)
        resource.id = -1
        resource.parentId = -1
        resource.name = ''
        resource.geomSize_x = -1
        resource.geomSize_y = -1
        has_parent = parent != 0

        if has_parent:
            resource.geomSize_x = parent.geomSize_x
            resource.geomSize_y = parent.geomSize_y
            resource.parentId = parent.id

        resource.LoadFromXML(xmlFile, xmlNode)
        if self.resourceMap.get(resource.name) is None:
            self.resourceMap[resource.name] = resource
        else:
            logger.warning(f"Error: duplicate resource name: {resource.name}")

        resourceVectorSize = len(self.resourceVector)
        resource.id = resourceVectorSize
        self.resourceVector.append(resource)

        if len(xmlNode.getchildren()) > 1:
            check_mono_xml_node(xmlNode, "Type")
            for child in xmlNode["Type"]:
                self._ReadResourceFromXml(xmlFile, child, resource)

    def GetResource(self, resourceId):
        return self.resourceVector[resourceId]

    def GetResourceName(self, resourceId):
        return self.resourceVector[resourceId].name

    def GetResourceId(self, resourceName):
        resource = self.resourceMap.get(resourceName)
        if resource is not None:
            return resource.id
        else:
            return -1

    def ResourceIsKindOf(self, resourceId, ancestorId):
        return self.resourceVector[resourceId].IsKindOf(self, ancestorId)

    def ResourceHasChildren(self, resourceId):
        # finds all resource that list given resourceId as parent and evaluate list to bool - empty list is false
        return bool([resource for resource in self.resourceVector if resource.parentId == resourceId])

    def GetResourceNameByVehiclePartName(self, vehiclePartName):  # (self, *result, vehiclePartName) in original
        res_name = self.vehiclePart2Resource.get(vehiclePartName)
        if res_name is not None:
            return res_name
        else:
            logger.warning(f"ResourceManager: can't find ResourceName for given VehiclePartName : {vehiclePartName}")

    def GetResourceDescendants(self, resourceId):
        return [resource for resource in self.resourceVector if resource.IsKindOf(self, resourceId)]
