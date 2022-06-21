// Copyright (c) 2017 Computer Vision Center (CVC) at the Universitat Autonoma
// de Barcelona (UAB).
//
// This work is licensed under the terms of the MIT license.
// For a copy, see <https://opensource.org/licenses/MIT>.

#include "carla/sensor/s11n/LightCodeSerializer.h"

#include "carla/sensor/data/Image.h"

namespace carla {
namespace sensor {
namespace s11n {

  SharedPtr<SensorData> LightCodeSerializer::Deserialize(RawData &&data) {
    return SharedPtr<data::LightCodeImage>(new data::LightCodeImage{std::move(data)});
  }

} // namespace s11n
} // namespace sensor
} // namespace carla
