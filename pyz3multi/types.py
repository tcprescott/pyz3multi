class MessageType:
    ItemFill = 0x00
    DungeonFill = 0x01
    EquipmentFill = 0x02
    RequestItem = 0x03
    AcquireItem = 0x04
    Finish = 0x05

    LobbyRequest = 0x10
    LobbyEntry = 0x11
    Create = 0x12
    Destroy = 0x13
    Identify = 0x14
    Knock = 0x15
    WorldDescription = 0x16
    WorldClaim = 0x17
    RoomReady = 0x18
    Kick = 0x19
    ImportRecords = 0x1F

    CreateFile = 0x40
    DeleteFile = 0x41
    SelectSpawn = 0x42
    EnterArea = 0x43
    FinishDungeon = 0x44
    Death = 0x45
    SaveQuit = 0x46

    PrepWrite = 0xE0

    Chat = 0xF0
    Introduction = 0xF1
    Version = 0xFE
    Log = 0xFF

class MessageTypeReverse:
    {
        0x00: "ItemFill",
        0x01: "DungeonFill",
        0x02: "EquipmentFill",
        0x03: "RequestItem",
        0x04: "AquireItem",
        0x05: "Finish",

        0x10: "LobbyRequest",
        0x11: "LobbyEntry",
        0x12: "Create",
        0x13: "Destroy",
        0x14: "Identify",
        0x15: "Knock",
        0x16: "WorldDescription",
        0x17: "WorldClaim",
        0x18: "RoomReady",
        0x19: "Kick",
        0x1F: "ImportRecords",

        0x40: "CreateFile",
        0x41: "DeleteFile",
        0x42: "SelectSpawn",
        0x43: "EnterArea",
        0x44: "Finish Dungeon",
        0x45: "Death",
        0x46: "SaveQuit",

        0xE0: "PrepWrite",

        0xF0: "Chat",
        0xF1: "Introduction",
        0xFE: "Version",
        0xFF: "Log",
    }

class GameMode:
    Lobby = 0
    Secure1P = 1
    Multiworld = 2
    LockoutTriforce = 3
    AutoBingo = 4
    SharedState = 5
    DungeonCrawl = 6