// Fill out your copyright notice in the Description page of Project Settings.


#pragma once
#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/FileHelper.h"
#include "AudioFunctions.generated.h"

using namespace std;
/**
 * 
 */
UCLASS()
class SOUNDSINULATORSTEAM_API UAudioFunctions : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

        //* Declare blueprint functions here?
        UFUNCTION(BlueprintCallable, Category = "AudioFunctions", meta = (DisplayName = "Get Sound Wave from Wave file", Keywords = "Get Sound Wave from Wave file"))
        static class USoundWave* GetSoundFromWaveFile(const FString& filePath, bool& Success);


    /** Obtain all files in a provided directory, with optional extension filter. All files are returned if Ext is left blank. Returns false if operation could not occur. */
    UFUNCTION(BlueprintPure, Category = "AudioFunctions")
        static bool GetALLFilesInFolder(TArray<FString>& Files, FString RootFolderFullPath, FString Ext);

	
};
