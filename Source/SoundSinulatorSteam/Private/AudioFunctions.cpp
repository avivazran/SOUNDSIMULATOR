// Fill out your copyright notice in the Description page of Project Settings.
#include "AudioFunctions.h"
#include "Sound/SoundWave.h"
#include "Misc/FileHelper.h"
#include "Kismet/GameplayStatics.h"


class USoundWave* UAudioFunctions::GetSoundFromWaveFile(const FString& filePath, bool& Success)
{
    if (filePath == "") { Success = false; return nullptr; }

    USoundWave* sw = NewObject<USoundWave>(USoundWave::StaticClass());
    if (!sw) { Success = false; return nullptr; }

    TArray < uint8 > rawFile;

    FFileHelper::LoadFileToArray(rawFile, filePath.GetCharArray().GetData());
    FWaveModInfo WaveInfo;

    if (WaveInfo.ReadWaveInfo(rawFile.GetData(), rawFile.Num()))
    {

        // - catching not supported bit depth
        if (*WaveInfo.pBitsPerSample != 16) { Success = false;  return nullptr; }

        sw->InvalidateCompressedData();

        sw->RawData.Lock(LOCK_READ_WRITE);
        void* LockedData = sw->RawData.Realloc(rawFile.Num());
        FMemory::Memcpy(LockedData, rawFile.GetData(), rawFile.Num());
        sw->RawData.Unlock();

        int32 DurationDiv = *WaveInfo.pChannels * *WaveInfo.pBitsPerSample * *WaveInfo.pSamplesPerSec;
        if (DurationDiv)
        {
            sw->Duration = *WaveInfo.pWaveDataSize * 8.0f / DurationDiv;
        }
        else
        {
            sw->Duration = 0.0f;
        }
        sw->SetSampleRate(*WaveInfo.pSamplesPerSec);
        sw->NumChannels = *WaveInfo.pChannels;
        sw->RawPCMDataSize = WaveInfo.SampleDataSize;
        sw->SoundGroup = ESoundGroup::SOUNDGROUP_Default;

    }
    else {
        Success = false;
        return nullptr;
    }

    // - Baking PCM Data from file into SoundWave memory
    const int32 NumSamples = sw->RawPCMDataSize / sizeof(Audio::FResamplerResults);

    sw->RawPCMDataSize = WaveInfo.SampleDataSize;
    //sw->RawPCMData = (uint8*)FMemory::Malloc(sw->RawPCMDataSize); 
    //FMemory::Memmove(sw->RawPCMData, rawFile.GetData(), rawFile.Num());

    sw->RawPCMData = (uint8*)FMemory::Malloc(sw->RawPCMDataSize);
    FMemory::Memcpy(sw->RawPCMData, WaveInfo.SampleDataStart, NumSamples * sizeof(Audio::FResamplerResults));
    //FMemory::Memcpy(sw->RawPCMData, rawFile.GetData(), rawFile.Num());

    if (!sw) { Success = false; return nullptr; }

    Success = true;
    return sw;
}
//~~~~~~
// File IO
//~~~~~~
bool UAudioFunctions::GetALLFilesInFolder(TArray<FString>& Files, FString RootFolderFullPath, FString Ext)
{
    if (RootFolderFullPath.Len() < 1) return false;

    FPaths::NormalizeDirectoryName(RootFolderFullPath);

    IFileManager& FileManager = IFileManager::Get();

    if (!Ext.Contains(TEXT("*")))
    {
        if (Ext == "")
        {
            Ext = "*.*";
        }
        else
        {
            Ext = (Ext.Left(1) == ".") ? "*" + Ext : "*." + Ext;
        }
    }

    FString FinalPath = RootFolderFullPath + "/" + Ext;

    FileManager.FindFiles(Files, *FinalPath, true, false);
    return true;
}



