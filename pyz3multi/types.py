class MessageTypes:
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
