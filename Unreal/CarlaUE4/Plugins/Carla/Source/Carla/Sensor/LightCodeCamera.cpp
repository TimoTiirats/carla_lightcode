// Copyright (c) 2017 Computer Vision Center (CVC) at the Universitat Autonoma
// de Barcelona (UAB).
//
// This work is licensed under the terms of the MIT license.
// For a copy, see <https://opensource.org/licenses/MIT>.

#include "Carla.h"
#include "Carla/Sensor/LightCodeCamera.h"

#include "Carla/Sensor/PixelReader.h"

FActorDefinition ALightCodeCamera::GetSensorDefinition()
{
  /*
    If needed any additional parameter for LightCode camera could be defined here!
    
    Add:
    - Range
  */

  FActorDefinition cameraDefinition = UActorBlueprintFunctionLibrary::MakeCameraDefinition(TEXT("lightcode"));

  FActorVariation Range;
  Range.Id = TEXT("range");
  Range.Type = EActorAttributeType::Float;
  Range.RecommendedValues = { TEXT("20.0") };
  Range.bRestrictToRecommended = false;

  cameraDefinition.Variations.Append({ Range });

  return cameraDefinition;
}

void ALightCodeCamera::Set(const FActorDescription &Description) 
{ 
  Super :: Set(Description);

  range = UActorBlueprintFunctionLibrary::RetrieveActorAttributeToFloat(
    "range",
    Description.Variations,
    20.0f);
}

ALightCodeCamera::ALightCodeCamera(const FObjectInitializer &ObjectInitializer)
  : Super(ObjectInitializer)
{
  AddPostProcessingMaterial(
      TEXT("Material'/Carla/PostProcessingMaterials/PhysicLensDistortion.PhysicLensDistortion'"));
  AddPostProcessingMaterial(
#if PLATFORM_LINUX
      TEXT("Material'/Carla/PostProcessingMaterials/DepthEffectMaterial_GLSL.DepthEffectMaterial_GLSL'")
#else
      TEXT("Material'/Carla/PostProcessingMaterials/DepthEffectMaterial.DepthEffectMaterial'")
#endif
  );
}

void ALightCodeCamera::PostPhysTick(UWorld *World, ELevelTick TickType, float DeltaSeconds)
{
  TRACE_CPUPROFILER_EVENT_SCOPE(ALightCodeCamera::PostPhysTick);
  FPixelReader::SendPixelsInRenderThread(*this);
}

float ALightCodeCamera::GetRange() const
{
  return range;
}
