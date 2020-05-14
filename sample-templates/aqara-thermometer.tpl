Thing mqtt:topic:mosquitto:{{thingid}} "{{label}}" (mqtt:broker:mosquitto)  @ "Environment" {
    Channels:
        Type number : temperature  [ stateTopic="zigbee/{{thingid}}/temperature", unit="°C" ]
        Type number : humidity     [ stateTopic="zigbee/{{thingid}}/humidity", unit="%" ]
        Type number : pressure     [ stateTopic="zigbee/{{thingid}}/pressure", unit="mbar" ]
        Type number : linkquality  [ stateTopic="zigbee/{{thingid}}/linkquality" ]
        Type switch : reachable    [ stateTopic="zigbee/{{thingid}}/availability", on="online", off="offline" ]
        Type number : battery      [ stateTopic="zigbee/{{thingid}}/battery", unit="%" ]
}

Group g{{name_parts[0]}}_Temperature "{{room}} Temperature" { ga="Thermostat" }
Number:Temperature {{name_parts[0]}}_Temperature "{{room}} Temperature" <temperature> (gTemperature, g{{name_parts[0]}}_Temperature)       { channel="mqtt:topic:mosquitto:{{thingid}}:temperature", expire="65m"{% for m in metadata: %}, {{m}}{% endfor %}, ga="thermostatTemperatureAmbient" }
Number             {{name_parts[0]}}_Humidity    "{{room}} Humidity [%.1f%%]" <humidity> {{humidity_groups}} { channel="mqtt:topic:mosquitto:{{thingid}}:humidity" }
Number             {{name_parts[0]}}_Pressure    "{{room}} Pressure"                                       { channel="mqtt:topic:mosquitto:{{thingid}}:pressure" }
Number             {{name}}_Link          "{{label}} Link"             <network>  (gSignalStrength) { channel="mqtt:topic:mosquitto:{{thingid}}:linkquality" }
Number             {{name}}_Battery       "{{label}} Battery [%d%%]"   <battery>  (gBatteries)      { channel="mqtt:topic:mosquitto:{{thingid}}:battery" }
