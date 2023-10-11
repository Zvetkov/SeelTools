from gameobjects.object_classes import Object


class Level(Object):
    def __init__(self):
        Object.__init__(self)
        self.weatherDetailName = ""
        self.weatherType = ""
        self.currentDayTime = 0
        self.levelPath = ""
        self.levelName = ""
        self.hfName = ""
        self.waterName = ""
        self.cameraMapName = ""
        self.colorMapName = ""
        self.cliffsetName = ""
        self.cliffmapName = ""
        self.roadsetName = ""
        self.roadmapName = ""
        self.waypointsName = ""
        self.beachsetsName = ""
        self.shoreLineName = ""
        self.normalMapName = ""
        self.cubeMapName = ""
        self.dsSrvName = ""
        self.questStatesFileName = ""
        self.externalPathsFileName = ""
        self.staticObstaclesFileName = ""
        self.playerPassMapFileName = ""
        self.prototypeFullNames = ""
        self.ObjectsFullNames = ""
        self.serversname = ""
        self.staticServers = ""
        self.passMapName = ""
        self.passMapCellSize = 1
        self.triggersName = ""
        self.cinemaTriggersName = ""
        self.dialogStrings = ""
        self.landSize = 0
        self.skyType = 0
        self.envMapsNames = []
        self.skyCloudsEnable = 0
        self.lsFarColor = 0
        self.oldFarColor = 0
        self.skyScrollSpeed = 0.0
        self.skyRotateSpeed = 0.0
        self.sunAzimuthSpeed = 0.0
        self.sunAzimuth = 0.0
        self.sunDayAscention = 0.0
        self.sunRiseAscention = 0.0
        self.sunSetAscention = 0.0
        self.waterLevel = 0.0
        self.baseWaterLevel = 0.0
        self.waterTexSmall = ""
        self.waterTexBig = ""
        self.demoFile = ""
        self.tilesFileName = ""

    def Load(self):
        pass

    def New(self, levelsize: int):
        self.levelName = "Untitled"
        self.levelPath = "data\\maps\\r1m1\\"  # r"data\editor"
        self.hfName = "displace.bin"
        self.waterName = "water.raw"
        self.cameraMapName = "cameramap.raw"
        self.maxHeight = 2500.0
        self.landSize = levelsize
        self.waterLevel = 0.0
        self.baseWaterLevel = 0.0
        self.reflectionTint = -1
        self.refractionTint = -1
        safe_size = (16 * levelsize * 8) - 40
        self.skyDomeDivider = 8.0
        self.minSafeX = 40.0
        self.minSafeY = 40.0
        self.maxSafeX = safe_size 
        self.maxSafeY = safe_size
        self.dsSrvName = "DynamicScene.xml"
        self.questStatesFileName = "QuestStates.xml"
        self.prototypeFullNames = r"data\if\diz\model_names.xml"
        self.objectsFullNames = "object_names.xml"
        self.externalPathsFileName = "external_paths.xml"
        self.staticObstaclesFileName = "static_obstacles.xml"
        self.playerPassMapFileName = "player_passmap.bin"
        self.staticServers = r"data\models\commonservers.xml"
        self.roadmapName = "LevelRoads.xml"
        self.roadsetName = "Roads.xml"
        self.passMapName = "passmap.raw"
        self.colorMapName = "colormap.raw"
        self.cliffmapName = "level.cliff"
        self.cliffsetName = "Cliffs.xml"
        self.waypointsName = "ways.xml"
        self.beachsetsName = "Beachsets.xml"
        self.shoreLineName = "ShoreLine.bin"
        self.normalMapName = "NormalMap.bin"
        self.cubemapName = r"data/models/textures/lobbycube.dds"
        self.passMapCellSize = 16
        self.triggersName = "triggers.xml"
        self.cinemaTriggersName = "cinemaTriggers.xml"
        self.dialogStrings = "strings.xml"
        self.weatherDetailName = "WeatherDetail.xml"
        self.tilesFileName = "level.tile"
        self.envMapsNames = [r"data\\env\\day4.left.tga",
                             r"data\\env\\day4.up.tga",
                             r"data\\env\\day4.right.tga",
                             r"data\\env\\day4.front.tga",
                             r"data\\env\\day4.back.tga"]
        self.skyScale = [0.8, 0.4]
        self.skyScrollSpeed = 1.0
        self.skyRotateSpeed = 2.0
        self.sunAzimuth = 45.0
        self.sunAzimuthSpeed = 0.0
        self.sunDayAscention = 90.0
        self.sunRiseAscention = 53.0
        self.skyCloudsEnable = 1
        self.sunSetAscention = 127.0
        self.weatherType = "0"
        self.worldOrigin = {"x": 54.348,
                            "y": 63.34,
                            "z": 354.97}
        self.rotYaw = -3.934
        self.rotPitch = 0.37599999
        self.rotRoll = 0.0
        self.demoFile = "demo.rec"
